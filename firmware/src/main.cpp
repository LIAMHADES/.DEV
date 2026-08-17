// =============================================================================
// ARES v4.0 Firmware - Main Entry Point
// Hardware: LilyGo T-SIM7000G S3 + Bosch BMI270 + Ignion A101
// =============================================================================
#include <Arduino.h>
#include "config.h"
#include "power_manager.h"
#include "network_manager.h"
#include "gps_manager.h"
#include "imu_manager.h"
#include "led_controller.h"
#include "storage_manager.h"

// --- Global Managers ---
PowerManager powerMgr;
NetworkManager networkMgr;
GpsManager gpsMgr;
ImuManager imuMgr;
LedController ledCtrl;
StorageManager storageMgr;

// --- Timing ---
unsigned long lastGpsPoll = 0;
unsigned long lastHeartbeat = 0;

void setup() {
    Serial.begin(115200);
    Serial.println("[ARES] Booting v4.0...");

    // 1. Initialize Storage (for Store & Forward buffer)
    storageMgr.begin();
    
    // 2. Initialize Sensors
    imuMgr.begin();
    gpsMgr.begin();
    
    // 3. Initialize Network (LTE-M)
    networkMgr.begin();
    
    // 4. Initialize LEDs
    ledCtrl.begin();
    
    // 5. Initialize Power Manager (State Machine)
    powerMgr.begin();
    
    // 6. Send initial boot heartbeat
    sendHeartbeat(RESET_REASON_POWER_ON);
    
    Serial.println("[ARES] Boot complete. Entering main loop.");
}

void loop() {
    // --- 1. Read IMU for motion detection ---
    MotionState motion = imuMgr.getMotionState();
    
    // --- 2. Power Manager decides current mode based on motion ---
    DeviceMode currentMode = powerMgr.updateMode(motion);
    
    // --- 3. Get GPS interval based on mode ---
    unsigned long gpsInterval = powerMgr.getGpsIntervalMs(currentMode);
    
    // --- 4. Poll GPS if interval elapsed ---
    if (millis() - lastGpsPoll >= gpsInterval) {
        lastGpsPoll = millis();
        
        GpsReading reading = gpsMgr.getReading();
        
        if (reading.valid) {
            // Create telemetry packet
            TelemetryPacket packet = createPacket(reading, motion);
            
            // Try to send
            if (networkMgr.isConnected()) {
                bool sent = networkMgr.sendPacket(packet);
                if (!sent) {
                    storageMgr.bufferPacket(packet); // Store & Forward
                }
                // Also try to flush buffered packets
                networkMgr.flushBuffer(storageMgr);
            } else {
                storageMgr.bufferPacket(packet); // No network, buffer it
            }
        }
    }
    
    // --- 5. Heartbeat (every 5 min or configurable) ---
    if (millis() - lastHeartbeat >= HEARTBEAT_INTERVAL_MS) {
        lastHeartbeat = millis();
        sendHeartbeat(RESET_REASON_NONE);
    }
    
    // --- 6. Process incoming commands (if any) ---
    networkMgr.processDownlink();
    
    // --- 7. LED Controller update ---
    ledCtrl.update();
    
    // --- 8. Enter light sleep if in SAVER mode ---
    if (currentMode == MODE_DEEP_SLEEP) {
        powerMgr.enterLightSleep(60000); // Wake in 60s or on motion
    }
    
    delay(100); // Main loop tick
}

// --- Helper: Create Telemetry Packet ---
TelemetryPacket createPacket(GpsReading& gps, MotionState& motion) {
    TelemetryPacket p;
    p.seq_id = storageMgr.getNextSeqId();
    p.timestamp = gps.timestamp;
    p.lat = gps.lat;
    p.lon = gps.lon;
    p.altitude = gps.altitude;
    p.speed_kmh = gps.speed;
    p.heading_deg = gps.heading;
    p.accuracy = gps.accuracy;
    p.satellites = gps.satellites;
    p.fix_type = gps.fix_type;
    p.battery_mv = powerMgr.getBatteryMv();
    p.activity_mode = motion.activity;
    p.motion_state = motion.state;
    p.steps = imuMgr.getStepCount();
    return p;
}

// --- Helper: Send Heartbeat ---
void sendHeartbeat(ResetReason reason) {
    HeartbeatPacket hb;
    hb.uptime_s = millis() / 1000;
    hb.reset_reason = reason;
    hb.failed_tx_count = networkMgr.getFailedTxCount();
    hb.fw_version = FW_VERSION;
    hb.battery_pct = powerMgr.getBatteryPercent();
    
    networkMgr.sendHeartbeat(hb);
}
