# Base de Conocimiento Canina — MVP (GPS + Nutrición + Ejercicio) · v0.1

> Documento vivo con los datos mínimos y reglas que la app necesita para funcionar bien desde el día 1. Estructurado por bloques (nutrición, ejercicio, condición corporal, clima/seguridad y GPS), listo para convertir en tablas de BD y lógica de negocio.

---

## A) Nutrición canina (completo)

### A.1 Fórmulas base (energía)
- **RER (kcal/día)**: `RER = 70 × (peso_kg ^ 0.75)`  
  (Aproximación rápida útil 2–45 kg: `RER ≈ 30 × peso_kg + 70`).
- **DER (mantenimiento)**: `DER = RER × factor_estado`.
- **Factores de estado (tabla de referencia)**  
  Adulto entero (1.8), Adulto esterilizado (1.6), Obeso propenso (1.3–1.4), Cachorro <4 m (3.0), Cachorro ≥4 m (2.0), Trabajo ligero (2.0), Trabajo intenso (5.0).  
  *(Se ajustarán por individuo ±20–30% según respuesta de peso/BCS.)*

### A.2 Requisitos nutricionales mínimos (tabla NutrientesMinimos)
- **Campos propuestos**: etapa (adulto / cachorro-reproducción), proteina_min_pctMS, grasa_min_pctMS, fibra_recomendada, humedad_ref, energía_densidad_kcal_100g, Ca_min, P_min, Ca_P_ratio, Na_min, K_min, Mg_min, EPA_DHA_objetivo_mg_kcal (opcional), vitaminas (A, D, E, complejo B) y trazas (Fe, Zn, Cu, Mn, Se, I).  
- **Uso en app**: validar dietas caseras / educativas; mostrar alertas si una dieta propuesta no cumple mínimos.

### A.3 Tipos de dieta y metadatos (tabla Dietas)
- **Tipos**: pienso seco, húmeda, mixta, casera cocida, BARF/CRUDA controlada, terapéutica (renal, hepática, hipocalórica, dermatológica, gastrointestinal, diabética, articular).
- **Campos**: nombre, marca (si aplica), kcal_por_100g, proteína %, grasa %, fibra %, humedad %, Ca, P, cenizas, etiqueta/claim, *etapa apropiada* (cachorro/adulto/senior), *objetivo clínico*.
- **Notas**: para caseras, guardar **receta**: ingredientes (g), cocción, suplementos (Ca, omega‑3), rinde total, ración por kg/día; marcar **aprobado por vet**.

### A.4 Lista de alimentos **permitidos**, **con moderación** y **prohibidos/tóxicos**
**A.4.1 Permitidos (generales, salvo alergias/condiciones)**  
Carnes magras cocidas (pollo, pavo, ternera), vísceras bien racionadas (hígado 1–2×/sem), pescado cocido y desespinado (ojo con espinas/mercurio), huevo cocido, arroz/pasta bien cocidos, patata **cocida** sin piel verde, calabaza, zanahoria, judía verde, calabacín, manzana/pera **sin semillas**, plátano, yogur natural sin azúcar (si tolera lactosa), aceite de pescado (EPA/DHA), aceite de oliva (pequeñas cantidades), pienso/húmeda comerciales **completas** para su etapa.

**A.4.2 Con moderación / bajo supervisión**  
Quesos poco curados (sodio/lactosa), pan simple/avena (calorías vacías), mantequilla de cacahuete **sin xilitol**, frutas azucaradas (mango/sandía sin semillas), verduras flatulentas (brócoli/coliflor cocidos), frutas secas **no uvas/pasas**, snacks comerciales **bajos en sal**.

**A.4.3 **Prohibidos / tóxicos** (tabla AlimentosToxicos)**  
Chocolate/cacao (teobromina), uvas y pasas, **xilitol** (chicles, cremas de cacahuete y “sin azúcar”), cebolla/ajo/cebollino/puerro, alcohol, cafeína/teína, masa de pan cruda (fermentación/etanol), huesos cocidos astillables, aguacate (persina, riesgo GI), nuez de macadamia, nuez moscada, edulcorantes varios, sal en exceso, setas desconocidas, patata verde o brotada, tomate verde y hojas, semillas/pepitas de frutas (cianogénicos), comidas muy saladas/condimentadas (jamón, embutidos), lácteos azucarados, uvas, pasas, edulcorantes “sin azúcar”, medicamentos humanos (ibuprofeno, paracetamol, etc.).  
**Campos por alimento**: compuesto_toxico, *dosis_toxica* si conocida, síntomas, **primeros auxilios** (p.ej., contacto veterinario inmediato; *no* inducir vómito salvo indicación; anotar cantidad/tiempo).

