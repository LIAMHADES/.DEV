// =============================================================================
// ARES v4.0 Firmware - Configuration
// =============================================================================
#ifndef CONFIG_H
#define CONFIG_H

// --- Firmware Version ---
#define FW_VERSION "4.0.0"

// --- Device Identity ---
// These would be read from EEPROM/NVS in production
#define DEVICE_ID "ARES-PROTO-001"
#define DEVICE_KEY "your-secret-key-here"

// --- Backend Endpoints ---
#define API_HOST "api.ares.pet"
#define API_PORT 443
#define INGEST_ENDPOINT "/v1/iot/ingest"
#define HEARTBEAT_ENDPOINT "/v1/iot/heartbeat"
#define COMMAND_ENDPOINT "/v1/iot/commands"
#define OTA_CHECK_ENDPOINT "/v1/iot/ota/check"

// --- Cellular / APN (1NCE) ---
#define CELL_APN        "iot.1nce.net"
#define CELL_APN_USER   ""
#define CELL_APN_PASS   ""
// If stack requires auth: PAP
#define CELL_APN_AUTH_PAP 1
#define CELL_PDP_TYPE   "IP"   // IPv4
#define CELL_SIM_PIN    ""     // Leave empty if not set


// --- Timing (ms) ---
#define HEARTBEAT_INTERVAL_MS 300000  // 5 minutes
#define GPS_INTERVAL_LIVE_MS 5000     // 5 seconds (Live Mode)
#define GPS_INTERVAL_ADAPTIVE_MS 15000 // 15 seconds (Adaptive)
#define GPS_INTERVAL_SAVER_MS 60000   // 60 seconds (Saver)
#define GPS_INTERVAL_GUARD_MS 10000   // 10 seconds (Near Geofence)
#define LIVE_MODE_TIMEOUT_MS 600000   // 10 minutes max Live

// --- Power Thresholds ---
#define BATTERY_CRITICAL_PCT 5
#define BATTERY_LOW_PCT 15
#define BATTERY_LED_BLOCK_PCT 15  // Block LED usage below this

// --- Motion Detection (BMI270) ---
#define MOTION_THRESHOLD_MG 50       // Movement threshold in milli-g
#define STATIONARY_TIMEOUT_MS 120000 // 2 minutes to enter Deep Sleep
#define VEHICLE_SPEED_THRESHOLD_KMH 25.0 // Anti-Fraud

// --- Store & Forward ---
#define BUFFER_MAX_PACKETS 10000     // ~24 hours of tracking
#define BATCH_UPLOAD_SIZE 50         // Packets per batch upload

// --- LED Pins (LilyGo T-SIM7000G) ---
#define LED_R_PIN 16
#define LED_G_PIN 17
#define LED_B_PIN 18

// --- Enums ---
enum DeviceMode {
    MODE_DEEP_SLEEP,
    MODE_SAVER,
    MODE_ADAPTIVE,
    MODE_LIVE,
    MODE_DEGRADED
};

enum MotionActivity {
    ACTIVITY_REST,
    ACTIVITY_WALK,
    ACTIVITY_JOG,
    ACTIVITY_RUN,
    ACTIVITY_VEHICLE
};

enum ResetReason {
    RESET_REASON_NONE,
    RESET_REASON_POWER_ON,
    RESET_REASON_WATCHDOG,
    RESET_REASON_BROWNOUT,
    RESET_REASON_PANIC
};

// --- Structs ---
struct MotionState {
    MotionActivity activity;
    const char* state; // "MOVING", "STATIONARY"
    float speed_estimate;
};

struct GpsReading {
    bool valid;
    unsigned long timestamp;
    double lat;
    double lon;
    float altitude;
    float speed;
    float heading;
    float accuracy;
    int satellites;
    const char* fix_type; // "GNSS", "WIFI", "CELL"
};

struct TelemetryPacket {
    uint32_t seq_id;
    unsigned long timestamp;
    double lat;
    double lon;
    float altitude;
    float speed_kmh;
    float heading_deg;
    float accuracy;
    int satellites;
    const char* fix_type;
    int battery_mv;
    MotionActivity activity_mode;
    const char* motion_state;
    int steps;
};

struct HeartbeatPacket {
    unsigned long uptime_s;
    ResetReason reset_reason;
    int failed_tx_count;
    const char* fw_version;
    int battery_pct;
};

#endif // CONFIG_H
