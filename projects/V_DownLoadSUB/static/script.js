// V_DOWNLOADER v3 — Stage-based workflow
var CapStyle = window.CaptionStyle;
var lastTranscriptText = "";
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
  if (saved === "dark") { document.documentElement.classList.add("dark"); }
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var isDark = document.documentElement.classList.toggle("dark");
      localStorage.setItem("vdownloader-theme", isDark ? "dark" : "light");
      if (typeof redraw === "function") redraw();
    });
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

async function checkStatus() {
  try {
    var r = await fetch(API_URL + "/api/status", { signal: AbortSignal.timeout(5000) });
    var s = await r.json();
    setBadge("badge-ytdlp", s.yt_dlp);
    setBadge("badge-ffmpeg", s.ffmpeg);
    setBadge("badge-whisper", s.whisper);
  } catch (e) {
    ["badge-ytdlp","badge-ffmpeg","badge-whisper"].forEach(function(id){
      var els = document.querySelectorAll("#" + id);
      els.forEach(function(el){
        el.classList.add("fail");
        el.textContent = el.textContent.split(" ")[0] + " ?";
      });
    });
  }
}

function setBadge(id, ok) {
  var els = document.querySelectorAll("#" + id);
  els.forEach(function (el) {
    el.classList.toggle("ok", ok);
    el.classList.toggle("fail", !ok);
    el.textContent = id.replace("badge-", "") + (ok ? " ✓" : " ✗");
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

async function fetchInfo() {
  var url = document.getElementById("urlInput").value.trim();
  if (!url) return;
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
  if (!url) { alert("Introduce una URL."); return; }
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
  dlBtn.textContent = isPlaylist ? "PROCESANDO COLECCION..." : "DESCARGANDO...";
  var transcribeCheck = document.getElementById("transcribeCheck");
  var ocrCheck = document.getElementById("ocrCheck");
  var autoTranslateCheck = document.getElementById("autoTranslateCheck");
  var payload = {
    url: url,
    quality: getSelected("quality") || "best",
    format: getSelected("format") || "mp4",
    subtitles: document.getElementById("subCheck").checked,
    embed_subs: document.getElementById("embedSubCheck").checked,
    cookies: getSelected("cookies") || "none",
    auto_transcribe: transcribeCheck && transcribeCheck.checked,
    whisper_model: "base",
    separate_audio: false,
    auto_ocr: ocrCheck && ocrCheck.checked,
    auto_translate: autoTranslateCheck && autoTranslateCheck.checked,
    is_playlist: isPlaylist
  };
  try {
    var controller = new AbortController();
    var warnTimer = setTimeout(function () { addLogLine("warn", "La descarga esta tardando mas de lo normal..."); }, 60000);
    var abortTimer = setTimeout(function () { controller.abort(); }, 600000);
    var resp = await fetch(API_URL + "/api/download", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload), signal: controller.signal
    });
    clearTimeout(warnTimer); clearTimeout(abortTimer);
    var data = await resp.json();
    if (data.status === "ok" && data.files) {
      document.getElementById("progressBar").style.width = "100%";
      document.getElementById("progressPct").textContent = "100%";
      document.getElementById("progressLabel").textContent = "✓ " + data.count + " video(s) procesados";
      data.files.forEach(function (f) { addLogLine("success", "✓ " + f.filename); });
    } else if (data.status === "ok") {
      document.getElementById("progressBar").style.width = "100%";
      document.getElementById("progressPct").textContent = "100%";
      document.getElementById("progressLabel").textContent = "✓ DESCARGA COMPLETADA";
      addLogLine("success", "✓ Guardado: " + data.filename);
      if (data.edited_file) addLogLine("success", "Video con subtitulos: " + data.edited_file);
    } else {
      document.getElementById("progressLabel").textContent = "ERROR";
      addLogLine("error", "✗ Error: " + (data.error || "Descarga fallida"));
    }
  } catch (e) {
    document.getElementById("progressLabel").textContent = "ERROR DE CONEXION";
    document.getElementById("progressBar").style.background = "var(--terracotta)";
    addLogLine("error", "Error: " + (e.name === "AbortError" ? "La descarga no respondio a tiempo" : e.message));
  }
  dlBtn.disabled = false; dlBtn.textContent = "⬇ DESCARGAR";
  loadDownloads();
}

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
  var zone = document.getElementById("dropZone");
  var text = zone && zone.querySelector(".drop-text");
  var hint = zone && zone.querySelector(".drop-hint");
  if (text) text.textContent = "Subiendo " + file.name + "...";
  if (hint) hint.textContent = "";
  var fd = new FormData();
  fd.append("file", file);
  fetch(API_URL + "/api/upload", { method: "POST", body: fd })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.error) {
        if (text) text.textContent = "Error: " + data.error;
        if (hint) hint.textContent = "";
        return;
      }
      if (text) text.textContent = "¡" + file.name + " subido!";
      if (hint) hint.textContent = "Redirigiendo...";
      loadDownloads();
      setTimeout(function () { openStudio(data.folder); }, 500);
    })
    .catch(function (e) {
      if (text) text.textContent = "Error: " + e.message;
      if (hint) hint.textContent = "";
      setTimeout(function () {
        if (text) text.textContent = "O arrastra tu vídeo o audio aquí";
        if (hint) hint.textContent = "MP4, MOV, WebM, MKV, MP3, WAV, OGG";
      }, 3000);
     });
}
