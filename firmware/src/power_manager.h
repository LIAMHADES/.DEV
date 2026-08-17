// =============================================================================
// ARES v4.0 Firmware - Power Manager (State Machine)
// =============================================================================
#ifndef POWER_MANAGER_H
#define POWER_MANAGER_H

#include "config.h"
#include <Arduino.h>

class PowerManager {
private:
    DeviceMode currentMode;
    unsigned long lastMotionTime;
    unsigned long liveModeStartTime;
    bool liveModeForcedByUser;
    
public:
    void begin() {
        currentMode = MODE_ADAPTIVE;
        lastMotionTime = millis();
        liveModeForcedByUser = false;
        Serial.println("[PowerMgr] Initialized in ADAPTIVE mode.");
    }
    
    // Core State Machine - Called every loop
    DeviceMode updateMode(MotionState& motion) {
        unsigned long now = millis();
        
        // --- Live Mode Timeout Check ---
        if (liveModeForcedByUser && currentMode == MODE_LIVE) {
            if (now - liveModeStartTime >= LIVE_MODE_TIMEOUT_MS) {
                Serial.println("[PowerMgr] LIVE mode timeout. Returning to ADAPTIVE.");
                liveModeForcedByUser = false;
                currentMode = MODE_ADAPTIVE;
            }
        }
        
        // --- Don't override if in forced LIVE mode ---
        if (liveModeForcedByUser) {
            return currentMode;
        }
        
        // --- Motion-based transitions ---
        if (strcmp(motion.state, "MOVING") == 0) {
            lastMotionTime = now;
            
            // Determine speed-based mode
            if (motion.speed_estimate > 15.0) {
                currentMode = MODE_LIVE; // Fast movement needs frequent updates
            } else if (motion.speed_estimate > 5.0) {
                currentMode = MODE_ADAPTIVE;
            } else {
                currentMode = MODE_SAVER;
            }
        } else {
            // Stationary
            if (now - lastMotionTime >= STATIONARY_TIMEOUT_MS) {
                currentMode = MODE_DEEP_SLEEP;
            }
        }
        
        return currentMode;
    }
    
    // Force LIVE mode (from user command)
    void forceLiveMode() {
        Serial.println("[PowerMgr] LIVE mode FORCED by user.");
        currentMode = MODE_LIVE;
        liveModeForcedByUser = true;
        liveModeStartTime = millis();
    }
    
    // Get GPS interval based on current mode
    unsigned long getGpsIntervalMs(DeviceMode mode) {
        switch (mode) {
            case MODE_LIVE:       return GPS_INTERVAL_LIVE_MS;
            case MODE_ADAPTIVE:   return GPS_INTERVAL_ADAPTIVE_MS;
            case MODE_SAVER:      return GPS_INTERVAL_SAVER_MS;
            case MODE_DEEP_SLEEP: return GPS_INTERVAL_SAVER_MS * 10; // Very infrequent
            default:              return GPS_INTERVAL_ADAPTIVE_MS;
        }
    }
    
    // Battery Reading (Placeholder - needs ADC implementation)
    int getBatteryMv() {
        // TODO: Read actual ADC value
        return 3800; // Placeholder
    }
    
    int getBatteryPercent() {
        int mv = getBatteryMv();
        // Simple linear mapping 3.0V = 0%, 4.2V = 100%
        int pct = map(mv, 3000, 4200, 0, 100);
        return constrain(pct, 0, 100);
    }
    
    bool isBatteryCritical() {
        return getBatteryPercent() <= BATTERY_CRITICAL_PCT;
    }
    
    bool isBatteryLow() {
        return getBatteryPercent() <= BATTERY_LOW_PCT;
    }
    
    // Enter Light Sleep (ESP32)
    void enterLightSleep(unsigned long durationMs) {
        Serial.println("[PowerMgr] Entering LIGHT SLEEP...");
        // esp_sleep_enable_timer_wakeup(durationMs * 1000);
        // esp_light_sleep_start();
        delay(durationMs); // Placeholder for simulation
    }
    
    DeviceMode getCurrentMode() {
        return currentMode;
    }
};

#endif // POWER_MANAGER_H
