/* ARES GPS - Orientacion nutricional publica.
   Reutiliza el perfil compartido de calculadora.html y actividad.html, pero no
   sustituye el calculo oficial del backend ni una pauta veterinaria. */
(function () {
  const form = document.getElementById('nutrition-planner-form');
  if (!form) return;

  const plannerPanel = document.getElementById('planner-panel');
  const plannerOpen = document.getElementById('planner-open');
  const plannerClose = document.getElementById('planner-close');
  const weightInput = document.getElementById('planner-weight');
  const ageInput = document.getElementById('planner-age');
  const ageUnitInput = document.getElementById('planner-age-unit');
  const goalInput = document.getElementById('planner-goal');
  const activityInput = document.getElementById('planner-activity');
  const foodTypeInput = document.getElementById('planner-food-type');
  const extraFoodInput = document.getElementById('planner-extra-food');
  const dryKcalInput = document.getElementById('planner-dry-kcal');
  const wetKcalInput = document.getElementById('planner-wet-kcal');
  const homeKcalInput = document.getElementById('planner-home-kcal');
  const densityFields = [...form.querySelectorAll('[data-food-density]')];
  const profileNote = document.getElementById('planner-profile-note');
  const emptyResult = document.querySelector('.planner-result-empty');
  const resultContent = document.querySelector('.planner-result-content');
  const kcalValue = document.getElementById('planner-kcal-value');
  const foodResult = document.getElementById('planner-food-result');
  const extraResult = document.getElementById('planner-extra-result');
  const sourceResult = document.getElementById('planner-source');
  const warningResult = document.getElementById('planner-warning');
  const activityLink = document.getElementById('planner-activity-link');
  const weightLink = document.getElementById('planner-weight-link');
  const saveAccountButton = document.getElementById('planner-save-account');

  let profile = window.ARES_BRIDGE ? window.ARES_BRIDGE.read() : null;
  let activity = profile && profile.activity ? profile.activity : null;

  const extraFoods = {
    apple: { label: 'Manzana sin semillas', kcalPer100g: 52, maxGramsPerKg: 4, note: 'Retira corazón y semillas.' },
    banana: { label: 'Plátano', kcalPer100g: 89, maxGramsPerKg: 2, note: 'Sin piel y en pocos trozos por su azúcar.' },
    orange: { label: 'Naranja', kcalPer100g: 47, maxGramsPerKg: 4, note: 'Solo pulpa; evita piel, semillas y zumo.' },
    mandarin: { label: 'Mandarina', kcalPer100g: 53, maxGramsPerKg: 4, note: 'Solo pulpa; introduce poca cantidad.' },
    blueberries: { label: 'Arándanos', kcalPer100g: 57, maxGramsPerKg: 2, note: 'Pocos y lavados, como premio ocasional.' },
    pumpkin: { label: 'Calabaza', kcalPer100g: 26, maxGramsPerKg: 8, note: 'Cocida y sin sal, azúcar ni especias.' },
    rice: { label: 'Arroz blanco cocido', kcalPer100g: 130, maxGramsPerKg: 8, note: 'Complemento medido, no base de la dieta.' },
    yogurt: { label: 'Yogur natural', kcalPer100g: 61, maxGramsPerKg: 4, note: 'Sin azúcar ni xilitol; retíralo si causa diarrea.' },
  };

  function numberOrNull(value) {
    const number = parseFloat(value);
    return Number.isFinite(number) ? number : null;
  }

  function formatNumber(value) {
    return Math.round(value).toLocaleString('es-ES');
  }

  function formatWeight(value) {
    return value.toLocaleString('es-ES', { maximumFractionDigits: 1 });
  }

  function ageInMonths() {
    const value = numberOrNull(ageInput.value);
    if (value == null) return null;
    return ageUnitInput.value === 'years' ? value * 12 : value;
  }

  function formatAge(months) {
    if (months == null) return '';
    if (months >= 24) {
      const years = months / 12;
      return Number.isInteger(years)
        ? years + ' años'
        : years.toLocaleString('es-ES', { maximumFractionDigits: 1 }) + ' años';
    }
    return Math.round(months) + ' meses';
  }

  function setAgeFromMonths(months) {
    if (months == null) return;
    const useYears = months >= 24 && months % 12 === 0;
    ageUnitInput.value = useYears ? 'years' : 'months';
    ageInput.value = useYears ? months / 12 : months;
    ageInput.max = useYears ? '20' : '240';
    ageInput.step = useYears ? '0.1' : '1';
  }

  function updateAgeUnit() {
    const months = ageInMonths();
    ageInput.max = ageUnitInput.value === 'years' ? '20' : '240';
    ageInput.step = ageUnitInput.value === 'years' ? '0.1' : '1';
    if (months != null) {
      ageInput.value = ageUnitInput.value === 'years' ? (months / 12).toFixed(1).replace(/\.0$/, '') : Math.round(months);
    }
  }

  function profileValue(key, fallback) {
    const value = profile && numberOrNull(profile[key]);
    return value == null ? fallback : value;
  }

  function hydrateProfile() {
    const latest = window.ARES_BRIDGE ? window.ARES_BRIDGE.read() : null;
    if (!latest) return;
    profile = latest;
    activity = profile.activity || null;
    if (numberOrNull(weightInput.value) == null) weightInput.value = profileValue('weightKg', '');
    if (numberOrNull(ageInput.value) == null) setAgeFromMonths(numberOrNull(profile.ageMonths));
    updateProfileNote();
  }

  function updateProfileNote() {
    const parts = [];
    if (profile && profile.breed) parts.push(profile.breed);
    if (profile && numberOrNull(profile.weightKg) != null) parts.push(formatWeight(numberOrNull(profile.weightKg)) + ' kg');
    if (profile && numberOrNull(profile.ageMonths) != null) parts.push(formatAge(numberOrNull(profile.ageMonths)));
    if (activity && numberOrNull(activity.minutes) != null) parts.push(Math.round(numberOrNull(activity.minutes)) + ' min de actividad');

    profileNote.textContent = parts.length
      ? 'Perfil detectado: ' + parts.join(' · ') + '. Puedes corregir los datos antes de calcular.'
      : 'No hay un perfil importado. Completa los datos mínimos para obtener una orientación.';
    profileNote.hidden = false;
  }

  function updateFoodInputs() {
    const type = foodTypeInput.value;
    densityFields.forEach((field) => {
      const visible = type === 'mixed'
        ? field.dataset.foodDensity === 'dry' || field.dataset.foodDensity === 'wet'
        : field.dataset.foodDensity === type;
      field.classList.toggle('visible', visible);
    });
  }

  function getActivityEstimate(weight, ageMonths) {
    const selected = activityInput.value;
    const profileMinutes = activity && numberOrNull(activity.minutes);
    const profileKcal = activity && numberOrNull(activity.kcal);
    const profileWeight = activity && numberOrNull(activity.weightKg);
    const profileDistance = activity && numberOrNull(activity.distanceKm);
    const rer = 70 * Math.pow(weight, 0.75);

    if (selected === 'auto' && profileKcal != null && profileKcal >= 0) {
      const weightRatio = profileWeight && profileWeight > 0 ? weight / profileWeight : 1;
      const adjustedActivityKcal = profileKcal * weightRatio;
      return {
        energy: rer + adjustedActivityKcal * 2,
        source: 'RER + el gasto de actividad importado (dos salidas como referencia)',
        actual: true,
      };
    }

    let factor = 1.6;
    let label = 'actividad moderada';
    if (selected === 'low') {
      factor = 1.4;
      label = 'actividad baja';
    } else if (selected === 'high') {
      factor = 1.9;
      label = 'actividad alta';
    } else if (selected === 'auto' && profileMinutes != null) {
      if (profileMinutes < 60) {
        factor = 1.4;
        label = 'actividad baja importada';
      } else if (profileMinutes > 120) {
        factor = 1.9;
        label = 'actividad alta importada';
      } else {
        label = 'actividad moderada importada';
      }
    }

    if (ageMonths < 12) {
      factor = 2.0;
      label = 'cachorro; factor de crecimiento';
    } else if (ageMonths >= 96) {
      factor = Math.min(factor, 1.3);
      label = 'senior; factor conservador';
    }

    return {
      energy: rer * factor,
      source: 'RER × ' + factor.toFixed(1) + ' (' + label + ')',
      actual: false,
      distance: profileDistance,
    };
  }

  function foodLines(dailyKcal) {
    const type = foodTypeInput.value;
    const dryKcal = numberOrNull(dryKcalInput.value);
    const wetKcal = numberOrNull(wetKcalInput.value);
    const homeKcal = numberOrNull(homeKcalInput.value);

    if (type === 'dry') {
      return dryKcal ? [{ label: 'Pienso seco', grams: dailyKcal * 100 / dryKcal }] : null;
    }
    if (type === 'wet') {
      return wetKcal ? [{ label: 'Comida húmeda', grams: dailyKcal * 100 / wetKcal }] : null;
    }
    if (type === 'mixed') {
      if (!dryKcal || !wetKcal) return null;
      return [
        { label: 'Pienso seco', grams: dailyKcal * 0.5 * 100 / dryKcal },
        { label: 'Comida húmeda', grams: dailyKcal * 0.5 * 100 / wetKcal },
      ];
    }
    if (type === 'home') {
      return homeKcal ? [{ label: 'Receta casera cocida', grams: dailyKcal * 100 / homeKcal }] : null;
    }
    return null;
  }

  function renderFood(lines) {
    if (!lines) {
      foodResult.innerHTML = '<strong>Falta la densidad energética</strong><br>Busca en la etiqueta las kcal por 100 g. Sin ese dato no podemos traducir la energía a gramos con sentido.';
      return;
    }
    foodResult.innerHTML = '<strong>Cantidad aproximada de alimento</strong><p class="food-help">Se obtiene dividiendo las kcal estimadas entre la densidad de tu alimento. Es una referencia, no una prescripción.</p>' + lines.map((line) =>
      '<div class="food-line"><span>' + line.label + '</span><span class="food-value">' + formatNumber(line.grams) + ' g/día</span></div>'
    ).join('');
  }

  function renderExtraPortion(dailyKcal, ageMonths, weight) {
    if (!extraResult) return;
    const food = extraFoods[extraFoodInput.value];
    if (!food) {
      extraResult.hidden = true;
      extraResult.innerHTML = '';
      return;
    }

    const goal = goalInput.value;
    const budgetRatio = ageMonths < 12 || ageMonths >= 96 || goal === 'lose' ? 0.03 : 0.05;
    const budgetKcal = dailyKcal * budgetRatio;
    const energyGrams = budgetKcal * 100 / food.kcalPer100g;
    const bodyCap = weight * food.maxGramsPerKg;
    const grams = Math.max(1, Math.min(energyGrams, bodyCap));
    const roundedGrams = Math.max(5, Math.round(grams / 5) * 5);

    extraResult.innerHTML = '<strong>Porción orientativa de ' + food.label.toLowerCase() + '</strong>'
      + '<div class="extra-meta">Hasta ' + formatNumber(roundedGrams) + ' g en un día como extra pequeño (' + Math.round(budgetKcal) + ' kcal aprox.). ' + food.note + ' Empieza por menos.</div>';
    extraResult.hidden = false;
  }

  function renderWarning(ageMonths) {
    const warnings = [];
    const goal = goalInput.value;
    const type = foodTypeInput.value;
    const category = profile && profile.category;

    if (ageMonths < 12) warnings.push('Es cachorro: el crecimiento requiere una dieta adecuada para su etapa y una revisión veterinaria.');
    if (ageMonths >= 96) warnings.push('Es senior: si hay pérdida de peso, apatía o cambios de apetito, consulta antes de ajustar la ración.');
    if (goal === 'lose') warnings.push('La pérdida de grasa debe ser gradual y controlada; no reduzcas más la ración sin revisar su peso y condición corporal.');
    if (goal === 'gain') warnings.push('Para ganar condición hay que descartar causas médicas y ajustar la dieta completa, no solo añadir calorías.');
    if (category === 'sobrepeso' || category === 'obesidad') warnings.push('La calculadora de peso indicó una desviación estimada: confirma el objetivo con tu veterinario.');
    if (type === 'home') warnings.push('La comida casera no es completa por defecto: la receta y los suplementos deben validarse profesionalmente.');
    if (extraFoodInput.value === 'banana') warnings.push('El plátano concentra más azúcar y calorías que otras opciones: usa la porción pequeña y no la sumes sin ajustar otros premios.');
    if (extraFoodInput.value === 'orange' || extraFoodInput.value === 'mandarin') warnings.push('Los cítricos pueden causar molestias digestivas: ofrece solo pulpa y suspende si aparecen síntomas.');
    if (extraFoodInput.value === 'yogurt') warnings.push('El yogur no es imprescindible y algunos perros no toleran bien la lactosa.');

    warningResult.textContent = warnings.join(' ');
    warningResult.hidden = warnings.length === 0;
  }

  function updateCrossLinks() {
    const currentAgeMonths = ageInMonths();
    const current = {
      ...(profile || {}),
      weightKg: numberOrNull(weightInput.value),
      ageMonths: currentAgeMonths,
      source: 'nutricion',
    };
    if (window.ARES_BRIDGE) {
      activityLink.href = 'actividad.html?' + window.ARES_BRIDGE.query(current, { source: 'nutricion' }).toString();
      weightLink.href = 'calculadora.html?' + window.ARES_BRIDGE.query(current, { source: 'nutricion' }).toString();
    }
  }

  function saveCurrentProfileToAccount() {
    if (!window.ARES_ACCOUNT || !window.ARES_BRIDGE || !window.ARES_ACCOUNT.current()) return;
    const saved = window.ARES_ACCOUNT.saveProfile(window.ARES_BRIDGE.read());
    document.dispatchEvent(new CustomEvent('ares:nutrition-profile-ready', {
      detail: { profile: saved || window.ARES_BRIDGE.read() },
    }));
  }

  function openPlanner() {
    if (!plannerPanel) return;
    hydrateProfile();
    plannerPanel.hidden = false;
    plannerOpen.hidden = true;
    plannerPanel.classList.add('is-open');
    setTimeout(() => weightInput.focus(), 80);
  }

  function requestPlanner() {
    const continueToPlanner = () => openPlanner();
    if (window.ARES_ACCOUNT && typeof window.ARES_ACCOUNT.requireAuth === 'function') {
      window.ARES_ACCOUNT.requireAuth(continueToPlanner);
      return;
    }
    openPlanner();
  }

  function closePlanner() {
    if (!plannerPanel) return;
    plannerPanel.hidden = true;
    plannerOpen.hidden = false;
    plannerPanel.classList.remove('is-open');
  }

  function calculate(event) {
    event.preventDefault();
    const weight = numberOrNull(weightInput.value);
    const ageMonths = ageInMonths();
    if (weight == null || ageMonths == null || weight <= 0 || ageMonths <= 0) return;

    const activityEstimate = getActivityEstimate(weight, ageMonths);
    const goalFactors = { maintain: 1.0, define: 1.0, lose: 0.85, gain: 1.1 };
    const dailyKcal = Math.round(activityEstimate.energy * (goalFactors[goalInput.value] || 1));
    const lines = foodLines(dailyKcal);

    kcalValue.textContent = formatNumber(dailyKcal);
    renderFood(lines);
    renderExtraPortion(dailyKcal, ageMonths, weight);
    sourceResult.textContent = activityEstimate.source + '. Es una orientación inicial, no una pauta clínica.';
    renderWarning(ageMonths);
    updateCrossLinks();
    emptyResult.hidden = true;
    resultContent.hidden = false;

    if (window.ARES_BRIDGE) {
      window.ARES_BRIDGE.save({
        source: 'nutricion',
        weightKg: weight,
        ageMonths,
        nutrition: {
          goal: goalInput.value,
           activitySource: activityInput.value,
           foodType: foodTypeInput.value,
           extraFood: extraFoodInput.value,
           targetKcal: dailyKcal,
          updatedAt: new Date().toISOString(),
        },
      });
      hydrateProfile();
      saveCurrentProfileToAccount();
    }

    document.dispatchEvent(new CustomEvent('ares:nutrition-calculated', {
      detail: {
        ageMonths,
        weightKg: weight,
        goal: goalInput.value,
         activitySource: activityInput.value,
         foodType: foodTypeInput.value,
         extraFood: extraFoodInput.value,
         targetKcal: dailyKcal,
        foodLines: lines,
      },
    }));
  }

  if (plannerOpen) plannerOpen.addEventListener('click', requestPlanner);
  if (plannerClose) plannerClose.addEventListener('click', closePlanner);
  if (ageUnitInput) ageUnitInput.addEventListener('change', updateAgeUnit);
  hydrateProfile();
  updateFoodInputs();
  if (saveAccountButton && window.ARES_ACCOUNT) {
    saveAccountButton.addEventListener('click', () => window.ARES_ACCOUNT.openModal());
    const refreshAccountLabel = () => {
      const account = window.ARES_ACCOUNT.current();
      const label = account ? 'Perfil guardado en ' + account.email : 'Crear cuenta y guardar mi perfil';
      const labelNode = saveAccountButton.querySelector('span');
      if (labelNode) labelNode.textContent = label;
    };
    window.ARES_ACCOUNT.onAuthChange(refreshAccountLabel);
    refreshAccountLabel();
  }
  document.addEventListener('ares:auth-success', () => {
    hydrateProfile();
    updateCrossLinks();
    saveCurrentProfileToAccount();
  });
  foodTypeInput.addEventListener('change', updateFoodInputs);
  form.addEventListener('submit', calculate);

  window.ARES_NUTRITION = {
    open: openPlanner,
    close: closePlanner,
    getProfile: () => window.ARES_BRIDGE ? window.ARES_BRIDGE.read() : null,
    getPayload: () => ({
      profile: window.ARES_BRIDGE ? window.ARES_BRIDGE.read() : null,
      ageMonths: ageInMonths(),
      weightKg: numberOrNull(weightInput.value),
      goal: goalInput.value,
       activitySource: activityInput.value,
       foodType: foodTypeInput.value,
       extraFood: extraFoodInput.value,
     }),
  };
})();