> **Regla de alertas**: si el usuario registra o fotografía un alimento de la lista negra → **alerta roja** + guía de acción y botón “llamar a mi vet” + “ver clínica 24/7 cercana”.

### A.5 Agua e hidratación
- Recomendación base: **~50–60 ml/kg/día** (más con calor/ejercicio, menos si dieta húmeda).  
- Añadir meta_hidratación y recordatorios contextuales con clima/actividad.

### A.6 Registro de comidas (tabla ConsumoDiario)
- **Campos**: perro_id, fecha_hora, alimento_id/receta_id, cantidad_g/ml, kcal_est, macronutrientes_est, notas, foto_uri, *fuente_estimación* (etiqueta/IA/manual), “apetito” (escala), “síntomas GI 24h”.
- **Reglas**: sumar **kcal_ingesta** del día, comparar con **kcal_objetivo** (de PerfilPerro) y con **kcal_gastadas** (ActividadDiaria) → estado **balance/deficit/superavit**.

### A.7 IA opcional (on‑device)
- **Clasificador de comida** en móvil (TensorFlow Lite/CoreML) para sugerir alimento y porción; siempre editable por el usuario.  
- **Privacidad**: todo en local; subir sólo si el usuario activa copia en nube.

---

## B) Actividad y ejercicio

### B.1 Niveles por edad, tamaño y BCS (tabla NivelActividad)
- **Baja**: senior/sedentario o BCS alto. Objetivo: **20–40 min** paseo suave/día, distancia 1–3 km, pausas.
- **Moderada**: adulto sano. Objetivo: **45–90 min** totales (paseos + juego), 3–6 km.
- **Alta**: razas activas/trabajo. Objetivo: **90–150 min**, 6–12 km, incluir estímulo mental.
- Añadir **variantes por tamaño** (toy/pequeño/mediano/grande/gigante) y **banderas** (braquicéfalo, artrosis, cachorro) para ajustar tiempos.

### B.2 Gasto calórico por ejercicio
- Regla práctica por distancia: **kcal ≈ 1.0 × peso_kg × distancia_km** (andar/trotar).  
- Intensidad alta: **≈ 1.3–1.5 ×** peso × km como corrección.

### B.3 Reglas de recomendación diaria
- Combinar clima + historial de actividad + perfil para proponer plan del día (duración, horas seguras, superficie recomendada, agua mínima a llevar).
- Objetivos semanales con **progresión** (+10%/sem si busca mejorar condición).

### B.4 Restricciones por condición/edad
- **Cachorros**: evitar saltos prolongados; bloques cortos y frecuentes.  
- **Senior/artrosis**: superficies blandas, sesiones cortas + calentamiento.  
- **Braquicéfalos**: limitar esfuerzo con calor; paseos muy tempranos o tardíos.

---

## C) Condición corporal (IMC + BCS)
- **IMC por raza y sexo** con rangos bajo/ideal/sobrepeso.  
- **BCS 1–9** con descripciones, % grasa estimado y **peso_relativo** para calcular **peso_ideal** desde el peso actual.  
- **Reglas**: si BCS ≥7 → activar **modo adelgazamiento** (DER × 0.8–0.9, subir NEAT, metas semanales de −1% peso). Si BCS ≤3 → alerta y recomendación vet.

---

## D) Clima y seguridad

### D.1 Umbrales térmicos y contexto
- **Riesgo por calor** (depende de tamaño/raza): advertencias desde **25–29 °C**; peligro con humedad alta y sol directo; pavimento caliente (test de 5 s con dorso de mano).
- **Riesgo por frío**: considerar viento/lluvia/tamaño; abrigos para toy/pequeños.
- **Altas PM2.5/ozono**: evitar alta intensidad; *placeholder para futura integración de calidad del aire*.

### D.2 Reglas de alerta
- Si `temp_ext > umbral_raza` **o** `índice_calor alto` → sugerir horas seguras, agua extra, rutas sombreadas.  
- Si superficie = asfalto y `temp_suelo` estimada alta → recomendar césped/tierra o botas.

---

## E) GPS y geo‑vallas (GF‑07)
- **Comandos clave**: 000 (vincular), 777 (ubicación), 888 (estado), 666 (alarma sonido), 555 (audio SD), 445 (borrar SD), 999 (reinicio), *#*#*# (fábrica), `imei#` (IMEI).
- **Lógica**: leer SMS → parsear coords/batería → evaluar **geo‑vallas** (círculo/polígono, con tolerancia) → **notificar**.  
- **Frecuencias**: modos intensivo/normal/ahorro; estimar **autonomía** según consulta cada X s/min.
- **Mapas**: OSM por defecto; opcional Google Maps con límites gratuitos; cacheo de tiles.

---

