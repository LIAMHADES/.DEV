/* ============================================
   ARES GPS — Cuenta local (registro / inicio de sesión)
   Registro o login con email en el menor número de pasos posible.
   Por ahora TODO es local (localStorage) como base pequeña de cuentas:
     - ares_accounts_v1        -> cuentas { email: {...} }
     - ares_session_v1         -> sesión activa (sessionStorage)
     - ares_saved_profiles_v1  -> perfil combinado (peso + actividad) por cuenta
   Cuando haya servidor (VPS), este módulo se conecta al backend real y se
   añade la verificación (Google o email). El contrato de ARES_ACCOUNT
   (signInWithEmail / current / signOut / saveProfile / savedProfile) se
   mantiene para no tocar las páginas cuando llegue ese momento.
   ============================================ */
 (function () {
  var ACCOUNTS_KEY = "ares_accounts_v1";
  var SESSION_KEY = "ares_session_v1";
  var PROFILES_KEY = "ares_saved_profiles_v1";

  function readJSON(key, fallback) {
    try {
      var v = JSON.parse(localStorage.getItem(key) || "null");
      return v == null ? fallback : v;
    } catch (e) {
      return fallback;
    }
  }
  function writeJSON(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) {}
  }
  function readSession() {
    try { return JSON.parse(sessionStorage.getItem(SESSION_KEY) || "null"); } catch (e) { return null; }
  }
  function writeSession(s) { try { sessionStorage.setItem(SESSION_KEY, JSON.stringify(s)); } catch (e) {} }
  function clearSession() { try { sessionStorage.removeItem(SESSION_KEY); } catch (e) {} }

  function normalizeEmail(e) { return String(e || "").trim().toLowerCase(); }
  function validEmail(e) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e); }

   var modalEl = null;
   var pendingContinuation = null;

  function buildModal() {
    var d = document.createElement("div");
    d.id = "ares-account-modal";
    d.className = "account-modal";
    d.setAttribute("role", "dialog");
    d.setAttribute("aria-modal", "true");
    d.setAttribute("aria-hidden", "true");
    d.innerHTML =
      '<div class="account-modal-backdrop" data-account-close></div>' +
      '<div class="account-modal-card">' +
        '<button type="button" class="account-modal-close" data-account-close aria-label="Cerrar">&times;</button>' +
        '<div class="account-modal-title">Inicia sesión para continuar</div>' +
        '<div class="account-modal-sub">Guardaremos los datos de tu perro y te llevaremos al siguiente paso sin que tengas que volver a introducirlos.</div>' +
        '<button type="button" class="account-google" id="account-google"><span class="ag-g">G</span> Continuar con Google</button>' +
        '<div class="account-or"><span>o con tu email</span></div>' +
        '<form id="account-form" class="account-form" novalidate>' +
          '<input type="email" id="account-email" placeholder="tu@email.com" autocomplete="email" required>' +
          '<button type="submit" id="account-submit">Continuar</button>' +
        '</form>' +
        '<div class="account-feedback" id="account-feedback" role="status"></div>' +
        '<div class="account-legal">Al continuar aceptas recibir comunicaciones de ARES GPS sobre el lanzamiento y el seguimiento de la condición de tu perro. Puedes darte de baja cuando quieras.</div>' +
      '</div>';
    document.body.appendChild(d);
    return d;
  }

  function getModal() {
    if (!modalEl) {
      modalEl = document.getElementById("ares-account-modal") || buildModal();
    }
    return modalEl;
  }

  function setFeedback(m, msg, isError) {
    var f = m.querySelector("#account-feedback");
    if (!f) return;
    f.textContent = msg || "";
    f.classList.toggle("error", !!isError);
    f.classList.toggle("ok", !isError && !!msg);
  }

  function openModal() {
    var m = getModal();
    m.setAttribute("aria-hidden", "false");
    m.classList.add("open");
    var input = m.querySelector("#account-email");
    var c = current();
    if (input) {
      if (c && c.email) input.value = c.email;
      setTimeout(function () { input.focus(); }, 60);
    }
    setFeedback(m, "");
    return m;
  }
   function closeModal() {
     if (!modalEl) return;
     pendingContinuation = null;
     modalEl.classList.remove("open");
    modalEl.setAttribute("aria-hidden", "true");
   }

   function requireAuth(continuation) {
     if (typeof continuation !== "function") return false;
     if (current()) {
       continuation();
       return true;
     }
     pendingContinuation = continuation;
     openModal();
     return false;
   }

   function wireAccountOpeners() {
     document.querySelectorAll("[data-account-open]").forEach(function (el) {
       if (el.dataset.accountBound) return;
       el.dataset.accountBound = "1";
       el.addEventListener("click", function () { openModal(); });
     });
   }

  function setSession(email) {
    writeSession({ email: email, loggedInAt: new Date().toISOString() });
  }

  function signInWithEmail(email) {
    email = normalizeEmail(email);
    if (!validEmail(email)) throw new Error("invalid email");
    var accounts = readJSON(ACCOUNTS_KEY, {});
    var isNew = !accounts[email];
    if (isNew) {
      accounts[email] = { email: email, createdAt: new Date().toISOString() };
    }
    accounts[email].lastLoginAt = new Date().toISOString();
    writeJSON(ACCOUNTS_KEY, accounts);
    setSession(email);
    return { newUser: isNew, email: email };
  }

  function signOut() {
    clearSession();
    dispatchAuth();
  }

  function current() {
    var s = readSession();
    if (!s || !s.email) return null;
    var accounts = readJSON(ACCOUNTS_KEY, {});
    if (!accounts[s.email]) { clearSession(); return null; }
    return { email: s.email };
  }

   function savedProfile(email) {
    email = email || (current() || {}).email;
    if (!email) return null;
    var profiles = readJSON(PROFILES_KEY, {});
     return profiles[email] || null;
   }

   function hasProfileContext(profile) {
     return !!(profile && (
       profile.breed || profile.weightKg != null || profile.ageMonths != null ||
       profile.activity || profile.nutrition
     ));
   }

   // Rehydrate the shared bridge when a returning account has a saved profile.
   // URL/session values remain the latest values because they are merged last.
   function restoreSavedProfile() {
     if (!window.ARES_BRIDGE) return null;
     var c = current();
     var saved = c && savedProfile(c.email);
     if (!saved) return null;
     var currentProfile = window.ARES_BRIDGE.read() || {};
     window.ARES_BRIDGE.save(Object.assign({}, saved, currentProfile));
     return saved;
   }

  function saveProfile(profile) {
    var c = current();
    if (!c || !profile) return null;
    var profiles = readJSON(PROFILES_KEY, {});
    var prev = profiles[c.email] || {};
    profiles[c.email] = Object.assign({}, prev, profile, {
      email: c.email,
      savedAt: new Date().toISOString(),
    });
    writeJSON(PROFILES_KEY, profiles);
    return profiles[c.email];
  }

  var authListeners = [];
  function onAuthChange(cb) { if (typeof cb === "function") authListeners.push(cb); }
  function dispatchAuth() {
    var c = current();
    authListeners.forEach(function (cb) { try { cb(c); } catch (e) {} });
    try {
      document.dispatchEvent(new CustomEvent("ares:auth-change", { detail: c }));
    } catch (e) {}
  }

  function wireModal() {
    var m = getModal();
    if (m.dataset.bound) return;
    m.dataset.bound = "1";

    m.querySelectorAll("[data-account-close]").forEach(function (el) {
      el.addEventListener("click", closeModal);
    });

    var google = m.querySelector("#account-google");
    if (google) {
      google.addEventListener("click", function () {
        var authRequest = new CustomEvent("ares:auth-request", {
          cancelable: true,
          detail: { provider: "google" }
        });
        document.dispatchEvent(authRequest);
        if (!authRequest.defaultPrevented) {
          setFeedback(m, "Google queda preparado como punto de conexión. Mientras no haya OAuth configurado, usa tu email de prueba.", true);
        }
      });
    }

    var form = m.querySelector("#account-form");
    if (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var input = m.querySelector("#account-email");
        var email = normalizeEmail(input ? input.value : "");
        if (!validEmail(email)) {
          setFeedback(m, "Introduce un email válido.", true);
          if (input) input.focus();
          return;
        }
        var btn = m.querySelector("#account-submit");
        if (btn) btn.disabled = true;
        var r;
        try { r = signInWithEmail(email); }
        catch (err) {
          setFeedback(m, "Introduce un email válido.", true);
          if (btn) btn.disabled = false;
          return;
        }
         // Keep new page data, or restore the saved profile when this is a
         // returning user who started from a clean browser/session.
         var existingProfile = savedProfile(r.email);
         var currentProfile = window.ARES_BRIDGE ? window.ARES_BRIDGE.read() : null;
         var restored = false;
         if (hasProfileContext(currentProfile)) {
           var mergedProfile = Object.assign({}, existingProfile || {}, currentProfile);
           if (window.ARES_BRIDGE) window.ARES_BRIDGE.save(mergedProfile);
           saveProfile(mergedProfile);
         } else if (existingProfile && window.ARES_BRIDGE) {
           window.ARES_BRIDGE.save(existingProfile);
           restored = true;
         }
         var feedback = r.newUser
           ? "Perfil nuevo creado y guardado, " + r.email + "."
           : (restored
             ? "Hemos recuperado tu perfil, " + r.email + "."
             : "Datos actualizados y guardados, " + r.email + ".");
          setFeedback(m, feedback, false);
         dispatchAuth();
         document.dispatchEvent(new CustomEvent("ares:auth-success", { detail: r }));
         var continuation = pendingContinuation;
         pendingContinuation = null;
         setTimeout(function () {
           closeModal();
           if (continuation) {
             try { continuation(); } catch (e) {}
           }
         }, 1400);
      });
    }
  }

   function init() {
      restoreSavedProfile();
      if (document.readyState === "loading") {
       document.addEventListener("DOMContentLoaded", function () { getModal(); wireModal(); wireAccountOpeners(); });
      } else {
       getModal();
      wireModal();
      wireAccountOpeners();
    }
  }

  window.ARES_ACCOUNT = {
    signInWithEmail: signInWithEmail,
    signOut: signOut,
    current: current,
    saveProfile: saveProfile,
    savedProfile: savedProfile,
    requireAuth: requireAuth,
    onAuthChange: onAuthChange,
    openModal: openModal,
    closeModal: closeModal,
  };
  init();
})();
