import requests
import json
import time
from datetime import datetime
import random

# Configuración
API_BASE = "http://localhost:8000/v1"
DEVICE_ID = "IMEI_123456789"  # Asegúrate de que este IMEI existe en tu DB
DEVICE_KEY = "ares_secret_key_123"  # La clave que rotamos antes
HEADERS = {
    "X-Device-Key": DEVICE_KEY,
    "Content-Type": "application/json"
}


def send_iot_batch(lat, lon, accuracy=2.5, activity=100):
    """
    Simula el envío de un paquete IoT profesional v2.0
    """
    payload = {
        "device_id": DEVICE_ID,
        "packets": [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "gps": {
                    "lat": lat,
                    "lon": lon,
                    "accuracy": accuracy,
                    "satellites": 8
                },
                "telemetry": {
                    "battery_mv": 3850,
                    "temperature": 25.4,
                    "activity_score": activity
                },
                "status": "MOVING"
            }
        ]
    }

    try:
        response = requests.post(
            f"{API_BASE}/iot/ingest", json=payload, headers=HEADERS)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Status: {response.status_code} | Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print(f"🚀 Iniciando Simulador ARES v2.0 (IoT Direct-to-Cloud)")
    print(f"📡 Target: {API_BASE}/iot/ingest")
    print(f"🆔 Device: {DEVICE_ID}\n")

    # Simular una ruta pequeña
    base_lat = 40.4168
    base_lon = -3.7038

    for i in range(5):
        # Mover un poco cada vez
        lat = base_lat + (i * 0.0001)
        lon = base_lon + (i * 0.0001)
        accuracy = random.uniform(1.5, 5.0)
        activity = random.randint(50, 200)

        send_iot_batch(lat, lon, accuracy, activity)
        time.sleep(2)
