// V_DOWNLOADER v3 — Stage-based workflow
var CapStyle = window.CaptionStyle;
var lastTranscriptText = "";
var activeDownloadJobId = null;
var downloadPollTimer = null;
var downloadPollWarningShown = false;
var localFile = null;
var localFileUrl = "";
var STAGE_IDS = ['stage-upload', 'stage-config', 'stage-studio'];

function showStage(stageId) {
  STAGE_IDS.forEach(function(id) {
    document.getElementById(id).style.display = 'none';
  });
  var stage = document.getElementById(stageId);
  if (!stage) return;
  stage.style.display = '';
  stage.style.animation = 'none';
  void stage.offsetHeight;
  stage.style.animation = 'stageIn 0.5s cubic-bezier(0.16,1,0.3,1) both';
}

window.addEventListener("DOMContentLoaded", function () {
  // Theme toggle
  var themeBtn = document.getElementById("themeToggle");
  var saved = localStorage.getItem("vdownloader-theme");
  if (!saved) {
    // Sin preferencia guardada: seguir la del sistema operativo
    saved = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  if (saved === "dark") { document.documentElement.classList.add("dark"); }
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var isDark = document.documentElement.classList.toggle("dark");
      localStorage.setItem("vdownloader-theme", isDark ? "dark" : "light");
      if (typeof redraw === "function") redraw();
    });
    // Si el usuario nunca eligió, seguir cambios de tema del SO en vivo
    if (!localStorage.getItem("vdownloader-theme") && window.matchMedia) {
      try {
        window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function (e) {
          document.documentElement.classList.toggle("dark", e.matches);
          if (typeof redraw === "function") redraw();
        });
      } catch (err) { /* navegadores antiguos */ }
    }
  }
  initDropUpload();
  try {
    checkStatus();
    loadDownloads();
    initRadioPills();
    initTabs();
    initSpotlight();
    initStudioV2();
  } catch (e) {
    console.error("Init error:", e);
  }
  ["badge-ytdlp","badge-ffmpeg","badge-whisper"].forEach(function(id){
    setBadge(id, "cargando");
  });
  showStage("stage-upload");
  document.getElementById("urlInput").addEventListener("keydown", function (e) {
    if (e.key === "Enter") fetchInfo();
  });
  document.getElementById("playlistCheck").addEventListener("change", function (e) {
    var pills = document.querySelectorAll("#cookieGroup .radio-pill");
    if (e.target.checked) {
      pills.forEach(function (p) { p.classList.add("disabled"); });
      var nonePill = document.querySelector('#cookieGroup [data-val="none"]');
      if (nonePill) { nonePill.click(); }
    } else {
      pills.forEach(function (p) { p.classList.remove("disabled"); });
    }
  });
});

function initSpotlight() {
  var wrap = document.getElementById("urlWrap");
  if (!wrap) return;
  var raf = 0, px = 0, py = 0;
  wrap.addEventListener("pointermove", function (e) {
    px = e.clientX; py = e.clientY;
    if (raf) return;
    raf = requestAnimationFrame(function () {
      raf = 0;
      var r = wrap.getBoundingClientRect();
      wrap.style.setProperty("--mx", (px - r.left) + "px");
      wrap.style.setProperty("--my", (py - r.top) + "px");
    });
  });
}

function initTabs() {
  document.querySelectorAll(".config-tab").forEach(function (tab) {
    tab.addEventListener("click", function () {
      document.querySelectorAll(".config-tab").forEach(function (t) { t.classList.remove("is-active"); });
      tab.classList.add("is-active");
      var panelId = tab.dataset.tab;
      document.querySelectorAll(".tab-panel").forEach(function (p) { p.classList.remove("is-active"); });
      var panel = document.getElementById("tab-" + panelId);
      if (panel) panel.classList.add("is-active");
    });
  });
}

