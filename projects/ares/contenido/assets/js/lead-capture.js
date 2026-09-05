/* ============================================
   ARES GPS — Componente de captura de lead (email + GDPR)
   Reutilizado en calculadora.html, pet-friendly.html y proximamente.html
   ============================================
   CONECTAR API REAL AQUI:
   Sustituir la funcion `submitLead()` de abajo por una llamada real a la
   plataforma de email marketing elegida (Mailchimp / Brevo / ConvertKit).
   Hoy: placeholder que guarda en localStorage + console.log, sin dependencias
   externas, para poder probar el flujo visual sin backend.
   ============================================ */

(function () {
   const STORAGE_KEY = "ares_leads_v1";
   const QUALIFICATION_STORAGE_ID = "ares_pending_qualification_v1";
   // Set this on the published site once the central receiver is deployed.
   const LEAD_ENDPOINT = window.ARES_LEAD_ENDPOINT || (location.protocol === "file:" ? "" : "/v1/leads");
   const BREED_SUGGESTIONS_STORAGE_ID = "ares_breed_suggestions_v1";

  function readLeads() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    } catch (e) {
      return [];
    }
  }

  function writeLead(lead) {
    const leads = readLeads();
    leads.push(lead);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(leads));
  }

  /**
   * Sugerencias de raza NO listada ("¿Tu raza no está en la lista?" en
   * calculadora.html). Se guardan en su propia key de localStorage (misma
   * mecanica/placeholder que STORAGE_KEY de arriba, separada para no mezclar
   * leads de email con sugerencias de dataset) con estructura
   * { breedName, timestamp, resultData }.
   *
   * TODO(integracion real): cuando se conecte el backend/email marketing real
   * (pendiente de decidir plataforma, ver comentario de submitLead arriba),
   * estas sugerencias tambien deben enviarse -- por ejemplo a un canal de
   * Slack via webhook, a una tabla de BD dedicada, o a un email automatico al
   * equipo -- para que alguien las revise y las anada a breed-data.js si
   * procede. De momento solo quedan registradas localmente.
   */
  function readBreedSuggestions() {
    try {
       return JSON.parse(localStorage.getItem(BREED_SUGGESTIONS_STORAGE_ID)) || [];
    } catch (e) {
      return [];
    }
  }

  function submitBreedSuggestion(breedName, resultData) {
    const trimmed = (breedName || "").trim();
    if (!trimmed) return;
    const suggestions = readBreedSuggestions();
    suggestions.push({
      breedName: trimmed,
      timestamp: new Date().toISOString(),
      resultData: resultData || null,
    });
     localStorage.setItem(BREED_SUGGESTIONS_STORAGE_ID, JSON.stringify(suggestions));
    console.log("[ARES lead-capture] Nueva sugerencia de raza no listada (placeholder, sin backend real):", trimmed);
  }

  /**
   * Punto unico de envio de leads.
   * TODO(integracion real): reemplazar el bloque de abajo por, por ejemplo:
   *
   *   return fetch('https://<tu-endpoint-mailchimp-o-brevo>', {
   *     method: 'POST',
   *     headers: { 'Content-Type': 'application/json' },
   *     body: JSON.stringify(lead)
   *   }).then(r => r.ok);
   *
   * de momento resolvemos siempre como si hubiese ido bien (placeholder).
   */
  function submitLead(lead) {
     let qualification = null;
     try {
       qualification = JSON.parse(sessionStorage.getItem(QUALIFICATION_STORAGE_ID) || "null");
     } catch (e) {}
     const payload = qualification ? { ...lead, qualification } : lead;

     if (!LEAD_ENDPOINT) {
       console.log("[ARES lead-capture] Lead local de prueba, sin endpoint:", payload);
       writeLead(payload);
       return Promise.resolve({ ok: true, local: true });
     }

      return fetch(LEAD_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }).then((response) => {
        if (!response.ok) throw new Error("Lead endpoint returned " + response.status);
         try { sessionStorage.removeItem(QUALIFICATION_STORAGE_ID); } catch (e) {}
        return { ok: true, local: false };
      });
   }

  function initForm(form) {
    if (!form || form.dataset.leadBound === "1") return;
    form.dataset.leadBound = "1";

    const emailInput = form.querySelector('[data-lead="email"]');
    const gdprInput = form.querySelector('[data-lead="gdpr"]');
    const submitBtn = form.querySelector('[data-lead="submit"]');
    const feedback = form.querySelector('[data-lead="feedback"]');
    const extraFields = form.querySelectorAll("[data-lead-extra]");

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (feedback) {
        feedback.textContent = "";
        feedback.classList.remove("lead-feedback--error", "lead-feedback--ok");
      }

      const email = (emailInput && emailInput.value || "").trim();
      const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

      if (!emailOk) {
        showFeedback("Introduce un email valido.", true);
        emailInput && emailInput.focus();
        return;
      }
      if (gdprInput && !gdprInput.checked) {
        showFeedback("Necesitamos tu consentimiento para continuar.", true);
        return;
      }

      const extra = {};
      extraFields.forEach((el) => {
        const key = el.dataset.leadExtra;
        if (el.type === "checkbox") extra[key] = el.checked;
        else extra[key] = el.value;
      });

      const lead = {
        email,
        gdprConsent: gdprInput ? gdprInput.checked : true,
        source: form.dataset.leadSource || "desconocido",
        extra,
        createdAt: new Date().toISOString(),
      };

      if (submitBtn) submitBtn.disabled = true;

      submitLead(lead)
        .then(() => {
          showFeedback("Listo. Te avisamos en cuanto ARES esté disponible.", false);
          form.reset();
          form.classList.add("lead-form--sent");
        })
        .catch(() => {
          showFeedback("Algo ha fallado. Intenta de nuevo en unos minutos.", true);
        })
        .finally(() => {
          if (submitBtn) submitBtn.disabled = false;
        });
    });

    function showFeedback(msg, isError) {
      if (!feedback) return;
      feedback.textContent = msg;
      feedback.classList.toggle("lead-feedback--error", !!isError);
      feedback.classList.toggle("lead-feedback--ok", !isError);
    }
  }

  function init() {
    document.querySelectorAll("[data-lead-form]").forEach(initForm);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.ARES_LEAD_CAPTURE = {
    submitLead,
    readLeads,
    submitBreedSuggestion,
    readBreedSuggestions,
  };
})();
