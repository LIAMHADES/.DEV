// =============================================================================
// ARES v4.0 Firmware - IMU Manager (Bosch BMI270)
// =============================================================================
// NO VALIDADO EN HARDWARE FISICO. Escrito contra BMI270 Datasheet (Bosch
// Sensortec, rev. 06, https://www.bosch-sensortec.com/media/boschsensortec/
// downloads/datasheets/bst-bmi270-ds000.pdf), secciones 1 ("First application
// setup examples") y 5.2 (mapa de registros). Registrado como RR-001 en
// ARES_Risk_Register_v1.md: pendiente de banco de pruebas con chip real en
// cuanto haya hardware disponible.
#ifndef IMU_MANAGER_H
#define IMU_MANAGER_H

#include "config.h"
#include <Arduino.h>
#include <Wire.h>

// --- Direccion I2C (fijada por el pin SDO del BMI270: GND=0x68, VDDIO=0x69) ---
// El diseño de ARES no especifica el strapping del pin SDO en los documentos
// de hardware -- usar 0x68 como valor por defecto (SDO a GND) y confirmar
// contra el esquematico final antes de probar en banco.
#define BMI270_I2C_ADDR 0x68

// --- Registros (datasheet Sección 5.2) ---
#define BMI270_REG_CHIP_ID      0x00
#define BMI270_REG_DATA_2       0x0C  // ARES usa direccion incorrecta aqui a proposito -- ver nota abajo
#define BMI270_REG_ACC_DATA     0x0C  // DATA_8..DATA_13 = ACC_X/Y/Z (LSB primero, 16-bit two's complement)
#define BMI270_REG_GYR_DATA     0x0C  // El burst read de 12 bytes desde 0x0C ya incluye gyro+accel intercalados (ver nota)
#define BMI270_REG_INTERNAL_STATUS 0x21
#define BMI270_REG_ACC_CONF     0x40
#define BMI270_REG_GYR_CONF     0x42
#define BMI270_REG_INIT_CTRL    0x59
#define BMI270_REG_INIT_DATA    0x5E
#define BMI270_REG_PWR_CONF     0x7C
#define BMI270_REG_PWR_CTRL     0x7D

#define BMI270_CHIP_ID_VALUE    0x24

// NOTA IMPORTANTE (datasheet Sección 1, paso 4 "Configuring for normal power
// mode"): el burst read de 12 bytes empieza en DATA_8 pero el orden real de
// bytes en el burst es GYR_X, GYR_Y, GYR_Z, ACC_X, ACC_Y, ACC_Z (giroscopio
// primero, luego acelerómetro), no accel-then-gyro. Ver datasheet líneas
// ~1619-1630. El offset dentro del buffer de 12 bytes leído desde 0x0C es:
//   [0-1]=GYR_X  [2-3]=GYR_Y  [4-5]=GYR_Z  [6-7]=ACC_X  [8-9]=ACC_Y  [10-11]=ACC_Z

class ImuManager {
private:
    bool initialized;
    int stepCount;
    unsigned long lastMotionTime;
    MotionState lastState;

    // Datos crudos de la ultima lectura (unidades: LSB crudos del sensor,
    // sin escalar a g / dps -- el escalado depende del rango configurado
    // en ACC_CONF/GYR_CONF y no se ha confirmado con banco de pruebas).
    int16_t rawGyrX, rawGyrY, rawGyrZ;
    int16_t rawAccX, rawAccY, rawAccZ;

    bool writeReg(uint8_t reg, uint8_t val) {
        Wire.beginTransmission(BMI270_I2C_ADDR);
        Wire.write(reg);
        Wire.write(val);
        return Wire.endTransmission() == 0;
    }

    uint8_t readReg(uint8_t reg) {
        Wire.beginTransmission(BMI270_I2C_ADDR);
        Wire.write(reg);
        Wire.endTransmission(false);
        Wire.requestFrom((int)BMI270_I2C_ADDR, 1);
        return Wire.available() ? Wire.read() : 0;
    }