// La página prueba primero el mismo origen y luego el motor local de Liam (5555).
var API_CANDIDATOS = (function () {
  var lista = [];
  var motor = new URLSearchParams(location.search).get("motor");
  if (motor) lista.push(motor.replace(/\/+$/, ""));
  if (location.protocol !== "file:" && !/github\.io$/.test(location.hostname)) lista.push(location.origin);
  lista.push("http://127.0.0.1:5555", "http://localhost:5555");
  return lista;
})();
var API_URL = API_CANDIDATOS[0];
var SIN_SERVIDOR = true;
var REINTENTO_MS = 8000;
var reintentoTimer = null;

function fijarControles(activos) {
  var urlInput = document.getElementById("urlInput");
  var fetchBtn = document.getElementById("fetchBtn");
  var fileInput = document.getElementById("fileInput");
  var dropZone = document.getElementById("dropZone");
  if (urlInput) {
    urlInput.disabled = !activos;
    urlInput.placeholder = activos ? "Pega aquí la URL del vídeo..." : "Conecta el motor local para analizar enlaces";
    if (activos) urlInput.removeAttribute("aria-describedby");
    else urlInput.setAttribute("aria-describedby", "avisoDemo");
  }
  if (fetchBtn) {
    fetchBtn.disabled = !activos;
    fetchBtn.classList.toggle("demo-only", !activos);
    fetchBtn.textContent = activos ? "Analizar" : "Siguiente paso";
    fetchBtn.title = activos ? "" : "El procesamiento no está disponible en esta página pública";
  }
  if (fileInput) fileInput.disabled = !activos;
  if (dropZone) {
    dropZone.classList.toggle("demo-disabled", !activos);
    dropZone.setAttribute("aria-disabled", activos ? "false" : "true");
  }
}
function avisoDemo(resaltar) {
  var aviso = document.getElementById("avisoDemo");
  if (!aviso) {
    aviso = document.createElement("div");
    aviso.id = "avisoDemo";
    aviso.className = "aviso-demo";
    aviso.setAttribute("role", "status");
     aviso.innerHTML = "<strong>Motor local no conectado.</strong> Analizar enlaces y procesar archivos necesita el motor de V_DOWNLOADER (Flask + yt-dlp + FFmpeg) en tu equipo. Hace falta el motor de V_DOWNLOADER en tu equipo. Lo intento de nuevo automáticamente cada 8 s; también puedes reintentar ahora:" +
      "<div class=\"aviso-acciones\"><button type=\"button\" class=\"aviso-btn\" id=\"reintentarMotor\">Reintentar conexión</button><a href=\"../../index.html#contact\">Pedir una demo funcional →</a></div>";
    var wrap = document.getElementById("urlWrap");
    if (wrap && wrap.parentNode) wrap.parentNode.insertBefore(aviso, wrap.nextSibling);
    var btn = document.getElementById("reintentarMotor");
    if (btn) btn.addEventListener("click", function () { btn.disabled = true; btn.textContent = "Conectando..."; checkStatus(); });
  }
  if (resaltar) { aviso.classList.remove("pulso"); void aviso.offsetWidth; aviso.classList.add("pulso"); }
}
function marcarSinServidor() {
  SIN_SERVIDOR = true;
  fijarControles(false);
  ["badge-ytdlp","badge-ffmpeg","badge-whisper"].forEach(function(id){
    setBadge(id, "fail");
  });
  avisoDemo(false);
  if (!reintentoTimer) {
    reintentoTimer = setInterval(function () {
      if (!SIN_SERVIDOR) { clearInterval(reintentoTimer); reintentoTimer = null; return; }
      checkStatus();
    }, REINTENTO_MS);
  }
}

function marcarConMotor(status) {
  SIN_SERVIDOR = false;
  fijarControles(true);
  var aviso = document.getElementById("avisoDemo");
  if (aviso) aviso.remove();
  ["badge-ytdlp","badge-ffmpeg","badge-whisper"].forEach(function(id){
    document.querySelectorAll("#" + id).forEach(function(el){ el.classList.remove("local"); });
  });
  if (status) {
    setBadge("badge-ytdlp", status.yt_dlp);
    setBadge("badge-ffmpeg", status.ffmpeg);
    setBadge("badge-whisper", status.whisper);
  }
}

