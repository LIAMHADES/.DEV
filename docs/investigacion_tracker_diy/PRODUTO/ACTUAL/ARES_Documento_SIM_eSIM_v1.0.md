# ARES — Documento SIM / eSIM (Decisión Nano-SIM prototipo + MFF2 venta) v1.0

## 1) Objetivo y decisión

**Objetivo:** conectividad fiable, simple de operar, coste controlable por dispositivo y control total desde nuestro backend (alta/baja, consumo, diagnóstico).

**Decisión operativa (ya tomada):**

*   **Prototipos / primeras unidades:** **Nano-SIM (4FF)** con conector físico (rápido, barato, sin MOQs raros, fácil de testear).
*   **Versión de venta (cuando escalemos):** migrar a **SIM soldada MFF2 (embedded “eSIM” física)** para ahorrar espacio, aumentar robustez y evitar manipulación.

Motivo clave del cambio: para soldar MFF2 en PCBA necesitas logística de suministro/ensamble más “industrial” (reels, consignación, etc.). Ejemplo real: el **“1NCE IoT SIM Chip”** aparece en el catálogo de PCBA de JLCPCB, pero figura **sin stock y con mínimo 447** (y “full reel 3000”), aunque permite **consignación** para ensamblar si tú aportas la pieza. ([jlcpcb.com][1])

---

## 2) Empresa elegida (nombre) y qué significa “para siempre”

**Empresa (la que más encaja por tu criterio de simplicidad + control):** **1NCE**.
Tiene modelo **pay-as-you-go** para datos altos: **5 €/GB + 12 € de alta (una vez)**, con precio global y uso en **170+ países/regiones**. ([1nce.com][2])

¿“Para siempre”? En IoT, “para siempre” real no existe: depende de proveedor, acuerdos de roaming y continuidad del servicio. Lo que sí puedes controlar tú:

*   **Activar/desactivar SIMs desde tu plataforma** (portal o API) para cortar servicio cuando el usuario no paga o da de baja. ([1NCE Developer Hub][3])

---

## 3) Cómo se comunica el dispositivo (servidores y teléfono)

### 3.1 Flujo de datos (lo normal en trackers)

1.  **Dispositivo (SIM7000G) → red móvil → proveedor IoT → Internet breakout → tu backend**

    *   Protocolos típicos: **HTTPS** o **MQTT** (con TLS).
2.  **App móvil → tu backend** (internet normal del teléfono).
3.  **Dispositivo ↔ teléfono** (opcional, corto alcance) por **BLE** para: alta rápida, diagnóstico local, emparejado, etc. (pero el tracking en campo va por móvil).

### 3.2 Identidad / “a qué usuario mando los datos”

No necesitas “1 SIM para varios dispositivos” (eso no funciona operativamente: **cada dispositivo que transmite necesita su propia suscripción/SIM**). Lo que sí haces es:

*   Cada dispositivo lleva un **DeviceID** (serial/UUID) en el payload.
*   En tu backend mapeas **DeviceID → Usuario → plan → reglas**.

---

## 4) Coste mensual estimado con tu hipótesis (0,25 GB/mes) y comparativa

Tipo de cambio usado para convertir USD→EUR: **ECB 15-ene-2026: 1 EUR = 1,1624 USD** (≈ **1 USD = 0,8603 EUR**). ([European Central Bank][4])

### 4.1 Coste “1 dispositivo, 0,25 GB/mes (250 MB)”

