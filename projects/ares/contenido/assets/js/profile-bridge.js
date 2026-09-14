/* ============================================
   ARES GPS — Puente de perfil entre páginas
   (calculadora.html <-> actividad.html)

   Un único origen de verdad del perfil del perro en sessionStorage
   (ares_dog_profile_v1) + tráfico vía URL params al cruzar de página.

   Forma del perfil:
     {
       breed, breeds, sex, weightKg, heightCm, ageMonths,
       category, bmi, normalMin, normalMax, sizeCategory, approxInput,
       activity: { weightKg, distanceKm, intensity, factor, minutes, kcal, updatedAt },
       source: 'calculadora' | 'actividad',
       registered: bool,   // true cuando se capturó el lead (registro de la persona)
       updatedAt
     }

   Carga: antes del script inline de cada página que use ARES_BRIDGE.
   ============================================ */
(function () {
  var KEY = 'ares_dog_profile_v1';

  function readStorage() {
    try {
      var v = JSON.parse(sessionStorage.getItem(KEY) || 'null');
      return v && typeof v === 'object' ? v : {};
    } catch (e) {
      return {};
    }
  }

  function writeStorage(profile) {
    try { sessionStorage.setItem(KEY, JSON.stringify(profile)); } catch (e) {}
  }

  // Campos que viajan por URL al cruzar de una página a otra. Los params
  // SIEMPRE ganan sobre lo guardado en sessionStorage: son lo más reciente.
  function readFromParams(params) {
    var p = {};
    var w = parseFloat(params.get('weight'));
    if (Number.isFinite(w)) p.weightKg = w;
    var h = parseFloat(params.get('height'));
    if (Number.isFinite(h)) p.heightCm = h;
    var a = parseFloat(params.get('age'));
    if (Number.isFinite(a)) p.ageMonths = a;
    if (params.get('breed')) p.breed = params.get('breed');
    if (params.get('category')) p.category = params.get('category');
    if (params.get('size')) p.sizeCategory = params.get('size');
    if (params.get('source')) p.source = params.get('source');
    if (params.get('from')) p.from = params.get('from');
    return p;
  }

  function read() {
    var profile = readStorage();
    var fromParams = readFromParams(new URLSearchParams(window.location.search));
    Object.keys(fromParams).forEach(function (k) { profile[k] = fromParams[k]; });
    return Object.keys(profile).length ? profile : null;
  }

  function save(patch) {
    var profile = Object.assign({}, readStorage(), patch || {});
    profile.updatedAt = new Date().toISOString();
    writeStorage(profile);
    return profile;
  }

  // Construye la query para cruzar de página con el perfil actual.
  // `extra` añade params adicionales (p.ej. source='actividad').
  function query(profile, extra) {
    var q = new URLSearchParams();
    profile = profile || {};
    if (profile.source) q.set('source', profile.source);
    if (profile.from) q.set('from', profile.from);
    if (typeof profile.weightKg === 'number' && Number.isFinite(profile.weightKg)) q.set('weight', profile.weightKg);
    if (typeof profile.heightCm === 'number' && Number.isFinite(profile.heightCm)) q.set('height', profile.heightCm);
    if (profile.ageMonths != null) q.set('age', profile.ageMonths);
    if (profile.breed) q.set('breed', profile.breed);
    if (profile.category) q.set('category', profile.category);
    if (profile.sizeCategory) q.set('size', profile.sizeCategory);
    if (extra) Object.keys(extra).forEach(function (k) { q.set(k, extra[k]); });
    return q;
  }

  window.ARES_BRIDGE = {
    KEY: KEY,
    read: read,
    save: save,
    query: query,
    readStorage: readStorage,
  };
})();
