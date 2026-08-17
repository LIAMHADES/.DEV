// =============================================================================
// ARES v4.0 Firmware - Network Manager (LTE-M + HTTPS)
// =============================================================================
#ifndef NETWORK_MANAGER_H
#define NETWORK_MANAGER_H

#include "config.h"
#include "storage_manager.h"
#include <Arduino.h>
// In production: #include <TinyGsmClient.h>

class NetworkManager {
private:
    bool connected;
    int failedTxCount;
    unsigned long timeSearchingNetworkMs;
    
public:
    void begin() {
        connected = false;
        failedTxCount = 0;
        timeSearchingNetworkMs = 0;
        Serial.println("[Network] Initializing SIM7000G modem...");
        // TODO: Initialize TinyGSM modem
        connect();
    }
    
    bool connect() {
        unsigned long start = millis();
        Serial.println("[Network] Connecting to LTE-M network...");
        
        // Simulation: Pretend we connect after 2 seconds
        delay(2000);
        connected = true;
        
        timeSearchingNetworkMs += (millis() - start);
        Serial.println("[Network] Connected to network.");
        return connected;
    }
    
    bool isConnected() {
        // TODO: Check actual modem status
        return connected;
    }
    
    // Send a single telemetry packet
    bool sendPacket(TelemetryPacket& packet) {
        if (!connected) {
            failedTxCount++;
            return false;
        }
        
        Serial.println("[Network] Sending packet seq_id=" + String(packet.seq_id));
        
        // TODO: Build JSON, send via HTTPS POST to INGEST_ENDPOINT
        // For now, simulate success
        bool success = true; // random(0, 10) > 1; // 90% success rate
        
        if (!success) {
            failedTxCount++;
            Serial.println("[Network] TX FAILED.");
        } else {
            Serial.println("[Network] TX OK.");
        }
        
        return success;
    }
    
    // Flush buffered packets (Store & Forward)
    void flushBuffer(StorageManager& storage) {
        if (storage.isEmpty() || !connected) return;
        
        Serial.println("[Network] Flushing buffer...");
        
        TelemetryPacket batch[BATCH_UPLOAD_SIZE];
        int batchSize = storage.getBatch(batch, BATCH_UPLOAD_SIZE);
        
        if (batchSize == 0) return;
        
        // TODO: Send as JSON array batch
        Serial.println("[Network] Sending batch of " + String(batchSize) + " packets...");
        
        // Simulate successful batch upload
        bool success = true;
        
        if (success) {
            // Get the highest seq_id in the batch
            uint32_t lastSeq = batch[batchSize - 1].seq_id;
            storage.ackUpTo(lastSeq);
            Serial.println("[Network] Batch OK. ACKed up to seq_id=" + String(lastSeq));
        } else {
            failedTxCount++;
            Serial.println("[Network] Batch FAILED.");
        }
    }
    
    // Send heartbeat
    bool sendHeartbeat(HeartbeatPacket& hb) {
        if (!connected) return false;
        
        Serial.println("[Network] Sending heartbeat (uptime=" + String(hb.uptime_s) + "s, battery=" + String(hb.battery_pct) + "%)");
        // TODO: HTTPS POST to HEARTBEAT_ENDPOINT
        return true;
    }
    
    // Process incoming downlink commands
    void processDownlink() {
        // TODO: Poll COMMAND_ENDPOINT or use MQTT subscribe
        // For now, placeholder
    }
    
    int getFailedTxCount() {
        return failedTxCount;
    }
    
    unsigned long getTimeSearchingNetworkMs() {
        return timeSearchingNetworkMs;
    }
    
    void simulateDisconnect() {
        connected = false;
        Serial.println("[Network] SIMULATED: Network disconnected.");
    }
    
    void simulateReconnect() {
        connect();
    }
};

#endif // NETWORK_MANAGER_H
