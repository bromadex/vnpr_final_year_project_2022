# VNPR - Vehicle Number Plate Recognition System

> **Modernized Version 2.0** — IoT Traffic Violation Detection with AI-Powered OCR

A complete traffic enforcement system that detects speeding vehicles and red light violations using Raspberry Pi edge devices, performs license plate recognition via Google Cloud Vision API, and delivers real-time alerts to law enforcement officers through a modern React dashboard.

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Raspberry Pi   │────▶│  Django Backend  │◀────│  React Frontend │
│  Edge Device    │     │  (REST + WS)     │     │  Dashboard      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                        │
         ▼                       ▼                        ▼
  ┌─────────────┐        ┌──────────────┐         ┌─────────────┐
  │ IR Sensors  │        │  PostgreSQL  │         │  WebSocket  │
  │ Pi Camera   │        │  Redis       │         │  Real-time  │
  │ GPS Module  │        │  Google OCR  │         │  Updates    │
  └─────────────┘        └──────────────┘         └─────────────┘
```

---

## 🚀 Quick Start (Docker)

### Prerequisites
- Docker & Docker Compose
- Google Cloud Vision API key
- (Optional) Raspberry Pi 4/5 with camera module

### 1. Clone & Configure

```bash
git clone <repo-url>
cd vnpr_project

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 2. Start Services

```bash
docker-compose up --build
```

### 3. Create Superuser

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 4. Access the Application

| Service | URL |
|---------|-----|
| Frontend Dashboard | http://localhost |
| Backend API | http://localhost:8000/api/ |
| Admin Panel | http://localhost:8000/admin/ |
| Django API Docs | http://localhost:8000/api/ |

---

## 📁 Project Structure

```
vnpr_project/
├── vnpr/                          # Django project config
│   ├── settings.py                # Settings (PostgreSQL, Redis, Channels)
│   ├── urls.py                    # URL routing
│   ├── routing.py                 # ASGI + WebSocket routing
│   └── utils/
│       └── ocr_service.py         # Google Cloud Vision integration
│
├── accounts/                      # Authentication app
│   ├── models.py                  # Custom User model
│   ├── views.py                   # Login/Signup views
│   └── urls.py
│
├── vehicles/                      # Vehicle registry
│   ├── models.py                  # Vehicle, VehicleImage
│   ├── serializers.py             # DRF serializers
│   ├── views.py                   # CRUD API views
│   └── urls.py
│
├── events/                        # Violation incidents
│   ├── models.py                  # Event, EventImage
│   ├── serializers.py
│   ├── views.py                   # Device endpoint + WebSocket
│   ├── consumers.py               # WebSocket consumer
│   └── routing.py                 # WS URL patterns
│
├── frontend/                      # React SPA
│   ├── src/
│   │   ├── components/            # Layout, ProtectedRoute
│   │   ├── pages/                 # Dashboard, Incidents, Vehicles, etc.
│   │   ├── context/               # AuthContext, WebSocketContext
│   │   └── styles/                # Tailwind CSS
│   ├── package.json
│   └── Dockerfile
│
├── raspberry_pi/                  # Edge device code
│   ├── main.py                    # Main control loop
│   ├── install.sh                 # Pi setup script
│   └── .env.example               # Device config template
│
├── docker-compose.yml             # Full stack orchestration
├── Dockerfile                     # Backend image
├── nginx.conf                     # Reverse proxy config
├── requirements.txt               # Python dependencies
└── .env.example                   # Environment template
```

---

## 🔧 Configuration

### Environment Variables (`.env`)

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DB_NAME=vnpr_db
DB_USER=vnpr_user
DB_PASSWORD=vnpr_password
DB_HOST=db
DB_PORT=5432

# Google Cloud Vision
GOOGLE_CLOUD_VISION_API_KEY=your-api-key