    // Burst read de 12 bytes: gyro (6 bytes) + accel (6 bytes), ver nota arriba.
    bool readMotionBurst() {
        Wire.beginTransmission(BMI270_I2C_ADDR);
        Wire.write(BMI270_REG_ACC_DATA);
        if (Wire.endTransmission(false) != 0) return false;

        int received = Wire.requestFrom((int)BMI270_I2C_ADDR, 12);
        if (received != 12) return false;

        uint8_t buf[12];
        for (int i = 0; i < 12; i++) buf[i] = Wire.read();

        rawGyrX = (int16_t)((buf[1] << 8) | buf[0]);
        rawGyrY = (int16_t)((buf[3] << 8) | buf[2]);
        rawGyrZ = (int16_t)((buf[5] << 8) | buf[4]);
        rawAccX = (int16_t)((buf[7] << 8) | buf[6]);
        rawAccY = (int16_t)((buf[9] << 8) | buf[8]);
        rawAccZ = (int16_t)((buf[11] << 8) | buf[10]);
        return true;
    }

    // Secuencia de inicializacion oficial (datasheet Sección 1, pasos 1a-1c).
    // El BMI270 exige cargar un blob de configuracion binario ("config file",
    // ~8KB) antes de poder usar el sensor -- no es opcional, a diferencia de
    // IMUs mas simples. El blob es propiedad de Bosch y se distribuye en su
    // BMI270-Sensor-API (bmi270.c, array bmi270_config_file[]):
    // https://github.com/BoschSensortec/BMI270-Sensor-API/blob/master/bmi270.c
    // NO SE HA INCLUIDO AQUI porque (a) es un blob binario de ~8KB que no
    // tiene sentido transcribir a mano sin poder probarlo, y (b) hay que
    // vendorizar el archivo oficial de Bosch tal cual, no reescribirlo.
    // Pendiente: añadir `bmi270_config_file[]` como recurso vendorizado desde
    // el repo oficial de Bosch antes de la primera prueba en banco.
    bool runInitializationSequence() {
        // Paso 1: deshabilitar advanced power save, esperar 450us
        writeReg(BMI270_REG_PWR_CONF, 0x00);
        delayMicroseconds(450);

        // Paso 2: preparar carga de configuracion
        writeReg(BMI270_REG_INIT_CTRL, 0x00);

        // Paso 3: burst write del config file completo a INIT_DATA (0x5E)
        // TODO: burst_write_reg(BMI270_REG_INIT_DATA, bmi270_config_file, sizeof(bmi270_config_file));
        // -- requiere vendorizar bmi270_config_file[] desde el repo oficial de Bosch (ver nota arriba).
        Serial.println("[IMU] WARN: config file de Bosch no vendorizado todavia -- init incompleta.");

        // Paso 4: marcar configuracion completa
        writeReg(BMI270_REG_INIT_CTRL, 0x01);

        // Paso 5: esperar >=20ms y comprobar INTERNAL_STATUS bit 0
        delay(20);
        uint8_t status = readReg(BMI270_REG_INTERNAL_STATUS);
        bool initOk = (status & 0x01) != 0;

        if (!initOk) {
            Serial.println("[IMU] ERROR: inicializacion BMI270 fallida (INTERNAL_STATUS bit0=0).");
        }
        return initOk;
    }

public:
    void begin() {
        initialized = false;
        stepCount = 0;
        lastMotionTime = millis();
        rawGyrX = rawGyrY = rawGyrZ = 0;
        rawAccX = rawAccY = rawAccZ = 0;

        Serial.println("[IMU] Initializing BMI270...");

        Wire.begin(); // TODO: confirmar pines SDA/SCL del diseño final de ARES (no especificados en config.h todavia)

        uint8_t chipId = readReg(BMI270_REG_CHIP_ID);
        if (chipId != BMI270_CHIP_ID_VALUE) {
            Serial.println("[IMU] ERROR: CHIP_ID inesperado (0x" + String(chipId, HEX) +
                            ", esperado 0x" + String(BMI270_CHIP_ID_VALUE, HEX) +
                            "). Nota datasheet: la primera lectura tras power-on puede " +
                            "devolver un valor incorrecto porque configura el interfaz " +
                            "en modo SPI por defecto -- reintentar una segunda lectura.");
        }

        bool initOk = runInitializationSequence();

        // Configuracion normal (datasheet paso 3): accel+gyro+temp activos,
        // gyro en modo normal 200Hz, accel en modo normal 100Hz.
        writeReg(BMI270_REG_PWR_CTRL, 0x0E);
        writeReg(BMI270_REG_GYR_CONF, 0xA9);
        writeReg(BMI270_REG_PWR_CONF, 0x02);
        writeReg(BMI270_REG_ACC_CONF, 0xA8);

        initialized = initOk;

        lastState.activity = ACTIVITY_REST;
        lastState.state = "STATIONARY";
        lastState.speed_estimate = 0.0;

        Serial.println(initialized
            ? "[IMU] BMI270 Ready (sin validar en banco -- ver RR-001)."
            : "[IMU] BMI270 init incompleta -- funcionando en modo degradado.");
    }