async function checkStatus() {
  ["badge-ytdlp","badge-ffmpeg","badge-whisper"].forEach(function(id){
    setBadge(id, "cargando");
  });
  var conectado = false;
  for (var i = 0; i < API_CANDIDATOS.length; i++) {
    try {
      var r = await fetch(API_CANDIDATOS[i] + "/api/status", { signal: AbortSignal.timeout(2500) });
      if (!r.ok) continue;
      var s = await r.json();
      API_URL = API_CANDIDATOS[i];
      marcarConMotor(s);
      conectado = true;
      loadDownloads();
      return;
    } catch (e) { /* siguiente candidato */ }
  }
  if (!conectado) marcarSinServidor();
}

function setBadge(id, estado) {
  // estado: "cargando" | "ok" | "fail"
  var els = document.querySelectorAll("#" + id);
  els.forEach(function (el) {
    el.classList.remove("cargando", "ok", "fail");
    el.classList.add(estado);
    var base = id.replace("badge-", "");
    if (estado === "cargando") {
      el.innerHTML = '<span class="badge-spin"></span>' + base;
      el.title = "Verificando…";
    } else if (estado === "ok") {
      el.textContent = base + " ✓";
      el.title = "Disponible";
    } else {
      el.textContent = base + " ✗";
      el.title = "No disponible";
    }
  });
}

function initRadioPills() {
  document.querySelectorAll(".radio-pill").forEach(function (pill) {
    pill.addEventListener("click", function () {
      var group = pill.dataset.group;
      document.querySelectorAll('[data-group="' + group + '"]').forEach(function (p) { p.classList.remove("active"); });
      pill.classList.add("active");
      var input = pill.querySelector("input");
      if (input) input.checked = true;
      if (group === "format") {
        var val = pill.dataset.val;
        var qCard = document.getElementById("qualityCard");
        if (qCard) {
          qCard.style.opacity = (val === "mp3" || val === "m4a") ? ".4" : "1";
          qCard.style.pointerEvents = (val === "mp3" || val === "m4a") ? "none" : "auto";
        }
      }
    });
  });
}

function getSelected(group) {
  var active = document.querySelector('[data-group="' + group + '"].active');
  return active ? active.dataset.val : null;
}

function isChecked(id) {
  var input = document.getElementById(id);
  return !!(input && input.checked);
}

async function fetchInfo() {
  var url = document.getElementById("urlInput").value.trim();
  if (!url) return;
  if (SIN_SERVIDOR) { avisoDemo(true); return; }
  var btn = document.getElementById("fetchBtn");
  btn.textContent = "..."; btn.disabled = true;
  try {
    var r = await fetch(API_URL + "/api/info", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url, cookies: getSelected("cookies") || "none" })
    });
    var info = await r.json();
    if (info.error) { alert("Error: " + info.error); btn.textContent = "Analizar"; btn.disabled = false; return; }
    document.getElementById("thumbnail").src = info.thumbnail || "";
    document.getElementById("videoTitle").textContent = info.title || "Sin titulo";
    document.getElementById("metaChannel").textContent = info.channel || "?";
    document.getElementById("metaDuration").textContent = info.duration || "?";
    document.getElementById("metaViews").textContent = info.view_count ? fmtNum(info.view_count) + " vistas" : "";
    document.getElementById("metaDate").textContent = fmtDate(info.upload_date) || "";
    document.getElementById("metaPlatform").textContent = info.platform || "";
    showStage("stage-config");
  } catch (e) {
    alert("Error de red: " + e.message);
  }
  btn.textContent = "Analizar"; btn.disabled = false;
}

function backToUpload() { showStage("stage-upload"); }

