"""
=============================================================================
ARES v4.0 Device Simulator
Simulates the full device logic: Modes, Store & Forward, Anti-Fraud, Lights.
Sends real packets to your backend for e2e testing.
=============================================================================
"""
import time
import random
import requests
import hashlib
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
from enum import Enum

# =============================================================================
# CONFIGURATION
# =============================================================================
API_BASE_URL = "http://localhost:8000"
INGEST_ENDPOINT = f"{API_BASE_URL}/v1/iot/ingest"
DEVICE_ID = "ARES-SIM-001"
DEVICE_KEY = "test-device-key-12345"
POLL_COMMANDS_ENDPOINT = f"{API_BASE_URL}/v1/devices/commands/poll"
ACK_COMMAND_ENDPOINT = f"{API_BASE_URL}/v1/devices/commands/{{}}/ack"

# Intervals (seconds)
GPS_INTERVAL_LIVE = 5
GPS_INTERVAL_ADAPTIVE = 15
GPS_INTERVAL_SAVER = 60

# Thresholds
VEHICLE_SPEED_THRESHOLD = 25.0  # km/h
STATIONARY_TIMEOUT = 120  # seconds

# =============================================================================
# ENUMS & DATA CLASSES
# =============================================================================


class DeviceMode(Enum):
    DEEP_SLEEP = "DEEP_SLEEP"
    SAVER = "SAVER"
    ADAPTIVE = "ADAPTIVE"
    LIVE = "LIVE"


class ActivityMode(Enum):
    REST = "REST"
    WALK = "WALK"
    JOG = "JOG"
    RUN = "RUN"
    VEHICLE = "VEHICLE"


@dataclass
class GpsReading:
    lat: float
    lon: float
    altitude: float
    speed_kmh: float
    heading_deg: float
    accuracy: float
    satellites: int
    fix_type: str = "GNSS"


@dataclass
class TelemetryPacket:
    seq_id: int
    timestamp: str
    gps: dict
    telemetry: dict
    activity_mode: str
    motion_state: str
    steps_count: int = 0
    cadence: int = 0
    gnss_confidence: int = 100
    lte_rssi: Optional[int] = None
    is_predicted: bool = False

# =============================================================================
# STORE & FORWARD BUFFER
# =============================================================================


class OfflineBuffer:
    def __init__(self, max_size: int = 10000):
        self.buffer: List[TelemetryPacket] = []
        self.max_size = max_size
        self.next_seq_id = 1

    def add(self, packet: TelemetryPacket):
        if len(self.buffer) >= self.max_size:
            self.buffer.pop(0)  # Remove oldest (circular)
            print(f"  [BUFFER] Overflow! Oldest packet discarded.")
        self.buffer.append(packet)
        print(
            f"  [BUFFER] Stored packet seq_id={packet.seq_id}. Buffer size: {len(self.buffer)}")

    def get_batch(self, batch_size: int = 50) -> List[TelemetryPacket]:
        return self.buffer[:batch_size]

    def ack_up_to(self, last_seq_id: int):
        before = len(self.buffer)
        self.buffer = [p for p in self.buffer if p.seq_id > last_seq_id]
        removed = before - len(self.buffer)
        print(
            f"  [BUFFER] ACK received for seq_id<={last_seq_id}. Removed {removed} packets.")

    def get_next_seq_id(self) -> int:
        seq = self.next_seq_id
        self.next_seq_id += 1
        return seq

    def is_empty(self) -> bool:
        return len(self.buffer) == 0

# =============================================================================
# DEVICE SIMULATOR
# =============================================================================


