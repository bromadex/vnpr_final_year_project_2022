#!/usr/bin/env python3
"""
VNPR Edge Device - Modernized Raspberry Pi Controller
Captures violations, performs OCR via Google Cloud Vision API,
and pushes data to the Django backend via REST API.

Hardware:
- Raspberry Pi 4/5
- Pi Camera Module 3 (or HQ Camera)
- 2x IR sensors for speed detection
- 1x IR sensor for red light violation
- Traffic light LEDs (Red, Yellow, Green)
- GPS Module (UART)
- 4G/LTE HAT (optional, for remote locations)

GPIO Pinout (BCM numbering):
- Traffic Light Red: GPIO 17
- Traffic Light Yellow: GPIO 27
- Traffic Light Green: GPIO 22
- Speed IR Sensor 1: GPIO 23
- Speed IR Sensor 2: GPIO 24
- Red Light IR Sensor: GPIO 25
- GPS Module: UART0 (GPIO 14/15)
"""

import os
import sys
import time
import json
import base64
import io
import threading
import requests
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Tuple

# Camera imports (use picamera2 for modern Pi)
try:
    from picamera2 import Picamera2
    from libcamera import controls
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False
    print("Warning: picamera2 not available. Using mock camera.")

# GPIO imports
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("Warning: RPi.GPIO not available. Using mock GPIO.")

# GPS imports
try:
    import serial
    GPS_AVAILABLE = True
except ImportError:
    GPS_AVAILABLE = False
    print("Warning: pyserial not available. GPS disabled.")

# Local OCR (fallback when no internet)
from vnpr.utils.ocr_service import LicensePlateOCR


# ============== CONFIGURATION ==============
@dataclass
class Config:
    """Device configuration"""
    # API Configuration
    API_BASE_URL: str = "http://your-server:8000/api"
    API_KEY: str = "your-device-api-key"

    # Speed Detection
    SENSOR_DISTANCE_M: float = 0.3  # Distance between speed sensors in meters
    SPEED_LIMIT_KMH: float = 60.0   # Speed limit in km/h

    # Camera
    CAMERA_RESOLUTION: Tuple[int, int] = (1920, 1080)
    CAMERA_FORMAT: str = "RGB888"

    # GPIO Pins (BCM)
    PIN_RED_LIGHT: int = 17
    PIN_YELLOW_LIGHT: int = 27
    PIN_GREEN_LIGHT: int = 22
    PIN_SPEED_IR_1: int = 23
    PIN_SPEED_IR_2: int = 24
    PIN_RED_IR: int = 25

    # Timing
    TRAFFIC_LIGHT_CYCLE: list = None
    CAPTURE_DELAY_MS: int = 100

    def __post_init__(self):
        if self.TRAFFIC_LIGHT_CYCLE is None:
            self.TRAFFIC_LIGHT_CYCLE = [
                ("RED", 5.0),
                ("YELLOW", 2.0),
                ("GREEN", 5.0),
            ]


CONFIG = Config()


# ============== MOCK CLASSES FOR TESTING ==============
class MockGPIO:
    """Mock GPIO for testing on non-Pi systems"""
    BCM = "BCM"
    BOARD = "BOARD"
    IN = "IN"
    OUT = "OUT"
    HIGH = 1
    LOW = 0

    _pin_states = {}

    @classmethod
    def setmode(cls, mode): pass
    @classmethod
    def setwarnings(cls, flag): pass
    @classmethod
    def setup(cls, pin, mode): cls._pin_states[pin] = 0
    @classmethod
    def output(cls, pin, state): cls._pin_states[pin] = state
    @classmethod
    def input(cls, pin): return cls._pin_states.get(pin, 0)
    @classmethod
    def cleanup(cls): cls._pin_states.clear()


