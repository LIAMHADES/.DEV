# ARES GPS Backend

Backend API for the ARES Dog GPS Tracking and Health Application. This project follows an **IoT Direct-to-Cloud** architecture, where tracker devices communicate directly with the API.

## Stack

- **API**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **Infrastructure**: Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Run the Backend

```bash
cd GPS

# Build and start services
docker-compose up -d --build

# Check logs
docker-compose logs -f api
```

### Access

- **API Docs (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

The API is divided into several logical groups:

### IoT

This is the core endpoint for data ingestion from the hardware devices.

- `POST /v1/iot/ingest` - Receive telemetry data (single or batch) from tracker devices.

### Auth

- `POST /v1/auth/register` - Register new user
- `POST /v1/auth/login` - Login and get token

### Dogs

- `POST /v1/dogs` - Create dog profile
- `GET /v1/dogs/{id}` - Get dog details
- `PATCH /v1/dogs/{id}` - Update dog profile
- `GET /v1/dogs/{id}/last-location` - Get last known location
- `GET /v1/dogs/{id}/locations` - Get location history
- `POST /v1/dogs/{id}/geofence` - Create geofence
- `GET /v1/dogs/{id}/alerts` - Get alerts

### Devices

- `POST /v1/devices` - Register tracker device
- `GET /v1/devices/{id}/status` - Get device status
- `POST /v1/devices/{id}/lost-mode` - Activate or deactivate lost mode.

## Environment Variables

| Variable                 | Default          | Description                        |
| ------------------------ | ---------------- | ---------------------------------- |
| DATABASE_URL             | postgresql://... | Database connection string         |
| SECRET_KEY               | change-me        | JWT secret key                     |
| WATCHDOG_WALKING_MINUTES | 5                | Alert if no signal in walking mode |
| WATCHDOG_REST_MINUTES    | 60               | Alert if no signal in rest mode    |
| GEOFENCE_TOLERANCE_M     | 5.0              | Geofence tolerance in meters       |