| Proveedor | Formato | Cómo cobra | Coste aprox 250MB/mes (1 SIM) | Encaje |
| --- | --- | --- | --- | --- |
| **1NCE (High Data IoT)** | SIM física / (MFF2 posible) | **5 €/GB + 12 € alta 1 vez** ([1nce.com][2]) | **≈ 1,25 €/mes** + **12 €** one-time | **Muy bueno** para empezar (sin cuota fija mensual) |
| **Telnyx** | SIM + **MFF2** + **eSIM OTA** ([Telnyx Centro de Ayuda][5]) | **$2/mes SIM activa** + datos por **zonas** y por **tiers** ([Telnyx Centro de Ayuda][6]) | En low-volume puede ser muy caro: ejemplo Tier1/2: **$15,65/mes ≈ 13,46 €/mes** ([Telnyx][7]) | Bueno cuando ya tienes **flota** y optimizas tiers/zonas; flojo para 1 SIM |
| **Simbase (España/Europa)** | Nano / MFF2 “a petición” ([Simbase Centro de Ayuda][8]) | **0,005 €/MB** + **0,01 €/día** por SIM activa ([SimBase][9]) | **≈ 1,55 €/mes** (1,25€ datos + ~0,30€ daily fee) | **Top** si quieres plan “España/UE” barato |
| **Hologram** | SIM / eUICC | **$0,03/MB + $1/mes** ([Hologram][10]) | **$8,50 ≈ 7,31 €/mes** ([Hologram][10]) | Más caro para tu consumo |
| **Onomondo** | eSIM / MFF2 | “starting at **€0,003/MB**” (normalmente negociado) ([Onomondo][11]) | **≈ 0,75 €/mes** (si aplicase ese rate) | Potencial al escalar; no es “plug&play self-serve” típico |

> Nota crítica sobre Telnyx: el **$0,0125/MB** es el rate de **tier alto (>5GB)**, no el de 1 SIM con 250MB. ([Telnyx][7])

### 4.2 Si algún mes subes a 1 GB

*   **1NCE High Data:** **≈ 5 €/mes** (1GB × 5€/GB) + alta one-time (12€). ([1nce.com][2])
*   **Simbase:** **≈ 5,30 €/mes** (5€ datos + ~0,30€ daily fee). ([SimBase][9])
*   **Telnyx (ejemplo Zone1 tiers):** puede irse a decenas €/mes si estás en tiers bajos (la estructura es por tramos). ([Telnyx][7])
*   **Hologram:** **$31 ≈ 26,67 €/mes**. ([Hologram][10])

---

## 5) Cómo ganan margen estas empresas (y cómo tú recortas precio)

### 5.1 Cómo suelen ganar margen

*   Compran **conectividad mayorista** a operadores (MNOs) y revenden como MVNO/IoT.
*   Te cobran:
    *   **Acceso mensual por SIM activa** (cubrir coste fijo + plataforma).
    *   **Datos con margen** (y a veces **por zonas** cuando el roaming cuesta más).
    *   Servicios extra: VPN, gateways privados, dashboards, etc.

### 5.2 Cómo recortar precio y mantener calidad (tu estrategia)

**Fase 0–1 (1–50 dispositivos):** manda la eficiencia a “operación simple”.

*   Elegir proveedor con **cero cuota fija** o cuota mínima: **1NCE High Data** ([1nce.com][2]) o **Simbase** para España/UE ([SimBase][9]).
*   Payload optimizado (binario/compacto), batching y backoff: reduces MB reales.

**Fase 2 (100–1.000):** empiezas a tener poder de compra.

*   **Pool de consumo** (cuenta agregada) + negociación por volumen.
*   Pides **pricing custom** (Telnyx lo contempla al escalar). ([Telnyx][12])
*   Consideras eSIM/eUICC solo si te aporta ROI (multi-perfil, cambios OTA).

---

## 6) Plan “España barato” vs “Global” (lo que pediste)

Sí, puedes ofrecer dos niveles, pero con matices:

### Opción A — 2 SKUs (lo más simple y fiable)

*   **SKU España/UE:** SIM tipo Simbase (barato en UE). ([SimBase][9])
*   **SKU Global:** 1NCE High Data (global sencillo). ([1nce.com][2])

Con Nano-SIM (prototipo) incluso es trivial: cambias SIM físicamente.

### Opción B — 1 SKU con eUICC multi-perfil (más complejo)

*   Requiere **eUICC real** y gestión de perfiles (no solo “MFF2 soldado”).
*   Más coste/operación; se justifica cuando el volumen y la logística lo piden.

---

## 7) Problemas típicos por opción (los reales en la práctica)

### 1NCE (High Data)

*   **One-time setup** por SIM (12€) ([1nce.com][2]): duele si haces muchas pruebas.
*   Si un día te vas a consumos altos constantes, pagas por GB (no es tarifa plana ilimitada).
*   Gestión: bien (API/portal para activar/desactivar). ([1NCE Developer Hub][3])

### Telnyx

