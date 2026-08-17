**AVISO: DOCUMENTO OBSOLETO (v3.6)**
Este archivo es una especificación técnica de una versión antigua del proyecto. La arquitectura, baterías y método de carga descritos aquí están desactualizados.
La información final y válida se encuentra en la carpeta `PRODUTO_V4_FINAL` (o `ACTUAL`), en los documentos maestros de la versión 4.0.

---

# ARES GPS: Especificación Técnica Final (v3.6 Sistema Modular)

Este documento es el **Manual Maestro** del proyecto ARES. Describe la arquitectura final modular del producto.

## 1. Misión y Requisitos de Producto

Crear un localizador de grado industrial con un sistema de **batería intercambiable** para garantizar un seguimiento ininterrumpido.

- **Precisión GNSS**: **0.8m a 1.8m** gracias a la antena Ignion A101 con LNA y el filtro Kalman.
- **Conectividad**: LTE-M (con eSIM soldada) + BLE 5.x.
- **Sensor de Actividad**: IMU **Bosch BMI270** para antifraude y predicción de ruta.
- **Autonomía**: **~30h a 90h** con packs de batería intercambiables (850/1200/2800mAh).
- **Protección**: Carcasa hermética IP68, con carga aislada en el módulo de batería.

## 2. Arquitectura de Sistema v3.6 (Modular)

El diseño se divide en dos módulos acoplables para maximizar la durabilidad y la experiencia de usuario.

### 2.1. Módulo A: "Cerebro"
Unidad sellada que contiene toda la electrónica principal:
- **MCU/LTE/GPS**: LilyGo T-SIM7000G.
- **Sensores**: Bosch BMI270 (IMU), Ignion A101 (Antena) + LNA, eSIM.
- **PCB**: Placa de 4 capas de 37x28mm.
- **Conexión**: 4 pads de oro para contacto con el módulo de batería.

### 2.2. Módulo B: "Power Pack"
Unidad intercambiable que contiene la batería y el circuito de carga.
- **Batería**: LiPo (850, 1200, o 2800mAh) en una bolsa ignífuga.
- **Carga**: Circuito BQ24040 con puerto **USB-C IP68**.
- **Conexión**: 4 Pogo Pins de oro que se acoplan a los pads del Módulo Cerebro.

### 2.3. Mecanismo de Unión
Un **raíl deslizante** y un **O-Ring de compresión** aseguran una conexión mecánica robusta y un sellado hermético IP68.

## 3. Lógica de Inteligencia (Back-end)

- **Filtro Kalman Predictivo**: Usa los datos del BMI270 para predecir la ruta durante pérdidas de señal GPS, asegurando una línea de mapa continua.
- **Localización Híbrida**: Combina 4 niveles (GNSS, Kalman, CELL-ID, WiFi AP) para maximizar la cobertura.
- **Endpoint de Ingesta**: `POST /v1/iot/ingest`.

## 4. Experiencia de Usuario

- **Cambio de Batería en 2 Segundos**: Permite tener múltiples "Power Packs" cargando y listos para usar.
- **Carga Independiente**: El módulo principal nunca queda fuera de servicio durante la carga.

---

_Este documento es el Single Source of Truth para ARES v3.6._