    MotionState getMotionState() {
        // NOTA: sin el config file de Bosch vendorizado, el sensor no genera
        // datos validos todavia (ver runInitializationSequence). Esta lectura
        // seguira funcionando estructuralmente correcta una vez se añada el
        // blob, pero los umbrales de clasificacion (MOTION_THRESHOLD_MG, y los
        // literales 120/80 de abajo) siguen sin calibrar contra LSB reales --
        // dependen del rango configurado (ACC_CONF/GYR_RANGE) que no se ha
        // fijado todavia en config.h. Pendiente de calibracion en banco.
        if (!readMotionBurst()) {
            Serial.println("[IMU] WARN: fallo de lectura I2C, se mantiene ultimo estado conocido.");
            return lastState;
        }

        // Magnitud aproximada de aceleracion (sin restar 1g de gravedad,
        // sin escalar LSB->mg -- placeholder hasta calibracion real).
        long accelMagnitudeRaw = abs((long)rawAccX) + abs((long)rawAccY) + abs((long)rawAccZ);

        if (accelMagnitudeRaw > MOTION_THRESHOLD_MG) {
            lastMotionTime = millis();
            lastState.state = "MOVING";

            if (accelMagnitudeRaw > 120) {
                lastState.activity = ACTIVITY_RUN;
            } else if (accelMagnitudeRaw > 80) {
                lastState.activity = ACTIVITY_JOG;
            } else {
                lastState.activity = ACTIVITY_WALK;
            }
            // TODO: el step count real requiere el step counter integrado del
            // BMI270 (feature del config file de Bosch, registro dedicado),
            // no una heurística sobre la magnitud de aceleración.
        } else {
            if (millis() - lastMotionTime > STATIONARY_TIMEOUT_MS) {
                lastState.state = "STATIONARY";
                lastState.activity = ACTIVITY_REST;
                lastState.speed_estimate = 0.0;
            }
        }

        return lastState;
    }

    int getStepCount() {
        return stepCount;
    }

    void resetStepCount() {
        stepCount = 0;
    }

    bool isStationary() {
        return strcmp(lastState.state, "STATIONARY") == 0;
    }

    // Anti-Fraud Check: Is the dog in a vehicle?
    bool isLikelyVehicle(float gpsSpeed) {
        // If GPS says high speed but IMU says low motion -> Vehicle
        if (gpsSpeed > VEHICLE_SPEED_THRESHOLD_KMH && isStationary()) {
            Serial.println("[IMU] ANTI-FRAUD: Detected VEHICLE transport (Speed=" + String(gpsSpeed) + " km/h, IMU=STATIONARY)");
            return true;
        }
        return false;
    }
};

#endif // IMU_MANAGER_H