# Redis
REDIS_URL=redis://redis:6379/0
```

### Raspberry Pi Device Config

```env
API_BASE_URL=http://your-server-ip:8000/api
DEVICE_API_KEY=your-device-api-key
SPEED_LIMIT=60
GOOGLE_CLOUD_VISION_API_KEY=your-api-key
```

---

## 🔌 Hardware Setup (Raspberry Pi)

### Components
- **Raspberry Pi 4/5** (4GB+ RAM recommended)
- **Pi Camera Module 3** or HQ Camera
- **2x IR Sensors** (for speed detection)
- **1x IR Sensor** (for red light violation)
- **3x LEDs** (Red, Yellow, Green traffic light simulation)
- **GPS Module** (UART interface)
- **Breadboard & jumper wires**

### GPIO Pinout (BCM)

| Component | GPIO Pin |
|-----------|----------|
| Red Light LED | GPIO 17 |
| Yellow Light LED | GPIO 27 |
| Green Light LED | GPIO 22 |
| Speed Sensor 1 | GPIO 23 |
| Speed Sensor 2 | GPIO 24 |
| Red Light Sensor | GPIO 25 |
| GPS Module | UART0 (GPIO 14/15) |

### Installation on Pi

```bash
# Run the install script
chmod +x raspberry_pi/install.sh
cd raspberry_pi
./install.sh

# Configure environment
cp .env.example .env
nano .env  # Add your API credentials

# Run the edge device
python main.py
```

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/accounts/login/` | Login |
| POST | `/api/accounts/signup/` | Register |
| POST | `/api/accounts/logout/` | Logout |

### Vehicles
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vehicles/` | List all vehicles |
| GET | `/api/vehicles/search/?q=ABC` | Search vehicles |
| POST | `/api/vehicles/new/` | Add vehicle |
| GET | `/api/vehicles/<id>/` | Vehicle detail |
| PUT | `/api/vehicles/<id>/edit/` | Update vehicle |
| DELETE | `/api/vehicles/<id>/delete/` | Delete vehicle |

### Events (Incidents)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/events/list/` | List incidents |
| POST | `/api/events/new/` | Add manual incident |
| POST | `/api/events/device/` | Device push endpoint |
| GET | `/api/events/<id>/` | Incident detail |
| POST | `/api/events/<id>/resolve/` | Mark resolved |

### WebSocket
| URL | Description |
|-----|-------------|
| `ws://host/ws/incidents/` | Real-time incident stream |

---

## 🧠 How It Works

### 1. Speed Detection
```
IR Sensor 1 ──► Vehicle passes ──► Start timer
                                    │
IR Sensor 2 ──► Vehicle passes ──► Stop timer
                                    │
                    Speed = Distance / Time
                    If Speed > Limit → Capture + OCR
```

### 2. Red Light Violation
```
Traffic Light = RED
      │
IR Sensor detects vehicle
      │
► VIOLATION → Capture + OCR
```

### 3. OCR Pipeline
```
Captured Image
      │
Google Cloud Vision API
      │
Text Detection + Plate Extraction
      │
Match with Vehicle Database
      │
Push to Backend via REST API
      │
Broadcast via WebSocket → Dashboard
```

---

## 🎨 Dashboard Features

- **Real-time Updates**: WebSocket-powered live incident feed
- **Interactive Maps**: Leaflet.js with violation markers
- **Vehicle Registry**: Full CRUD with image uploads
- **Search**: Plate number, owner, or vehicle name
- **Filtering**: By type (speeding/red light), resolved status
- **Responsive Design**: Mobile-friendly for officers in the field

---

## 🔐 Security

- Django's built-in authentication with custom User model
- CORS configured for frontend origin
- API key authentication for device endpoints
- CSRF protection on web routes
- Environment variable management for secrets

---

## 🛠️ Development

### Backend Only
```bash
cd vnpr_project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Only
```bash
cd frontend
npm install
npm start  # Runs on localhost:3000
```

### Run Tests
```bash
# Backend
docker-compose exec backend python manage.py test

# Frontend
cd frontend && npm test
```

---

## 📊 Comparison: Original vs Modernized

| Feature | Original (2022) | Modernized (2024) |
|---------|----------------|-------------------|
| OCR | Custom KNN + OpenCV | Google Cloud Vision API |
| Accuracy | ~85% | 95%+ |
| Backend | Django templates | Django REST Framework |
| Frontend | Server-rendered HTML | React SPA |
| Real-time | Page refresh | WebSocket |
| Database | Firebase | PostgreSQL + Redis |
| Maps | Basic Leaflet | Interactive with filters |
| Camera | PiCamera v1 | PiCamera2 (modern) |
| Deployment | Manual | Docker Compose |
| Edge Code | Single-threaded | Multi-threaded |

---

## 📝 License

This project was originally developed by **Clement Mpala** as a final year project at NUST (National University of Science and Technology), Zimbabwe.

Modernized version maintained with ❤️.

---

## 🙏 Acknowledgements

- Original project supervisor: Eng. M. Nleya
- NUST Department of Electronic Engineering
- Google Cloud Vision API
- Django & React communities