class MockCamera:
    """Mock camera for testing"""
    def __init__(self):
        self.resolution = (1920, 1080)

    def start(self): pass
    def stop(self): pass
    def capture_array(self):
        import numpy as np
        return np.zeros((1080, 1920, 3), dtype=np.uint8)
    def configure(self, config): pass
    def create_preview_configuration(self, **kwargs): return None


class MockSerial:
    """Mock serial for GPS testing"""
    def __init__(self, port, baudrate): pass
    def readline(self): return b"$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47\r\n"
    def close(self): pass


# Use mocks if hardware not available
if not GPIO_AVAILABLE:
    GPIO = MockGPIO()
if not PICAMERA2_AVAILABLE:
    Picamera2 = MockCamera
if not GPS_AVAILABLE:
    serial = MockSerial


# ============== HARDWARE CONTROLLER ==============
class HardwareController:
    """Manages all hardware components"""

    def __init__(self, config: Config = CONFIG):
        self.config = config
        self.camera = None
        self.gps_serial = None
        self._running = False
        self._current_light = None

        self._init_gpio()
        self._init_camera()
        self._init_gps()

    def _init_gpio(self):
        """Initialize GPIO pins"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Traffic lights as outputs
        GPIO.setup(self.config.PIN_RED_LIGHT, GPIO.OUT)
        GPIO.setup(self.config.PIN_YELLOW_LIGHT, GPIO.OUT)
        GPIO.setup(self.config.PIN_GREEN_LIGHT, GPIO.OUT)

        # IR sensors as inputs
        GPIO.setup(self.config.PIN_SPEED_IR_1, GPIO.IN)
        GPIO.setup(self.config.PIN_SPEED_IR_2, GPIO.IN)
        GPIO.setup(self.config.PIN_RED_IR, GPIO.IN)

        # All lights off initially
        self._all_lights_off()

    def _init_camera(self):
        """Initialize camera"""
        if PICAMERA2_AVAILABLE:
            self.camera = Picamera2()
            camera_config = self.camera.create_preview_configuration(
                main={"size": self.config.CAMERA_RESOLUTION, "format": self.config.CAMERA_FORMAT}
            )
            self.camera.configure(camera_config)
            self.camera.start()
            time.sleep(2)  # Warm-up
        else:
            self.camera = MockCamera()

    def _init_gps(self):
        """Initialize GPS module"""
        if GPS_AVAILABLE:
            try:
                self.gps_serial = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
            except Exception as e:
                print(f"GPS init failed: {e}")
                self.gps_serial = None

    def _all_lights_off(self):
        """Turn all traffic lights off"""
        GPIO.output(self.config.PIN_RED_LIGHT, GPIO.LOW)
        GPIO.output(self.config.PIN_YELLOW_LIGHT, GPIO.LOW)
        GPIO.output(self.config.PIN_GREEN_LIGHT, GPIO.LOW)

    def set_traffic_light(self, color: str):
        """Set traffic light color"""
        self._all_lights_off()
        self._current_light = color.upper()

        if color.upper() == "RED":
            GPIO.output(self.config.PIN_RED_LIGHT, GPIO.HIGH)
        elif color.upper() == "YELLOW":
            GPIO.output(self.config.PIN_YELLOW_LIGHT, GPIO.HIGH)
        elif color.upper() == "GREEN":
            GPIO.output(self.config.PIN_GREEN_LIGHT, GPIO.HIGH)

    def read_speed_sensor_1(self) -> bool:
        """Read speed sensor 1 state"""
        return GPIO.input(self.config.PIN_SPEED_IR_1) == GPIO.HIGH

    def read_speed_sensor_2(self) -> bool:
        """Read speed sensor 2 state"""
        return GPIO.input(self.config.PIN_SPEED_IR_2) == GPIO.HIGH

    def read_red_light_sensor(self) -> bool:
        """Read red light violation sensor"""
        return GPIO.input(self.config.PIN_RED_IR) == GPIO.HIGH

    def capture_image(self) -> bytes:
        """Capture image and return as bytes"""
        if PICAMERA2_AVAILABLE:
            image_array = self.camera.capture_array()
            # Convert to JPEG bytes
            from PIL import Image
            img = Image.fromarray(image_array)
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            return buffer.getvalue()
        else:
            # Return a test image
            with open("test_image.jpg", "rb") as f:
                return f.read()

    def get_gps_coordinates(self) -> Tuple[Optional[float], Optional[float]]:
        """Get current GPS coordinates"""
        if not self.gps_serial:
            return None, None

        try:
            line = self.gps_serial.readline().decode('utf-8').strip()
            if line.startswith('$GPGGA'):
                parts = line.split(',')
                if len(parts) >= 6 and parts[2] and parts[4]:
                    lat = self._parse_gps(parts[2], parts[3])
                    lon = self._parse_gps(parts[4], parts[5])
                    return lat, lon
        except Exception as e:
            print(f"GPS read error: {e}")

        return None, None

    def _parse_gps(self, coord: str, direction: str) -> float:
        """Parse GPS coordinate"""
        degrees = float(coord[:2]) if direction in ['N', 'S'] else float(coord[:3])
        minutes = float(coord[2:] if direction in ['N', 'S'] else coord[3:])
        decimal = degrees + minutes / 60.0
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal

    def cleanup(self):
        """Cleanup hardware resources"""
        self._running = False
        self._all_lights_off()
        if self.camera and PICAMERA2_AVAILABLE:
            self.camera.stop()
        if self.gps_serial:
            self.gps_serial.close()
        GPIO.cleanup()


# ============== VIOLATION DETECTOR ==============
class ViolationDetector:
    """Detects traffic violations and triggers capture"""

    def __init__(self, hardware: HardwareController, config: Config = CONFIG):
        self.hardware = hardware
        self.config = config
        self.ocr = LicensePlateOCR()
        self._running = False

        # Speed detection state
        self._speed_start_time = None
        self._speed_in_progress = False

    def start(self):
        """Start violation detection loops"""
        self._running = True

        # Start traffic light cycle in background
        traffic_thread = threading.Thread(target=self._traffic_light_cycle, daemon=True)
        traffic_thread.start()

        # Start speed detection
        speed_thread = threading.Thread(target=self._speed_detection_loop, daemon=True)
        speed_thread.start()

        # Start red light detection
        red_light_thread = threading.Thread(target=self._red_light_detection_loop, daemon=True)
        red_light_thread.start()

        print("Violation detector started. Monitoring traffic...")

        # Keep main thread alive
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop violation detection"""
        self._running = False
        print("Violation detector stopped.")

    def _traffic_light_cycle(self):
        """Run traffic light cycle continuously"""
        while self._running:
            for color, duration in self.config.TRAFFIC_LIGHT_CYCLE:
                if not self._running:
                    break
                self.hardware.set_traffic_light(color)
                time.sleep(duration)

    def _speed_detection_loop(self):
        """Monitor speed sensors and detect speeding"""
        while self._running:
            # Wait for sensor 1 trigger
            if self.hardware.read_speed_sensor_1() and not self._speed_in_progress:
                self._speed_start_time = time.time()
                self._speed_in_progress = True
                print(f"Speed detection started at {self._speed_start_time}")

            # Check sensor 2
            if self._speed_in_progress and self.hardware.read_speed_sensor_2():
                end_time = time.time()
                elapsed = end_time - self._speed_start_time

                if elapsed > 0:
                    speed_ms = self.config.SENSOR_DISTANCE_M / elapsed
                    speed_kmh = speed_ms * 3.6

                    print(f"Vehicle speed: {speed_kmh:.2f} km/h")

                    if speed_kmh > self.config.SPEED_LIMIT_KMH:
                        print(f"SPEEDING VIOLATION DETECTED: {speed_kmh:.2f} km/h")
                        self._handle_violation("OVER_SPEEDING", speed_kmh)

                self._speed_in_progress = False
                self._speed_start_time = None

            time.sleep(0.01)  # 10ms polling

    def _red_light_detection_loop(self):
        """Monitor red light violations"""
        while self._running:
            # Only check if light is RED
            if self.hardware._current_light == "RED":
                if self.hardware.read_red_light_sensor():
                    print("RED LIGHT VIOLATION DETECTED!")
                    self._handle_violation("RED_ROBOT")
                    time.sleep(2)  # Debounce

            time.sleep(0.05)  # 50ms polling

    def _handle_violation(self, violation_type: str, speed: Optional[float] = None):
        """Handle a detected violation"""
        try:
            # Capture image
            print("Capturing image...")
            image_bytes = self.hardware.capture_image()

            # Get GPS coordinates
            lat, lon = self.hardware.get_gps_coordinates()

            # Perform OCR
            print("Performing OCR...")
            ocr_result = self.ocr.recognize_plate(image_bytes=image_bytes)

            if ocr_result['success'] and ocr_result['plate_number']:
                print(f"Plate recognized: {ocr_result['plate_number']} "
                      f"(confidence: {ocr_result['confidence']})")
            else:
                print(f"OCR failed or no plate found: {ocr_result.get('error', 'Unknown')}")

            # Upload to server
            self._upload_violation(
                plate_number=ocr_result.get('plate_number'),
                violation_type=violation_type,
                image_bytes=image_bytes,
                speed=speed,
                latitude=lat,
                longitude=lon,
                raw_text=ocr_result.get('raw_text', '')
            )

        except Exception as e:
            print(f"Error handling violation: {e}")

    def _upload_violation(self, plate_number: Optional[str], violation_type: str,
                         image_bytes: bytes, speed: Optional[float] = None,
                         latitude: Optional[float] = None, longitude: Optional[float] = None,
                         raw_text: str = ""):
        """Upload violation data to the server"""
        try:
            # Encode image as base64
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')

            # Prepare payload
            payload = {
                "number_plate": plate_number or "UNKNOWN",
                "description": f"Traffic violation detected. Raw OCR: {raw_text}",
                "event_type": violation_type,
                "speed": speed,
                "latitude": latitude,
                "longitude": longitude,
                "location": f"{latitude},{longitude}" if latitude and longitude else None,
                "is_from_device": True,
                "image_b64": image_b64,
            }

            # Send to API
            headers = {
                "Content-Type": "application/json",
                "X-Device-API-Key": self.config.API_KEY,
            }

            response = requests.post(
                f"{self.config.API_BASE_URL}/events/device/",
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 201:
                print(f"Violation uploaded successfully: {response.json()}")
            else:
                print(f"Upload failed: {response.status_code} - {response.text}")

                # Save locally for retry
                self._save_local_backup(payload)

        except Exception as e:
            print(f"Upload error: {e}")
            self._save_local_backup(payload)

    def _save_local_backup(self, payload: dict):
        """Save violation data locally for retry"""
        backup_dir = "violation_backups"
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{backup_dir}/violation_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(payload, f, indent=2)

        print(f"Violation saved locally: {filename}")


# ============== MAIN ENTRY POINT ==============
def main():
    """Main entry point for the edge device"""
    print("=" * 60)
    print("  VNPR Edge Device - IoT Traffic Violation System")
    print("  Modernized Version 2024")
    print("=" * 60)

    config = Config()

    # Override from environment variables
    config.API_BASE_URL = os.environ.get('API_BASE_URL', config.API_BASE_URL)
    config.API_KEY = os.environ.get('DEVICE_API_KEY', config.API_KEY)
    config.SPEED_LIMIT_KMH = float(os.environ.get('SPEED_LIMIT', config.SPEED_LIMIT_KMH))

    hardware = HardwareController(config)
    detector = ViolationDetector(hardware, config)

    try:
        detector.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        detector.stop()
        hardware.cleanup()
        print("Device shutdown complete.")


if __name__ == "__main__":
    main()
