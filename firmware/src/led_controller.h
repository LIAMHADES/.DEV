// =============================================================================
// ARES v4.0 Firmware - LED Controller (12x RGB LEDs)
// =============================================================================
#ifndef LED_CONTROLLER_H
#define LED_CONTROLLER_H

#include "config.h"
#include <Arduino.h>

enum LedMode {
    LED_OFF,
    LED_VISIBILITY,      // Slow blink for night walks
    LED_FIND,            // Fast strobe for locating
    LED_STATUS_OK,       // Green pulse
    LED_STATUS_WARNING,  // Yellow pulse
    LED_STATUS_ERROR     // Red pulse
};

class LedController {
private:
    LedMode currentMode;
    unsigned long modeStartTime;
    unsigned long modeTimeoutMs;
    bool ledState;
    unsigned long lastToggle;
    
    // PWM channels
    int pwmR, pwmG, pwmB;
    
    // Calibration factors (from SPEC)
    const float R_CALIB = 0.60;
    const float G_CALIB = 0.90;
    const float B_CALIB = 1.0;
    
public:
    void begin() {
        currentMode = LED_OFF;
        modeStartTime = 0;
        modeTimeoutMs = 0;
        ledState = false;
        lastToggle = 0;
        
        // Configure PWM channels (ESP32)
        ledcSetup(0, 2000, 8); // R channel, 2kHz, 8-bit
        ledcSetup(1, 2000, 8); // G channel
        ledcSetup(2, 2000, 8); // B channel
        
        ledcAttachPin(LED_R_PIN, 0);
        ledcAttachPin(LED_G_PIN, 1);
        ledcAttachPin(LED_B_PIN, 2);
        
        setColor(0, 0, 0); // Off
        Serial.println("[LED] Controller initialized. LEDs OFF.");
    }
    
    void setColor(int r, int g, int b) {
        // Apply calibration
        int rCal = (int)(r * R_CALIB);
        int gCal = (int)(g * G_CALIB);
        int bCal = (int)(b * B_CALIB);
        
        ledcWrite(0, rCal);
        ledcWrite(1, gCal);
        ledcWrite(2, bCal);
    }
    
    void setMode(LedMode mode, unsigned long timeoutMs = 0) {
        currentMode = mode;
        modeStartTime = millis();
        modeTimeoutMs = timeoutMs;
        Serial.println("[LED] Mode changed to: " + String(mode) + ", timeout=" + String(timeoutMs) + "ms");
    }
    
    // Called in main loop
    void update() {
        unsigned long now = millis();
        
        // Check timeout
        if (modeTimeoutMs > 0 && (now - modeStartTime >= modeTimeoutMs)) {
            Serial.println("[LED] Mode timeout reached. Turning OFF.");
            currentMode = LED_OFF;
        }
        
        switch (currentMode) {
            case LED_OFF:
                setColor(0, 0, 0);
                break;
                
            case LED_VISIBILITY:
                // Slow blink (0.5 Hz): 1s on, 1s off
                if (now - lastToggle >= 1000) {
                    lastToggle = now;
                    ledState = !ledState;
                    if (ledState) setColor(255, 255, 255); // White
                    else setColor(0, 0, 0);
                }
                break;
                
            case LED_FIND:
                // Fast strobe (4 Hz): 125ms on, 125ms off (ALWAYS BLINK to save power)
                if (now - lastToggle >= 125) {
                    lastToggle = now;
                    ledState = !ledState;
                    if (ledState) setColor(0, 255, 255); // Cyan (max visibility)
                    else setColor(0, 0, 0);
                }
                break;
                
            case LED_STATUS_OK:
                // Soft green pulse
                pulseColor(0, 150, 0);
                break;
                
            case LED_STATUS_WARNING:
                // Yellow pulse
                pulseColor(200, 150, 0);
                break;
                
            case LED_STATUS_ERROR:
                // Red pulse
                pulseColor(255, 0, 0);
                break;
        }
    }
    
    void pulseColor(int r, int g, int b) {
        // Simple breathing effect
        float phase = (millis() % 2000) / 1000.0; // 0 to 2
        float brightness;
        if (phase < 1.0) brightness = phase;
        else brightness = 2.0 - phase;
        
        setColor((int)(r * brightness), (int)(g * brightness), (int)(b * brightness));
    }
    
    bool canUseLeds(int batteryPct) {
        if (batteryPct < BATTERY_LED_BLOCK_PCT) {
            Serial.println("[LED] BLOCKED: Battery too low (" + String(batteryPct) + "%)");
            return false;
        }
        return true;
    }
    
    LedMode getMode() {
        return currentMode;
    }
};

#endif // LED_CONTROLLER_H
