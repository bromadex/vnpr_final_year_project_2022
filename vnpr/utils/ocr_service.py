"""
Google Cloud Vision OCR Service for License Plate Recognition
"""
import os
import re
import io
import base64
from typing import Optional, Tuple
from google.cloud import vision
from google.oauth2 import service_account


class LicensePlateOCR:
    """
    Service class for detecting and reading license plates from images
    using Google Cloud Vision API.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OCR service.

        Args:
            api_key: Google Cloud Vision API key. If not provided, 
                    looks for GOOGLE_CLOUD_VISION_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get('GOOGLE_CLOUD_VISION_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Google Cloud Vision API key is required. "
                "Set GOOGLE_CLOUD_VISION_API_KEY environment variable."
            )

        # Initialize the client
        # For API key authentication, we use the client with explicit credentials
        # In production, use service account JSON file instead
        self.client = vision.ImageAnnotatorClient(
            client_options={"api_key": self.api_key}
        )

    def detect_text(self, image_path: Optional[str] = None, 
                   image_bytes: Optional[bytes] = None,
                   image_b64: Optional[str] = None) -> dict:
        """
        Detect text in an image.

        Args:
            image_path: Path to the image file
            image_bytes: Raw image bytes
            image_b64: Base64 encoded image string

        Returns:
            Dictionary with detected text and annotations
        """
        image = vision.Image()

        if image_path:
            with io.open(image_path, 'rb') as image_file:
                image.content = image_file.read()
        elif image_bytes:
            image.content = image_bytes
        elif image_b64:
            image.content = base64.b64decode(image_b64)
        else:
            raise ValueError("Must provide one of: image_path, image_bytes, or image_b64")

        # Perform text detection
        response = self.client.text_detection(image=image)
        texts = response.text_annotations

        if response.error.message:
            raise Exception(f"API Error: {response.error.message}")

        return {
            'full_text': texts[0].description if texts else '',
            'annotations': [
                {
                    'text': text.description,
                    'confidence': text.confidence if hasattr(text, 'confidence') else None,
                    'bounding_poly': [
                        {'x': vertex.x, 'y': vertex.y} 
                        for vertex in text.bounding_poly.vertices
                    ]
                }
                for text in texts
            ]
        }

    def extract_plate_number(self, text: str, country_code: str = 'ZW') -> Optional[str]:
        """
        Extract license plate number from detected text.

        Supports multiple formats:
        - Zimbabwe: ABC1234, AB 1234, etc.
        - Generic: Any alphanumeric pattern that looks like a plate

        Args:
            text: Raw detected text
            country_code: Country code for plate format (default: ZW for Zimbabwe)

        Returns:
            Cleaned plate number or None if not found
        """
        # Remove whitespace and normalize
        text = text.upper().replace(' ', '').replace('-', '').replace('_', '')

        # Zimbabwe plate patterns: 2-3 letters followed by 1-4 numbers
        # Examples: ABC1234, AB1234, A1234
        patterns = {
            'ZW': [
                r'[A-Z]{2,3}[0-9]{1,4}',      # Standard: ABC1234
                r'[A-Z]{1,3}[0-9]{2,4}',      # Short: AB12, A123
            ],
            'GENERIC': [
                r'[A-Z0-9]{4,8}',              # Generic alphanumeric
            ]
        }

        country_patterns = patterns.get(country_code, patterns['GENERIC'])

        for pattern in country_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Return the longest match (most likely to be the full plate)
                best_match = max(matches, key=len)
                # Validate: should be 4-8 characters
                if 4 <= len(best_match) <= 8:
                    return best_match

        return None

    def recognize_plate(self, image_path: Optional[str] = None,
                       image_bytes: Optional[bytes] = None,
                       image_b64: Optional[str] = None,
                       country_code: str = 'ZW') -> dict:
        """
        Full pipeline: detect text and extract plate number.

        Args:
            image_path: Path to image file
            image_bytes: Raw image bytes  
            image_b64: Base64 encoded image
            country_code: Country for plate format

        Returns:
            Dictionary with plate_number, confidence, and raw_text
        """
        try:
            result = self.detect_text(image_path, image_bytes, image_b64)
            raw_text = result['full_text']

            plate_number = self.extract_plate_number(raw_text, country_code)

            # Calculate confidence based on text clarity
            confidence = 0.0
            if result['annotations'] and len(result['annotations']) > 1:
                # Skip the first annotation (full text), use individual words
                individual_annotations = result['annotations'][1:]
                confidences = [
                    a.get('confidence', 0.8) or 0.8 
                    for a in individual_annotations
                ]
                confidence = sum(confidences) / len(confidences) if confidences else 0.8
            else:
                confidence = 0.8  # Default confidence

            return {
                'success': True,
                'plate_number': plate_number,
                'confidence': round(confidence, 2),
                'raw_text': raw_text.strip(),
                'country_code': country_code,
                'error': None
            }

        except Exception as e:
            return {
                'success': False,
                'plate_number': None,
                'confidence': 0.0,
                'raw_text': '',
                'country_code': country_code,
                'error': str(e)
            }


# Singleton instance for reuse
_ocr_instance = None

def get_ocr_service() -> LicensePlateOCR:
    """Get or create the OCR service instance."""
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = LicensePlateOCR()
    return _ocr_instance
