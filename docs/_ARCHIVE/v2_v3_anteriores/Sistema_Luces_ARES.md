Esta estrategia es la más robusta porque reconoce las limitaciones físicas de la batería sin intentar engañarlas con electrónica compleja (Boosters).

### Uso de mcd altos (Serie APTD)
Al usar LEDs de 30°/40°, estamos "inyectando" muchísima más luz en el plástico. Aunque el LED sea estrecho, el difusor esparcirá esos miles de milicandelas por toda la "L". Es como meter una linterna en una barra de hielo; brilla entera.

### Muro del 15%
A menos de 3.5V (aprox. 15%), el Verde y el Azul dejan de ser fiables. Bloquear la función "Encender Luz" protege la integridad del sistema.

### Luces Informativas
Mantener un pequeño destello rojo para "Batería Baja" o "Buscando GPS" por debajo del 15% es vital para que el usuario sepa que el dispositivo sigue vivo.

---

## 2. ¿Qué nos estamos dejando? (El "Checklist" final)

Para que el tema de las luces esté completamente cerrado, asegúrate de que tu diseñador de PCB y tu programador tengan esto en cuenta:

### A. El "Ghosting" (Encendidos Fantasma)
Los pines del ESP32-S3 pueden "flotar" durante el arranque. Si no ponemos una resistencia de 100k Ohm (Pull-down) en la puerta (gate) del MOSFET de cada canal, las luces podrían dar un fogonazo blanco al encender el collar o al reiniciarse. Queremos un arranque limpio.

### B. La Frecuencia del PWM
Si el PWM es muy lento (menos de 100Hz), el parpadeo se verá "a saltos" si el perro corre. Si es muy rápido, puede generar un leve silbido electrónico o interferir con el Bluetooth.

**Recomendación:** Configura el PWM a 1kHz - 4kHz. Es el estándar de oro para que la luz sea sólida como una roca al ojo humano y a la cámara del móvil.

### C. El balance de blancos (Calibración)
Como el Rojo brilla mucho más (700-1500 mcd) que el Azul (300-700 mcd), si pones los tres al 100%, el collar se verá Rosa/Naranja, no Blanco.

**Solución:** Debes definir en el código un "Factor de Corrección". Por ejemplo: Rojo al 60%, Verde al 90% y Azul al 100% para conseguir un Blanco puro.

---

## 3. Documento Final de Configuración: "SISTEMA LUCES ARES"

| Elemento | Especificación Final |
|---|---|
| **LEDs por lateral** | 6 (2 Rojos, 2 Verdes, 2 Azules) - Serie APTD (Alta Intensidad). |
| **Control** | 3 Canales PWM (R, G, B) vía MOSFETs low-side. |
| **Alimentación** | Directo a VBAT (3.0V - 4.2V). SIN BOOST. |
| **Lógica de App** | Función: "Encender Luz". |
| **Muro de Seguridad** | < 15% Batería: Bloqueo total de luz manual. |
| **Muro de Prioridad**| Apagado automático de luces durante ráfagas de envío de posición. |
| **Óptica** | Difusor de policarbonato mate + Cámara interna blanca reflectante. |