class AresDeviceSimulator:
    def __init__(self):
        self.mode = DeviceMode.ADAPTIVE
        self.buffer = OfflineBuffer()
        self.network_connected = True
        self.battery_pct = 100
        self.step_count = 0
        self.last_motion_time = time.time()

        # Simulated position (Madrid)
        self.lat = 40.416775
        self.lon = -3.703790
        self.altitude = 650.0

    def simulate_motion(self) -> tuple:
        """Simulate IMU motion state and activity."""
        is_moving = random.random() > 0.3  # 70% chance of moving

        if is_moving:
            self.last_motion_time = time.time()
            accel = random.randint(30, 150)

            if accel > 120:
                activity = ActivityMode.RUN
                speed = random.uniform(10, 18)
            elif accel > 80:
                activity = ActivityMode.JOG
                speed = random.uniform(6, 10)
            else:
                activity = ActivityMode.WALK
                speed = random.uniform(2, 6)

            self.step_count += random.randint(5, 20)
            return ("MOVING", activity, speed)
        else:
            if time.time() - self.last_motion_time > STATIONARY_TIMEOUT:
                return ("STATIONARY", ActivityMode.REST, 0.0)
            else:
                return ("MOVING", ActivityMode.WALK, random.uniform(0, 2))

    def update_mode(self, motion_state: str, speed: float):
        """State machine for device mode."""
        if motion_state == "STATIONARY":
            self.mode = DeviceMode.DEEP_SLEEP
        elif speed > 12:
            self.mode = DeviceMode.LIVE
        elif speed > 5:
            self.mode = DeviceMode.ADAPTIVE
        else:
            self.mode = DeviceMode.SAVER

        print(f"  [MODE] Current mode: {self.mode.value}")

    def get_gps_reading(self, speed: float) -> GpsReading:
        """Simulate GPS reading."""
        # Move position slightly
        self.lat += random.uniform(-0.0001, 0.0001)
        self.lon += random.uniform(-0.0001, 0.0001)
        self.altitude += random.uniform(-1, 1)

        return GpsReading(
            lat=round(self.lat, 6),
            lon=round(self.lon, 6),
            altitude=round(self.altitude, 1),
            speed_kmh=round(speed, 1),
            heading_deg=random.randint(0, 360),
            accuracy=round(random.uniform(1.0, 3.0), 1),
            satellites=random.randint(8, 14)
        )

    def anti_fraud_check(self, gps_speed: float, motion_state: str, activity: ActivityMode) -> ActivityMode:
        """Check for vehicle transport (fraud)."""
        if gps_speed > VEHICLE_SPEED_THRESHOLD and motion_state == "STATIONARY":
            print(
                f"  [ANTI-FRAUD] Detected VEHICLE! GPS speed={gps_speed} but IMU=STATIONARY")
            return ActivityMode.VEHICLE
        return activity

    def create_packet(self, gps: GpsReading, activity: ActivityMode, motion_state: str) -> TelemetryPacket:
        """Create telemetry packet."""
        return TelemetryPacket(
            seq_id=self.buffer.get_next_seq_id(),
            timestamp=datetime.utcnow().isoformat() + "Z",
            gps={
                "lat": gps.lat,
                "lon": gps.lon,
                "altitude": gps.altitude,
                "speed_kmh": gps.speed_kmh,
                "heading_deg": gps.heading_deg,
                "accuracy": gps.accuracy,
                "satellites": gps.satellites,
                "fix_type": gps.fix_type
            },
            telemetry={
                "battery_mv": int(3000 + (self.battery_pct / 100) * 1200),
                "battery_capacity_mah": 2750,
                "temperature": round(random.uniform(20, 35), 1),
                "activity_score": random.randint(0, 100)
            },
            activity_mode=activity.value,
            motion_state=motion_state,
            steps_count=random.randint(
                5, 50) if motion_state == "MOVING" else 0,
            cadence=random.randint(40, 160) if motion_state == "MOVING" else 0,
            gnss_confidence=random.randint(
                80, 100) if gps.satellites > 6 else 40,
            lte_rssi=random.randint(-110, -50)
        )

    def poll_commands(self):
        """Poll for pending commands from backend."""
        if not self.network_connected:
            return

        headers = {
            "X-Device-Key": DEVICE_KEY
        }

        try:
            resp = requests.get(POLL_COMMANDS_ENDPOINT,
                                headers=headers, timeout=5)
            if resp.status_code == 200:
                cmd_data = resp.json()
                if cmd_data:
                    self.execute_command(cmd_data)
            elif resp.status_code != 200 and resp.status_code != 404:
                # print(f"  [CMD] Poll failed: {resp.status_code}")
                pass
        except Exception as e:
            print(f"  [CMD] Error polling commands: {e}")

    def execute_command(self, cmd: dict):
        """Simulate command execution on the hardware."""
        cmd_id = cmd.get("id")
        cmd_name = cmd.get("command")
        payload = cmd.get("payload", {})

        print(f"\n  [CMD] >>> EXECUTING: {cmd_name} (ID: {cmd_id})")

        if cmd_name == "SET_LOST_MODE":
            enabled = payload.get("enabled", False)
            print(
                f"  [HW] LOST_MODE is now: {'ENABLED' if enabled else 'DISABLED'}")
            if enabled:
                print("  [HW] Reducing GPS interval to 2s, LTE always ON.")
                self.mode = DeviceMode.LIVE

        elif cmd_name == "FIND_ME":
            pattern = payload.get("pattern", "STOBE")
            color = payload.get("color", "CYAN")
            print(
                f"  [HW] LED PATTERN: {pattern} | COLOR: {color} | VISIBILITY: MAX")

        elif cmd_name == "SET_GEOFENCE":
            gf_id = payload.get("id")
            radius = payload.get("radius")
            print(f"  [HW] LOCAL GEOFENCE SYNCED: {gf_id} | Radius: {radius}m")

        elif cmd_name == "SET_RATE_PROFILE":
            profile = payload.get("profile")
            print(f"  [HW] FORCE RATE PROFILE: {profile}")
            if profile == "LIVE":
                self.mode = DeviceMode.LIVE
            elif profile == "SAVER":
                self.mode = DeviceMode.SAVER
            else:
                self.mode = DeviceMode.ADAPTIVE

        elif cmd_name == "PING":
            print("  [HW] PONG - Healthcheck responded.")

        elif cmd_name == "START_OTA":
            url = payload.get("url")
            print(f"  [HW] STARTING FIRMWARE UPDATE from {url}...")
            print("  [HW] Download: [###.......] 30%")
            print("  [HW] Download: [######....] 60%")
            print("  [HW] Download: [##########] 100%")
            print("  [HW] Verifying checksum... OK. Restarting...")

        # Send ACK
        self.send_ack(cmd_id)

    def send_ack(self, command_id: int):
        """Acknowledge command completion."""
        headers = {"X-Device-Key": DEVICE_KEY}
        url = ACK_COMMAND_ENDPOINT.format(command_id)
        try:
            resp = requests.post(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                print(f"  [CMD] ACK sent for command {command_id}")
            else:
                print(f"  [CMD] ACK failed: {resp.status_code}")
        except Exception as e:
            print(f"  [CMD] ACK error: {e}")

    def flush_buffer(self):
        """Send buffered packets."""
        if self.buffer.is_empty() or not self.network_connected:
            return

        batch = self.buffer.get_batch(50)
        print(f"  [NET] Flushing {len(batch)} buffered packets...")

        payload = {
            "device_id": DEVICE_ID,
            "packets": [asdict(p) for p in batch]
        }

        headers = {
            "X-Device-Key": DEVICE_KEY,
            "Content-Type": "application/json"
        }

        try:
            resp = requests.post(
                INGEST_ENDPOINT, json=payload, headers=headers, timeout=10)
            if resp.status_code == 201:
                last_seq = batch[-1].seq_id
                self.buffer.ack_up_to(last_seq)
            else:
                print(f"  [NET] Batch failed: {resp.status_code}")
        except requests.RequestException as e:
            print(f"  [NET] Batch connection failed: {e}")

    def run_cycle(self):
        """Single simulation cycle."""
        print(f"\n{'='*60}")
        print(
            f"[CYCLE] Battery: {self.battery_pct}% | Steps: {self.step_count}")

        # 1. Get motion state
        motion_state, activity, speed = self.simulate_motion()
        print(
            f"  [IMU] Motion: {motion_state}, Activity: {activity.value}, Speed: {speed:.1f} km/h")

        # 2. Update mode
        self.update_mode(motion_state, speed)

        # 3. Get GPS
        gps = self.get_gps_reading(speed)
        print(f"  [GPS] Lat: {gps.lat}, Lon: {gps.lon}, Acc: {gps.accuracy}m")

        # 4. Anti-fraud
        final_activity = self.anti_fraud_check(
            gps.speed_kmh, motion_state, activity)

        # 5. Create packet
        packet = self.create_packet(gps, final_activity, motion_state)

        # 6. Try to send
        if self.network_connected:
            success = self.send_packet(packet)
            if not success:
                self.buffer.add(packet)
            else:
                # After successful telemetry, poll for commands
                self.poll_commands()
            self.flush_buffer()
        else:
            self.buffer.add(packet)
            print(f"  [NET] OFFLINE - Packet buffered.")

        # 7. Drain battery
        self.battery_pct = max(0, self.battery_pct - random.uniform(0.1, 0.5))

    def simulate_network_outage(self, duration_cycles: int):
        """Simulate losing network for N cycles."""
        print(f"\n{'#'*60}")
        print(f"# SIMULATING NETWORK OUTAGE FOR {duration_cycles} CYCLES")
        print(f"{'#'*60}")
        self.network_connected = False

        for i in range(duration_cycles):
            print(f"\n--- Outage Cycle {i+1}/{duration_cycles} ---")
            self.run_cycle()
            time.sleep(1)

        print(f"\n{'#'*60}")
        print(f"# NETWORK RESTORED - FLUSHING BUFFER")
        print(f"{'#'*60}")
        self.network_connected = True
        self.flush_buffer()

# =============================================================================
# MAIN
# =============================================================================


def main():
    print("=" * 60)
    print("ARES v4.0 DEVICE SIMULATOR")
    print("=" * 60)
    print(f"Device ID: {DEVICE_ID}")
    print(f"Backend: {API_BASE_URL}")
    print("=" * 60)

    sim = AresDeviceSimulator()

    # Run 10 normal cycles
    print("\n>>> Running 10 NORMAL cycles...")
    for i in range(10):
        sim.run_cycle()
        time.sleep(2)

    # Simulate network outage (Store & Forward test)
    sim.simulate_network_outage(5)

    # Run 5 more normal cycles
    print("\n>>> Running 5 more NORMAL cycles...")
    for i in range(5):
        sim.run_cycle()
        time.sleep(2)

    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print(f"Final battery: {sim.battery_pct:.1f}%")
    print(f"Total steps: {sim.step_count}")
    print(f"Buffered packets remaining: {len(sim.buffer.buffer)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