function fmtNum(n) { return Number(n).toLocaleString("es-ES"); }
function fmtDate(d) {
  if (!d || d.length < 8) return d;
  return d.slice(6, 8) + "/" + d.slice(4, 6) + "/" + d.slice(0, 4);
}

async function startDownload() {
  var url = document.getElementById("urlInput").value.trim();
  if (!url && !localFile) { alert("Introduce una URL o selecciona un archivo."); return; }
  if (localFile && !url) {
    downloadLocalFile();
    return;
  }
  if (activeDownloadJobId) return;
  var progressCard = document.getElementById("progressCard");
  var transcriptCard = document.getElementById("transcriptCard");
  progressCard.classList.remove("hidden");
  if (transcriptCard) transcriptCard.classList.add("hidden");
  document.getElementById("logArea").innerHTML = "";
  document.getElementById("progressBar").style.width = "0%";
  document.getElementById("progressPct").textContent = "0%";
  document.getElementById("progressLabel").textContent = "INICIANDO DESCARGA...";
  var dlBtn = document.getElementById("downloadBtn");
  dlBtn.disabled = true;
  var isPlaylist = document.getElementById("playlistCheck").checked;
  dlBtn.textContent = "INICIANDO...";
  var transcribeCheck = document.getElementById("transcribeCheck");
  var ocrCheck = document.getElementById("ocrCheck");
  var autoTranslateCheck = document.getElementById("autoTranslateCheck");
  var payload = {
    url: url,
    quality: getSelected("quality") || "best",
    format: getSelected("format") || "mp4",
    subtitles: !!(document.getElementById("subCheck") || {}).checked,
    embed_subs: !!(document.getElementById("embedSubCheck") || {}).checked,
    cookies: getSelected("cookies") || "none",
    auto_transcribe: !!(transcribeCheck && transcribeCheck.checked),
    whisper_model: "base",
    separate_audio: false,
    auto_ocr: !!(ocrCheck && ocrCheck.checked),
    auto_translate: !!(autoTranslateCheck && autoTranslateCheck.checked),
    is_playlist: isPlaylist
  };
  try {
    var resp = await fetch(API_URL + "/api/download", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    var data = await resp.json();
    if (!resp.ok || !data.job_id) {
      throw new Error(data.error || "No se pudo iniciar la descarga.");
    }
    activeDownloadJobId = data.job_id;
    dlBtn.textContent = isPlaylist ? "PROCESANDO COLECCIÓN..." : "DESCARGANDO...";
    pollDownloadJob(activeDownloadJobId);
  } catch (e) {
    document.getElementById("progressLabel").textContent = "ERROR AL INICIAR";
    document.getElementById("progressBar").style.background = "var(--terracotta)";
    addLogLine("error", "Error: " + e.message);
    dlBtn.disabled = false;
    dlBtn.textContent = "⬇ DESCARGAR";
    document.getElementById("pauseDownloadBtn").hidden = true;
    document.getElementById("resumeDownloadBtn").hidden = true;
  }
}

function renderDownloadJob(job) {
  var pct = Number(job.percent);
  var bar = document.getElementById("progressBar");
  var label = document.getElementById("progressLabel");
  var pctLabel = document.getElementById("progressPct");
  var hint = document.getElementById("downloadStageHint");
  var pauseBtn = document.getElementById("pauseDownloadBtn");
  var resumeBtn = document.getElementById("resumeDownloadBtn");
  var dlBtn = document.getElementById("downloadBtn");
  if (Number.isFinite(pct)) bar.style.width = Math.max(0, Math.min(100, pct)) + "%";
  pctLabel.textContent = job.total_bytes ? Math.round(pct || 0) + "%" : "";
  label.textContent = job.message || "Procesando…";
  if (job.state === "processing") {
    hint.textContent = "Descarga terminada; transcripción/OCR/render en curso. La pausa solo controla la descarga.";
  } else if (job.state === "pausing") {
    hint.textContent = "Pausando en el siguiente fragmento…";
  } else if (job.state === "paused") {
    hint.textContent = "Descarga pausada. Pulsa Reanudar para continuar.";
  } else if (job.state === "downloading") {
    var details = [];
    if (job.speed) details.push(formatDownloadSize(job.speed) + "/s");
    if (job.eta !== null && job.eta !== undefined && Number.isFinite(Number(job.eta))) details.push("quedan " + formatDownloadEta(Number(job.eta)));
    hint.textContent = details.join(" · ");
  } else {
    hint.textContent = "";
  }
  pauseBtn.hidden = job.state !== "downloading";
  resumeBtn.hidden = !["pausing", "paused"].includes(job.state);
  resumeBtn.disabled = job.state === "pausing";
  resumeBtn.textContent = job.state === "pausing" ? "Pausando…" : "▶ Reanudar";
  var terminado = ["completed", "error"].includes(job.state);
  dlBtn.disabled = !terminado;
  if (terminado) {
    dlBtn.textContent = "⬇ DESCARGAR";
  } else if (job.state === "paused") {
    dlBtn.textContent = "PAUSADO";
  } else if (job.state === "processing") {
    dlBtn.textContent = "PROCESANDO…";
  } else {
    dlBtn.textContent = "DESCARGANDO…";
  }
}

async function pollDownloadJob(jobId) {
  if (activeDownloadJobId !== jobId) return;
  try {
    var response = await fetch(API_URL + "/api/download/" + encodeURIComponent(jobId), {
      signal: AbortSignal.timeout(8000)
    });
    var job = await response.json();
    if (!response.ok) throw new Error(job.error || "No se pudo consultar el progreso.");
    downloadPollWarningShown = false;
    renderDownloadJob(job);
    if (job.state === "completed") {
      activeDownloadJobId = null;
      loadDownloads();
      var result = job.result || {};
      var files = result.files || [];
      var folder = result.folder || (files.length === 1 ? files[0].folder : null);
      if (folder) setTimeout(function () { openStudio(folder); }, 350);
      else if (files.length > 1) addLogLine("success", files.length + " vídeos listos. Elige una carpeta para abrir el Studio.");
      return;
    }
    if (job.state === "error") {
      activeDownloadJobId = null;
      addLogLine("error", "✗ " + (job.error || job.message || "Descarga fallida."));
      return;
    }
  } catch (e) {
    if (activeDownloadJobId === jobId && !downloadPollWarningShown) {
      downloadPollWarningShown = true;
      addLogLine("warn", "Sin actualización de progreso; sigo comprobando el trabajo…");
    }
  }
  if (activeDownloadJobId === jobId) downloadPollTimer = setTimeout(function () { pollDownloadJob(jobId); }, 1000);
}

function formatDownloadSize(bytes) {
  var units = ["B", "KB", "MB", "GB"];
  var value = Math.max(0, Number(bytes) || 0), unit = 0;
  while (value >= 1024 && unit < units.length - 1) { value /= 1024; unit++; }
  return value.toFixed(unit ? 1 : 0) + " " + units[unit];
}

function formatDownloadEta(seconds) {
  var value = Math.max(0, Math.round(seconds));
  if (value < 60) return value + " s";
  var minutes = Math.floor(value / 60), rest = value % 60;
  return minutes + " min" + (rest ? " " + rest + " s" : "");
}

async function controlDownload(action) {
  if (!activeDownloadJobId) return;
  var button = document.getElementById(action === "pause" ? "pauseDownloadBtn" : "resumeDownloadBtn");
  button.disabled = true;
  try {
    var response = await fetch(API_URL + "/api/download/" + encodeURIComponent(activeDownloadJobId) + "/" + action, { method: "POST" });
    var job = await response.json();
    if (!response.ok) throw new Error(job.error || "No se pudo cambiar el estado de la descarga.");
    renderDownloadJob(job);
  } catch (e) {
    addLogLine("error", e.message);
  } finally {
    if (button.isConnected) button.disabled = false;
  }
}

function pauseActiveDownload() { return controlDownload("pause"); }
function resumeActiveDownload() { return controlDownload("resume"); }

function addLogLine(type, msg) {
  var area = document.getElementById("logArea");
  if (!area) return;
  var div = document.createElement("div");
  div.className = "log-line" + (type ? " " + type : "");
  div.textContent = msg;
  area.appendChild(div);
  area.scrollTop = area.scrollHeight;
}

function copyTranscript() {
  if (!lastTranscriptText) return;
  navigator.clipboard.writeText(lastTranscriptText);
}

function downloadTranscript() {
  if (!lastTranscriptText) return;
  var blob = new Blob([lastTranscriptText], { type: "text/plain;charset=utf-8" });
  var a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "transcript_" + Date.now() + ".txt";
  a.click();
}

function initStudioV2() {
  var ui = {
    studioCard: document.getElementById("studioCard"),
    video: document.getElementById("studioVideo"),
    videoPreview: document.getElementById("videoPreview"),
    caption: document.getElementById("caption"),
    captionGuides: document.getElementById("captionGuides"),
    segList: document.getElementById("segList"),
    segCount: document.getElementById("segCount"),
    langTabs: document.getElementById("langTabs"),
    addSegBtn: document.getElementById("addSegBtn"),
    langAddBtn: document.getElementById("langAddBtn"),
    translateBtn: document.getElementById("translateBtn"),
    renderBtn: document.getElementById("renderBtn"),
    exportSrtBtn: document.getElementById("exportSrtBtn"),
    closeStudio: document.getElementById("closeStudio"),
    extractAudio: document.getElementById("extractAudio"),
    extractVisual: document.getElementById("extractVisual"),
    extractBoth: document.getElementById("extractBoth"),
    tlUndo: document.getElementById("tlUndo"),
    tlRedo: document.getElementById("tlRedo"),
    tlPlay: document.getElementById("tlPlay"),
    tlClock: document.getElementById("tlClock"),
    tlZoomIn: document.getElementById("tlZoomIn"),
    tlZoomOut: document.getElementById("tlZoomOut"),
    timeline: document.getElementById("timeline"),
    timelineScroll: document.getElementById("timelineScroll"),
    timelineTrack: document.getElementById("timelineTrack"),
    timelineRuler: document.getElementById("timelineRuler"),
    timelineBlocks: document.getElementById("timelineBlocks"),
    timelinePlayhead: document.getElementById("timelinePlayhead"),
    styleToggle: document.getElementById("styleToggle"),
    styleControls: document.getElementById("styleControls"),
    stylePresets: document.getElementById("stylePresets"),
    csFont: document.getElementById("csFont"),
    csSize: document.getElementById("csSize"),
    csColor: document.getElementById("csColor"),
    csBold: document.getElementById("csBold"),
    csItalic: document.getElementById("csItalic"),
    csOutline: document.getElementById("csOutline"),
    csBg: document.getElementById("csBg"),
    csBgColor: document.getElementById("csBgColor"),
    csBgOpacity: document.getElementById("csBgOpacity"),
    csWordHighlight: document.getElementById("csWordHighlight"),
    csPosition: document.getElementById("csPosition"),
    csAlign: document.getElementById("csAlign"),
  };
  StudioV2.init(ui);
}

function openStudio(folderName) {
  StudioV2.open(folderName);
  showStage("stage-studio");
}
function closeStudio() {
  StudioV2.close();
  showStage("stage-config");
}
function extractStudio(mode) { StudioV2.extract(mode); }
function renderStudio() { StudioV2.renderVideo(); }

async function loadDownloads() {
  try {
    var r = await fetch(API_URL + "/api/downloads");
    var data = await r.json();
    var lists = document.querySelectorAll("#downloadsList, #downloadsListConfig");
    lists.forEach(function (container) {
      if (!data.files || data.files.length === 0) {
        container.innerHTML = '<p class="empty-hint">Sin archivos aun.</p>';
        return;
      }
      container.innerHTML = data.files.map(function (f) {
        if (f.type === "folder") {
          return '<div class="download-item folder" onclick="openStudio(\'' + f.name + '\')">' +
            '<span class="dl-ext">DIR</span>' +
            '<div class="dl-info"><div class="dl-name">' + f.name + '</div><div class="dl-meta">' + f.size_mb + ' MB · ' + f.modified + '</div></div>' +
            '<button class="btn" style="flex-shrink:0">Abrir Studio</button></div>';
        }
        return '<div class="download-item">' +
          '<span class="dl-ext">' + (f.ext || 'file') + '</span>' +
          '<div class="dl-info"><div class="dl-name">' + f.name + '</div><div class="dl-meta">' + f.size_mb + ' MB · ' + f.modified + '</div></div>';
      }).join("");
    });
  } catch (e) {}
}

function initDropUpload() {
  var zone = document.getElementById("dropZone");
  var input = document.getElementById("fileInput");
  if (!zone || !input) return;

  zone.addEventListener("click", function () { input.click(); });
  input.addEventListener("change", function () {
    if (input.files.length) uploadFile(input.files[0]);
  });

  ["dragenter", "dragover"].forEach(function (ev) {
    zone.addEventListener(ev, function (e) { e.preventDefault(); zone.classList.add("drag-over"); });
  });
  ["dragleave", "drop"].forEach(function (ev) {
    zone.addEventListener(ev, function (e) { e.preventDefault(); zone.classList.remove("drag-over"); });
  });
  zone.addEventListener("drop", function (e) {
    e.preventDefault();
    zone.classList.remove("drag-over");
    if (e.dataTransfer.files.length) uploadFile(e.dataTransfer.files[0]);
  });
}

function uploadFile(file) {
  if (SIN_SERVIDOR) { avisoDemo(true); return; }
  if (localFileUrl) URL.revokeObjectURL(localFileUrl);
  localFile = file;
  localFileUrl = URL.createObjectURL(file);
  var zone = document.getElementById("dropZone");
  var text = zone && zone.querySelector(".drop-text");
  var hint = zone && zone.querySelector(".drop-hint");
  if (text) text.textContent = "¡" + file.name + " listo en tu dispositivo!";
  if (hint) hint.textContent = "No se ha subido ningún archivo al servidor.";

  var media = document.createElement(file.type.indexOf("audio/") === 0 ? "audio" : "video");
  media.preload = "metadata";
  media.src = localFileUrl;
  media.onloadedmetadata = function () {
    document.getElementById("thumbnail").removeAttribute("src");
    document.getElementById("videoTitle").textContent = file.name;
    document.getElementById("metaChannel").textContent = "Archivo local";
    document.getElementById("metaDuration").textContent = formatDuration(media.duration);
    document.getElementById("metaViews").textContent = formatBytes(file.size);
    document.getElementById("metaDate").textContent = "";
    document.getElementById("metaPlatform").textContent = "Procesamiento local";
    showStage("stage-config");
  };
}

function downloadLocalFile() {
  var a = document.createElement("a");
  a.href = localFileUrl;
  a.download = localFile.name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  var card = document.getElementById("progressCard");
  if (card) card.classList.remove("hidden");
  document.getElementById("progressBar").style.width = "100%";
  document.getElementById("progressPct").textContent = "100%";
  document.getElementById("progressLabel").textContent = "✓ ARCHIVO DESCARGADO LOCALMENTE";
  addLogLine("success", "✓ El archivo nunca salió de tu dispositivo.");
}

function formatDuration(seconds) {
  if (!Number.isFinite(seconds)) return "Duración desconocida";
  var mins = Math.floor(seconds / 60);
  var secs = Math.floor(seconds % 60).toString().padStart(2, "0");
  return mins + ":" + secs;
}

function formatBytes(bytes) {
  if (!bytes) return "";
  return (bytes / 1024 / 1024).toFixed(1) + " MB";
}
