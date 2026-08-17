// =============================================================================
// ARES v4.0 Firmware - GPS Manager (SIM7000G GNSS)
// =============================================================================
#ifndef GPS_MANAGER_H
#define GPS_MANAGER_H

#include "config.h"
#include <Arduino.h>
// In production: #include <TinyGPSPlus.h>

class GpsManager {
private:
    bool gpsEnabled;
    unsigned long lastFixTime;
    unsigned long timeToFixMs;
    GpsReading lastReading;
    
public:
    void begin() {
        gpsEnabled = false;
        lastFixTime = 0;
        timeToFixMs = 0;
        Serial.println("[GPS] Initializing SIM7000G GNSS...");
        enableGps();
    }
    
    void enableGps() {
        Serial.println("[GPS] Enabling GNSS module...");
        gpsEnabled = true;
        // TODO: Send AT command to enable GNSS on SIM7000G
    }
    
    void disableGps() {
        Serial.println("[GPS] Disabling GNSS module (power save).");
        gpsEnabled = false;
        // TODO: Send AT command to disable GNSS
    }
    
    GpsReading getReading() {
        GpsReading reading;
        reading.valid = false;
        
        if (!gpsEnabled) {
            enableGps();
        }
        
        unsigned long start = millis();
        
        // TODO: Parse NMEA or use TinyGPS++
        // Simulating a valid fix
        reading.valid = true;
        reading.timestamp = millis();
        reading.lat = 40.416775 + (random(-100, 100) / 100000.0);  // Madrid area
        reading.lon = -3.703790 + (random(-100, 100) / 100000.0);
        reading.altitude = 650.0 + (random(-10, 10) / 10.0);
        reading.speed = random(0, 80) / 10.0;  // 0-8 km/h
        reading.heading = random(0, 360);
        reading.accuracy = 1.5 + (random(0, 20) / 10.0); // 1.5-3.5m
        reading.satellites = random(8, 14);
        reading.fix_type = "GNSS";
        
        timeToFixMs = millis() - start;
        lastFixTime = millis();
        lastReading = reading;
        
        Serial.println("[GPS] Fix: lat=" + String(reading.lat, 6) + 
                       ", lon=" + String(reading.lon, 6) +
                       ", acc=" + String(reading.accuracy) + "m" +
                       ", sats=" + String(reading.satellites));
        
        return reading;
    }
    
    unsigned long getAgeOfFixMs() {
        if (lastFixTime == 0) return 0xFFFFFFFF; // Never had a fix
        return millis() - lastFixTime;
    }
    
    unsigned long getLastTimeToFixMs() {
        return timeToFixMs;
    }
    
    GpsReading getLastReading() {
        return lastReading;
    }
};

#endif // GPS_MANAGER_H
