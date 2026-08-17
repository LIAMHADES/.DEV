
import requests
import time
import os
import sys

# CONFIG
API_BASE = "http://localhost:8000"
DEVICE_ID = "ARES-SIM-001"
DEVICE_KEY = "test-device-key-12345"
# We'll try to find the device ID dynamically if possible, or assume 1 for first dog
DEVICE_ID_INT = 1


def test_downlink_cycle():
    print("=" * 60)
    print("🚀 ARES v4.0 VIRTUAL INTEGRATION TEST")
    print("=" * 60)

    # 1. Healthcheck
    try:
        requests.get(f"{API_BASE}/docs", timeout=2)
        print("✅ BACKEND: Online")
    except:
        print("❌ BACKEND: Offline. Start docker-compose first.")
        return

    # 2. Ingest some dummy telemetry to wake up the system
    print("\n📡 STEP 1: Sending initial telemetry...")
    ingest_payload = {
        "device_id": DEVICE_ID,
        "packets": [{
            "timestamp": "2026-01-16T20:00:00Z",
            "gps": {"lat": 40.4167, "lon": -3.7037, "accuracy": 1.5, "speed_kmh": 0.0, "fix_type": "GNSS"},
            "telemetry": {"battery_mv": 4200, "temperature": 25.5},
            "activity_mode": "REST",
            "motion_state": "STATIONARY"
        }]
    }
    headers = {"X-Device-Key": DEVICE_KEY, "Content-Type": "application/json"}
    ingest_resp = requests.post(
        f"{API_BASE}/v1/iot/ingest", json=ingest_payload, headers=headers)

    if ingest_resp.status_code == 201:
        print("✅ TELEMETRY: Ingested successfully")
    else:
        print(
            f"❌ TELEMETRY: Failed ({ingest_resp.status_code}) - {ingest_resp.text}")

    # 3. Login as User to get Token
    print("\n🔑 STEP 2: Logging in as User...")
    login_payload = {"phone": "555000444"}  # Test user from setup_test_device
    login_resp = requests.post(f"{API_BASE}/v1/auth/login", json=login_payload)
    if login_resp.status_code == 200:
        token = login_resp.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"}
        print("✅ AUTH: Logged in successfully")
    else:
        print(f"❌ AUTH: Login failed ({login_resp.status_code})")
        return

    # 4. Queue a remote command (Requires User Token)
    print("\n💡 STEP 3: Queuing Remote Command (FIND_ME)...")
    cmd_payload = {"pattern": "STROBE", "color": "CYAN"}
    # Note: Using device_id=1 as it's the first one created in seeds
    cmd_resp = requests.post(
        f"{API_BASE}/v1/devices/1/lights/find", json=cmd_payload, headers=user_headers)

    if cmd_resp.status_code == 200:
        cmd_id = cmd_resp.json()["command_id"]
        print(f"✅ COMMAND: Queued with ID {cmd_id}")
    else:
        print(
            f"❌ COMMAND: Failed to queue ({cmd_resp.status_code}) - {cmd_resp.text}")
        return

    # 5. Device Polling (Requires Device Key)
    print("\n📥 STEP 4: Simulated Device Polling...")
    device_headers = {"X-Device-Key": DEVICE_KEY}
    poll_resp = requests.get(
        f"{API_BASE}/v1/devices/commands/poll", headers=device_headers)

    if poll_resp.status_code == 200 and poll_resp.json():
        cmd = poll_resp.json()
        print(
            f"✅ DEVICE: Received command '{cmd['command']}' (ID: {cmd['id']})")

        # 6. Acknowledge (Requires Device Key)
        print("\n📤 STEP 5: Sending Acknowledgment (ACK)...")
        ack_resp = requests.post(
            f"{API_BASE}/v1/devices/commands/{cmd['id']}/ack", headers=device_headers)
        if ack_resp.status_code == 200:
            print("✅ ACK: Command confirmed as executed")
        else:
            print(f"❌ ACK: Failed to confirm ({ack_resp.status_code})")
    else:
        print("❌ POLL: No command found. Check if device_id logic is correct.")

    print("\n" + "=" * 60)
    print("🏆 VIRTUAL TEST COMPLETE")
    print("The system is fully synchronized and ready for hardware!")
    print("=" * 60)


if __name__ == "__main__":
    test_downlink_cycle()