## F) Salud preventiva y “primeros auxilios” (educativo)
- **Calendario**: core (moquillo, parvo, hepatitis, rabia según normativa local), desparasitaciones (endo/ecto), chequeo dental. *(Cargar por país/región en versiones futuras.)*
- **Señales de alarma**: vómito persistente, diarrea con sangre, letargia, golpe de calor (jadeo extremo, encías rojas/pálidas), cojera aguda.  
- **Protocolo tóxicos**: identificar alimento, tiempo y cantidad; **contactar vet**; no administrar remedios caseros sin indicación.

---

## G) Estructura de BD (tablas y campos mínimos)

1. **Razas**: nombre, tamaño, alturas por sexo, rangos IMC por sexo, braquicéfalo?, longevidad (opt).  
2. **CategoriasTamano**: peso_aprox_min/max, FC_reposo, FR_reposo, temp_normal_min/max, umbral_calor, umbral_frio.  
3. **BCS**: score 1–9, descripción, %grasa, peso_relativo%
4. **NivelActividad**: nivel (baja/moderada/alta), min_moderado, min_vigoroso, distancia_ref_km.
5. **FactoresEnergeticos**: condicion, factor_RER.
6. **NutrientesMinimos**: etapa, proteína_min%, grasa_min%, Ca, P, Ca:P, Na, K, Mg, vitaminas/oligoelementos.
7. **AlimentosToxicos**: alimento, compuesto_toxico, dosis_toxica, síntomas, acciones.
8. **Dietas**: tipo, nombre/marca, kcal_100g, macros/minerales/vitam, etapa, objetivo_clínico.
9. **PerfilPerro**: raza_id, sexo, fecha_nac, peso_actual, BCS_actual, objetivo_peso, nivel_actividad, flags (esterilizado, patologías), **calorias_objetivo**.
10. **PesoHistorial**: perro_id, fecha, peso, BCS.
11. **ActividadDiaria**: perro_id, fecha, min_mod, min_vig, distancia_km, kcal_quemadas.
12. **ConsumoDiario**: perro_id, fecha, kcal_ingesta, agua_ml, alimentos (relación), notas.
13. **GeoValla**: perro_id, nombre, tipo (círculo/polígono), coords, tolerancia_m, activo.
14. **Eventos**: perro_id, fecha_hora, tipo (salida_geovalla, batería_baja, calor_ext…), payload.

---

## H) Reglas de decisión (MVP)

1. **Cálculo kcal_objetivo**  
   a) RER desde peso_actual **o** desde **peso_ideal** si BCS ≥6.  
   b) Multiplicar por factor de **FactoresEnergeticos**.  
   c) Si **modo adelgazamiento**: multiplicar por 0.8–0.9.  
   d) Autocalibración semanal: si peso baja/sube >1%/semana fuera del plan → ajustar ±5–10%.

2. **Gasto ejercicio**  
   `kcal = 1.0 × kg × km` (ajuste intensidad).

3. **Alertas clima**  
   Si `temp > umbral_calor_tamaño` **o** braquicéfalo con `>25 °C` → alertas, sugerencias horarias y agua.

4. **Geo‑valla**  
   Salida confirmada tras **2 lecturas consecutivas** fuera del polígono (para evitar falsos positivos). Cooldown de notificación configurable (p.ej., 3–5 min).

5. **Tóxicos**  
   Al registrar alimento incluido en AlimentosToxicos → alerta inmediata con pasos y teléfono del vet.

---

## I) Pendientes para versión “completa”
- Poblar **NutrientesMinimos** con tablas AAFCO/NRC vigentes.
- Cargar **IMC por raza** completo (todas las razas; ya hay estructura).
- Catálogo base de **marcas/dietas** populares en ES/EU con kcal/100g y composición.
- Integrar **calidad del aire** y **índice UV** para recomendaciones.
- Tabla **Clínicas 24/7** por provincia (ES) y botón de emergencia.
- Modelo IA de comidas (dataset curado) + “modo educativo” con ingredientes alternativos seguros.

---

## J) Glosario rápido
- **RER**: energía de reposo; **DER**: energía diaria (mantenimiento).
- **BCS**: Body Condition Score (1–9).
- **Braquicéfalo**: razas de hocico chato (p.ej., Bulldog Francés).
- **IMC**: índice masa corporal; aquí, calibrado por raza/sexo.

---

### Notas finales
Este documento está preparado para convertirse tal cual en esquema de BD y reglas de negocio. Si lo aprobamos, el siguiente paso es: (1) generar las tablas con valores semilla, (2) escribir los **servicios** de cálculo (kcal objetivo, gasto, alertas) y (3) conectar el **módulo GPS** con las geo‑vallas y notificaciones.

