/* ============================================
   ARES GPS — Motor de calculo de la Calculadora de Peso Ideal
   Fuente de la logica: ARES_Estrategia_Contenido_Comunidad_v1.md §4.2
   Datos reales: docs/combers/IMC_por_raza__seed_v1_.csv (160 razas)
                 docs/combers/bmi_simple_bands_v1.csv (bandas por tamano)
   Los datos ya vienen embebidos en breed-data.js (window.ARES_BREED_DATA)
   para poder abrir esta pagina con file:// sin servidor ni fetch/CORS.
   ============================================ */

(function () {
  const PUPPY_THRESHOLD_MONTHS = 12; // umbral cachorro, ver §4.2 punto 3

  function getData() {
    return window.ARES_BREED_DATA || { breeds: [], bands: [], sizeFallback: {}, breedNames: [] };
  }

  /**
   * Busca la fila exacta de IMC_por_raza para breed+sex.
   * Si no hay fila para el sexo exacto, intenta "U" (unisex) como fallback.
   */
  function findBreedRow(breed, sex) {
    const { breeds } = getData();
    let row = breeds.find((b) => b.breed === breed && b.sex === sex);
    if (!row) row = breeds.find((b) => b.breed === breed && b.sex === "U");
    return row || null;
  }

  /**
   * Busca la fila de bandas simplificadas (bmi_simple_bands) para breed+sex.
   */
  function findBandRow(breed, sex) {
    const { bands } = getData();
    let row = bands.find((b) => b.breed === breed && b.sex === sex);
    if (!row) row = bands.find((b) => b.breed === breed && b.sex === "U");
    return row || null;
  }

  /**
   * Estima categoria de tamano aproximada a partir de peso (kg), para el caso
   * "Mestizo / No se" sin raza conocida — mapeo simple y conservador.
   */
  function estimateSizeCategory(weightKg) {
    if (weightKg <= 5) return "toy";
    if (weightKg <= 10) return "small";
    if (weightKg <= 25) return "medium";
    if (weightKg <= 40) return "large";
    return "giant";
  }

  function isPuppy(ageMonths) {
    return typeof ageMonths === "number" && ageMonths > 0 && ageMonths < PUPPY_THRESHOLD_MONTHS;
  }

  /**
   * Clasifica un valor de IMC contra una banda con 4 categorias:
   * Bajo peso / Ideal / Sobrepeso / Obesidad
   */
  function classify(bmi, normalMin, normalMax, overweightStart, obesityStart) {
    if (bmi < normalMin) return "bajo_peso";
    if (bmi <= normalMax) return "ideal";
    if (bmi < obesityStart) return "sobrepeso";
    return "obesidad";
  }

  /**
   * Calcula las bandas (normalMin/normalMax/overweightStart/obesityStart) para
   * UNA sola raza, sin decidir todavia la categoria final. Se usa tanto para el
   * caso de 1 raza como para promediar cuando hay 2 razas (mestizo de 2 razas
   * conocidas, punto 6). Devuelve null si la raza no se reconoce.
   */
  function resolveBandsForBreed(breed, sex, puppy) {
    const row = findBreedRow(breed, sex);
    if (row) {
      let normalMin = row.imc_normal_min;
      let normalMax = row.imc_normal_max;
      const overweightStart = row.imc_overweight_start;
      const obesityStart = row.imc_obesity_start;

      const bandRow = findBandRow(breed, sex);
      if (puppy && bandRow) {
        normalMin = bandRow.puppy_adj_min;
        normalMax = bandRow.puppy_adj_max;
      }

      return {
        normalMin,
        normalMax,
        overweightStart,
        obesityStart,
        breedUsed: row.breed,
        sizeCategory: row.size_category,
        puppyAdjusted: puppy && !!bandRow,
        source: "imc_por_raza",
      };
    }

    // Fallback: bandas simplificadas por raza (si la raza esta ahi pero no en el CSV principal)
    const bandRow = findBandRow(breed, sex);
    if (bandRow) {
      let normalMin = bandRow.bmi_ideal_min;
      let normalMax = bandRow.bmi_ideal_max;
      if (puppy) {
        normalMin = bandRow.puppy_adj_min;
        normalMax = bandRow.puppy_adj_max;
      }
      const obesityStart = normalMax * 1.15;
      return {
        normalMin,
        normalMax,
        overweightStart: normalMax,
        obesityStart,
        breedUsed: bandRow.breed || "tu perro (por tamaño estimado)",
        sizeCategory: bandRow.category_simple,
        puppyAdjusted: puppy,
        source: "bmi_simple_bands",
      };
    }

    return null;
  }

  /**
   * Rangos aproximados predefinidos para quien no tiene bascula/metro a mano
   * (cambio: alternativa de precision para peso/altura). El motor toma el
   * punto medio del rango como valor de entrada al calculo, pero el resultado
   * queda marcado con approxInput=true para que la UI amplie el margen de
   * error mostrado -- ver isApprox mas abajo y el bloque de "menor precision"
   * en calculadora.html.
   */
  const WEIGHT_RANGES = [
    { id: "w1", label: "Menos de 5 kg", min: 0.5, max: 5 },
    { id: "w2", label: "5 - 10 kg", min: 5, max: 10 },
    { id: "w3", label: "10 - 20 kg", min: 10, max: 20 },
    { id: "w4", label: "20 - 30 kg", min: 20, max: 30 },
    { id: "w5", label: "30 - 40 kg", min: 30, max: 40 },
    { id: "w6", label: "Más de 40 kg", min: 40, max: 55 },
  ];

  const HEIGHT_RANGES = [
    { id: "h1", label: "Menos de 20 cm", min: 10, max: 20 },
    { id: "h2", label: "20 - 35 cm", min: 20, max: 35 },
    { id: "h3", label: "35 - 50 cm", min: 35, max: 50 },
    { id: "h4", label: "50 - 65 cm", min: 50, max: 65 },
    { id: "h5", label: "Más de 65 cm", min: 65, max: 90 },
  ];

  function midpoint(range) {
    return round1((range.min + range.max) / 2);
  }

  /**
   * Resuelve un valor de entrada (peso o altura) que puede venir como cifra
   * exacta (number) o como rango aproximado ({ rangeId }). Devuelve el valor
   * numerico a usar en el calculo + si el origen fue aproximado.
   */
  function resolveInputValue(rawValue, rangeList) {
    if (rawValue && typeof rawValue === "object" && rawValue.rangeId) {
      const range = rangeList.find((r) => r.id === rawValue.rangeId);
      if (range) return { value: midpoint(range), isApprox: true };
    }
    const num = typeof rawValue === "object" ? NaN : parseFloat(rawValue);
    return { value: num, isApprox: false };
  }

  /**
   * Calcula el resultado de la calculadora.
   * @param {Object} input
   * @param {string|string[]} input.breed - nombre de raza, "mestizo", o un array
   *   de 1-2 nombres de raza (mestizo de dos razas conocidas, punto 6). Se
   *   mantiene compatibilidad con el input historico de string unico.
   * @param {string} input.sex - "F" | "M" | "U"
   * @param {number|{rangeId:string}} input.weightKg - cifra exacta en kg, o
   *   { rangeId } de WEIGHT_RANGES si el usuario eligio un rango aproximado.
   * @param {number|{rangeId:string}} input.heightCm - cifra exacta en cm, o
   *   { rangeId } de HEIGHT_RANGES si el usuario eligio un rango aproximado.
   * @param {number} input.ageMonths
   * @returns {Object} resultado con categoria, bmi, banda usada, fuente de
   *   datos y approxInput (true si peso y/o altura vinieron de un rango, no
   *   de una cifra exacta -- la UI debe mostrar un margen de error ampliado).
   */
  function calculate(input) {
    const { sex, ageMonths } = input;
    const weightResolved = resolveInputValue(input.weightKg, WEIGHT_RANGES);
    const heightResolved = resolveInputValue(input.heightCm, HEIGHT_RANGES);
    const weightKg = weightResolved.value;
    const heightCm = heightResolved.value;
    const approxInput = weightResolved.isApprox || heightResolved.isApprox;
    const heightM = heightCm / 100;
    const bmi = weightKg / (heightM * heightM);
    const puppy = isPuppy(ageMonths);

    // Normaliza input.breed a un array de 1 o 2 razas reales (sin "mestizo"/vacios)
    const rawBreeds = Array.isArray(input.breed) ? input.breed : [input.breed];
    const realBreeds = rawBreeds
      .map((b) => (b || "").trim())
      .filter((b) => b && !/^mestizo$/i.test(b) && !/no s[ée]/i.test(b));

    if (realBreeds.length > 0) {
      const resolved = realBreeds.map((b) => resolveBandsForBreed(b, sex, puppy)).filter(Boolean);

      if (resolved.length === 1) {
        const r = resolved[0];
        const category = classify(bmi, r.normalMin, r.normalMax, r.overweightStart, r.obesityStart);
        return {
          bmi: round1(bmi),
          category,
          normalMin: round1(r.normalMin),
          normalMax: round1(r.normalMax),
          source: r.source,
          breedUsed: r.breedUsed,
          sizeCategory: r.sizeCategory,
          puppyAdjusted: r.puppyAdjusted,
          approxInput,
        };
      }

      if (resolved.length === 2) {
        // Mestizo de 2 razas conocidas: se promedian las bandas de ambas razas
        // (normal_min/max, overweight_start, obesity_start) en vez de usar solo
        // una — logica confirmada explicitamente para este caso.
        const avg = (key) => (resolved[0][key] + resolved[1][key]) / 2;
        const normalMin = avg("normalMin");
        const normalMax = avg("normalMax");
        const overweightStart = avg("overweightStart");
        const obesityStart = avg("obesityStart");
        const category = classify(bmi, normalMin, normalMax, overweightStart, obesityStart);
        return {
          bmi: round1(bmi),
          category,
          normalMin: round1(normalMin),
          normalMax: round1(normalMax),
          source: "promedio_2_razas",
          breedUsed: resolved.map((r) => r.breedUsed).join(" x "),
          sizeCategory: resolved[0].sizeCategory,
          puppyAdjusted: resolved[0].puppyAdjusted || resolved[1].puppyAdjusted,
          approxInput,
        };
      }
      // Si ninguna de las razas indicadas se reconoce, cae al fallback por tamano de abajo.
    }

    // Fallback final: mestizo o raza(s) desconocida(s) -> categoria de tamano aproximada
    // por peso. Se promedian todas las bandas de esa categoria de tamano (no se usa una
    // raza al azar, que daria un "breedUsed" enganoso para un perro mestizo).
    const sizeCat = estimateSizeCategory(weightKg);
    const fallbackCategory = getData().sizeFallback[sizeCat] || "medium_general";
    const { bands } = getData();
    const matchingBands = bands.filter((b) => b.category_simple === fallbackCategory);

    if (matchingBands.length > 0) {
      const avgBand = averageBands(matchingBands);
      return resultFromBand(bmi, avgBand, puppy, sizeCat, approxInput);
    }

    // Si ni siquiera hay banda generica (no deberia pasar), devolvemos solo el BMI
    return {
      bmi: round1(bmi),
      category: "ideal",
      normalMin: null,
      normalMax: null,
      source: "sin_datos",
      breedUsed: realBreeds.join(" x ") || "Mestizo/No sé",
      sizeCategory: sizeCat,
      puppyAdjusted: false,
      approxInput,
    };
  }

  /**
   * Promedia varias filas de bmi_simple_bands que comparten category_simple,
   * para usar como banda generica del tamano cuando no se conoce la raza.
   */
  function averageBands(rows) {
    const avg = (key) => rows.reduce((sum, r) => sum + r[key], 0) / rows.length;
    return {
      breed: null,
      sex: "U",
      category_simple: rows[0].category_simple,
      bmi_ideal_min: avg("bmi_ideal_min"),
      bmi_ideal_max: avg("bmi_ideal_max"),
      puppy_adj_min: avg("puppy_adj_min"),
      puppy_adj_max: avg("puppy_adj_max"),
    };
  }

  function resultFromBand(bmi, bandRow, puppy, sizeCatOverride, approxInput) {
    let normalMin = bandRow.bmi_ideal_min;
    let normalMax = bandRow.bmi_ideal_max;
    if (puppy) {
      normalMin = bandRow.puppy_adj_min;
      normalMax = bandRow.puppy_adj_max;
    }
    // Bandas simplificadas no traen umbral de obesidad explicito -> se estima
    // como +15% sobre el limite superior de la banda ideal (regla conservadora,
    // documentada aqui porque no viene en el CSV secundario).
    const obesityStart = normalMax * 1.15;
    const category = classify(bmi, normalMin, normalMax, normalMax, obesityStart);
    return {
      bmi: round1(bmi),
      category,
      normalMin: round1(normalMin),
      normalMax: round1(normalMax),
      source: "bmi_simple_bands",
      breedUsed: bandRow.breed || "tu perro (por tamaño estimado)",
      sizeCategory: sizeCatOverride || bandRow.category_simple,
      puppyAdjusted: puppy,
      approxInput: !!approxInput,
    };
  }

  function round1(n) {
    return Math.round(n * 10) / 10;
  }

  const CATEGORY_LABELS = {
    bajo_peso: "Bajo peso",
    ideal: "Ideal",
    sobrepeso: "Sobrepeso",
    obesidad: "Obesidad",
  };

  const CATEGORY_MESSAGES = {
    bajo_peso:
      "Tu perro está por debajo de su rango de peso estimado. Esto es una estimación, no un diagnóstico — consulta con tu veterinario sobre su alimentación.",
    ideal:
      "Tu perro está en su peso estimado para su raza y tamaño. Mantén su rutina actual de alimentación y ejercicio.",
    sobrepeso:
      "Tu perro tiene sobrepeso estimado para su raza y tamaño. Consulta con tu veterinario sobre un plan de ajuste — esto es una estimación, no un diagnóstico.",
    obesidad:
      "Tu perro está en un rango de obesidad estimado. Te recomendamos hablar con tu veterinario cuanto antes — esto es una estimación, no un diagnóstico médico.",
  };

  window.ARES_CALCULATOR = {
    calculate,
    getData,
    CATEGORY_LABELS,
    CATEGORY_MESSAGES,
    isPuppy,
    WEIGHT_RANGES,
    HEIGHT_RANGES,
  };
})();
