// =============================================================================
// ARES v4.0 Firmware - Storage Manager (Store & Forward Buffer)
// =============================================================================
#ifndef STORAGE_MANAGER_H
#define STORAGE_MANAGER_H

#include "config.h"
#include <Arduino.h>
// In production: #include <LittleFS.h> or <SPIFFS.h>

class StorageManager {
private:
    // Circular buffer in RAM for prototype (use Flash/NVS in production)
    TelemetryPacket buffer[BUFFER_MAX_PACKETS];
    int head;
    int tail;
    int count;
    uint32_t nextSeqId;
    
public:
    void begin() {
        head = 0;
        tail = 0;
        count = 0;
        nextSeqId = 1;
        Serial.println("[Storage] Buffer initialized. Capacity: " + String(BUFFER_MAX_PACKETS));
    }
    
    uint32_t getNextSeqId() {
        return nextSeqId++;
    }
    
    // Store a packet in the circular buffer
    bool bufferPacket(TelemetryPacket& packet) {
        if (count >= BUFFER_MAX_PACKETS) {
            // Buffer full - overwrite oldest (circular)
            Serial.println("[Storage] Buffer FULL. Overwriting oldest packet.");
            tail = (tail + 1) % BUFFER_MAX_PACKETS;
        } else {
            count++;
        }
        
        buffer[head] = packet;
        head = (head + 1) % BUFFER_MAX_PACKETS;
        
        Serial.println("[Storage] Packet buffered. seq_id=" + String(packet.seq_id) + ", count=" + String(count));
        return true;
    }
    
    // Get the next batch of packets to send
    int getBatch(TelemetryPacket* outBatch, int maxBatch) {
        int toSend = min(count, maxBatch);
        for (int i = 0; i < toSend; i++) {
            int idx = (tail + i) % BUFFER_MAX_PACKETS;
            outBatch[i] = buffer[idx];
        }
        return toSend;
    }
    
    // Acknowledge packets up to (and including) the given seq_id
    void ackUpTo(uint32_t lastAckedSeqId) {
        int removed = 0;
        while (count > 0) {
            int idx = tail;
            if (buffer[idx].seq_id <= lastAckedSeqId) {
                tail = (tail + 1) % BUFFER_MAX_PACKETS;
                count--;
                removed++;
            } else {
                break; // All older ones removed
            }
        }
        Serial.println("[Storage] ACK received. Removed " + String(removed) + " packets. Remaining: " + String(count));
    }
    
    int getBufferedCount() {
        return count;
    }
    
    bool isEmpty() {
        return count == 0;
    }
};

#endif // STORAGE_MANAGER_H