*   **Coste fijo mensual por SIM activa ($2)** y **datos caros en tiers bajos**. ([Telnyx Centro de Ayuda][6])
*   Pricing por **zonas/tiers**: fácil de equivocarse si no vigilas MCC/roaming y el tramo de consumo. ([Telnyx Centro de Ayuda][6])
*   Punto fuerte: **estados de SIM (active/standby/disabled)** y control operativo sin penalizaciones extra por cambiar estado. ([Telnyx Centro de Ayuda][5])
*   Formatos: tiene SIM, MFF2 y eSIM OTA. ([Telnyx Centro de Ayuda][5])

### Simbase (España/UE)

*   Tiene **daily fee** por SIM activa (0,01€/día) ([SimBase][13]): si el dispositivo está activo siempre, lo asumes.
*   MFF2 disponible “a petición”. ([Simbase Centro de Ayuda][8])
*   Encaje fuerte para “no salen del país / UE”.

---

## 8) Implicación de diseño: plantilla PCB/carcasa (añadir al documento hardware)

### Prototipo (Nano-SIM)

Añadir al template:

*   **Footprint conector Nano-SIM**, keep-out mecánico, y ruta limpia de señales.
*   Impacto: **más espacio y sellado** (waterproof) más exigente.

### Venta (MFF2)

Añadir:

*   Footprint **MFF2** (soldado) y keep-out.
*   Plan logístico:
    *   Comprar MFF2 en lotes (p. ej. 100/500 en reel según packaging de 1NCE). ([1NCE Developer Hub][14])
    *   Ensamble en JLCPCB como **consign part** si no hay stock (y ojo al mínimo que aparece en su librería para ese chip). ([jlcpcb.com][1])

---

## 9) Conclusión (por qué Nano-SIM ahora y MFF2 después)

*   **Nano-SIM ahora**: te permite iterar hardware/firmware sin fricción y sin depender de MOQs/stock de chips embebidos.
*   **MFF2 después**: te da el producto “de verdad” (más compacto, robusto, anti-manipulación) cuando tenga sentido industrializar compras y PCBA.

Si quieres, te lo convierto en una **plantilla fija** (1 página) para meterla tal cual en el documento maestro de hardware/BOM: “Conectividad celular y estrategia SIM (REV-A Nano / REV-B MFF2)”.

[1]: https://jlcpcb.com/partdetail/JIALICHUANGSMT-1NCE_IoT_SIMChip/C9900143967?utm_source=chatgpt.com "1NCE IoT SIM Chip | JLCPCB Assembly | New Arrivals"
[2]: https://www.1nce.com/en-eu/1nce-connect/features/high-data-iot?utm_source=chatgpt.com "High Data IoT"
[3]: https://help.1nce.com/dev-hub/docs/portal-dashboard?utm_source=chatgpt.com "Dashboard"
[4]: https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/eurofxref-graph-usd.en.html?utm_source=chatgpt.com "US dollar (USD) - European Central Bank"
[5]: https://support.telnyx.com/en/articles/3270136-telnyx-global-sims-faqs?utm_source=chatgpt.com "Telnyx Global SIMs FAQs"
[6]: https://support.telnyx.com/en/articles/3296669-iot-sim-card-pricing "IoT SIM Card Pricing | Telnyx Help Center"
[7]: https://telnyx.com/pricing/iot-data-plans "IoT SIM Card & Data Plans and Pricing"
[8]: https://support.simbase.com/the-new-user/fundamentals/sim-cards?utm_source=chatgpt.com "SIM cards"
[9]: https://simbase.com/best-iot-sim-card/spain?utm_source=chatgpt.com "Best IoT SIM Card for Spain - full comparison"
[10]: https://www.hologram.io/pricing/?utm_source=chatgpt.com "IoT data plans & pricing"
[11]: https://onomondo.com/go/future-proof-esims-for-iot-m2m-embedded/?utm_source=chatgpt.com "Future-proof Embedded SIMs for IoT & M2M"
[12]: https://telnyx.com/pricing?utm_source=chatgpt.com "Pricing"
[13]: https://www.simbase.com/plans/eu/business?utm_source=chatgpt.com "The best IoT data rates with the Simbase Business Plan"
[14]: https://help.1nce.com/dev-hub/docs/sim-chips-iot-industrial?utm_source=chatgpt.com "IoT SIM Chip Industrial"