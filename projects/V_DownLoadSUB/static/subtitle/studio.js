// Subtitle Studio v2 — Main orchestrator (Phase 1 port from subvid.app)
window.StudioV2 = (function () {
  var $ = SubtitleDOM.$;

  // ─── State ──────────────────────────────────────────────────────────────────
  var state = {
    detectedLang: "",
    baseSegments: [],
    segmentsByLang: {},
    orderedLangs: [],
    activeLang: "",
    dualTrackMode: false,
    dualTrackLangs: [],
    videoPath: "",
    videoFile: "",
  };

  var history;
  var timeline;
  var segEditor;
  var ui = {};
  var isOpen = false;

  // ─── Public API ──────────────────────────────────────────────────────────────
  function open(folderName, videoFile) {
    state.videoFile = videoFile;
    state.videoPath = folderName;

    // Reset state
    state.baseSegments = [];
    state.segmentsByLang = {};
    state.orderedLangs = [];
    state.activeLang = "";
    state.detectedLang = "";

    // Configure video path
    var videoUrl = folderName + "/" + (videoFile || "");
    if (!videoFile) {
      fetch(API_URL + "/api/downloads").then(function (r) { return r.json(); }).then(function (data) {
        var folder = (data.files || []).find(function (f) { return f.name === folderName; });
        if (folder && folder.files) {
          var vf = folder.files.find(function (f) { return f.endsWith(".mp4") || f.endsWith(".webm"); });
          if (vf) {
            videoUrl = folderName + "/" + vf;
            state.videoFile = vf;
          }
        }
        setupVideo(videoUrl);
      });
    } else {
      setupVideo(videoUrl);
    }
  }

  function setupVideo(videoUrl) {
    ui.video.src = API_URL + "/api/video/" + encodeURIComponent(videoUrl);
    ui.studioCard.classList.remove("hidden");
    isOpen = true;
    ui.studioCard.scrollIntoView({ behavior: "smooth" });
    if (history) history.reset();
    renderTimeline && renderTimeline();
    if (segEditor) { segEditor.renderSegments(); segEditor.renderTabs(); }
    CapStyle.renderPresets();
  }

  function close() {
    ui.video.pause();
    ui.video.src = "";
    state.baseSegments = [];
    state.segmentsByLang = {};
    state.orderedLangs = [];
    state.activeLang = "";
    ui.studioCard.classList.add("hidden");
    isOpen = false;
    updateMainDownloads();
    if (typeof showStage === 'function') showStage('stage-config');
  }

  // ─── Extraction ──────────────────────────────────────────────────────────────
  function extract(mode, evt) {
    if (!state.videoPath) return;
    var videoFullPath = "downloads/" + state.videoPath + "/" + state.videoFile;
    var btn = evt && evt.target;
    if (!btn) return;
    var orig = btn.textContent;
    btn.textContent = "..."; btn.disabled = true;

    fetch(API_URL + "/api/studio/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: videoFullPath, mode: mode }),
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.error) { alert("Error: " + data.error); return; }
        setSubtitles(data.subtitles || []);
      })
      .catch(function (e) { alert("Error: " + e.message); })
      .finally(function () { btn.textContent = orig; btn.disabled = false; });
  }

  function setSubtitles(subs) {
    if (!subs.length) return;
    // Use video source language or auto-detect
    var lang = state.detectedLang || "es";
    var segments = subs.map(function (s) {
      return { start: s.start, end: s.end, text: s.text, source: s.source };
    });

    var before = history ? history.snapshot() : "";
    state.segmentsByLang[lang] = segments;
    state.orderedLangs = [lang];
    state.activeLang = lang;
    state.baseSegments = segments;
    if (history) history.push(before);
    if (segEditor) { segEditor.renderSegments(); segEditor.renderTabs(); }
    if (timeline) timeline.renderTimeline();
    if (timeline) timeline.updateCaption();
    CapStyle.setActiveTrack("subtitles", lang);
  }

  // ─── Get state ───────────────────────────────────────────────────────────────
  function getState() { return state; }
  function setActiveLang(lang) { state.activeLang = lang; }
  function setOrderedLangs(langs) { state.orderedLangs = langs; }
  function setSegsForLang(lang, segs) { state.segmentsByLang[lang] = segs; }
  function snapshotSegs() { return JSON.stringify(getState()); }

  function trackLabel(lang) {
    if (lang === state.detectedLang) return "Original (" + lang.toUpperCase() + ")";
    return "Idioma: " + lang.toUpperCase();
  }

  function toggleTrackHidden(lang) {
    var key = "__hidden_" + lang;
    state.trackStates = state.trackStates || {};
    state.trackStates[lang] = state.trackStates[lang] || {};
    state.trackStates[lang].hidden = !state.trackStates[lang].hidden;
    if (timeline) timeline.renderTimeline();
    if (timeline) timeline.updateCaption();
  }

  function toggleTrackLocked(lang) {
    var key = "__locked_" + lang;
    state.trackStates = state.trackStates || {};
    state.trackStates[lang] = state.trackStates[lang] || {};
    state.trackStates[lang].locked = !state.trackStates[lang].locked;
    if (timeline) timeline.renderTimeline();
  }

  function visibleTracks() {
    return state.orderedLangs.map(function (lang) {
      var segs = state.segmentsByLang[lang] || [];
      var ts = (state.trackStates || {})[lang] || {};
      return {
        lang: lang,
        label: lang.toUpperCase(),
        role: "subtitles",
        segments: segs,
        hidden: ts.hidden || false,
        locked: ts.locked || false,
      };
    });
  }

  // ─── Translation ─────────────────────────────────────────────────────────────
  function translateStudio(evt) {
    var lang = state.activeLang;
    var segs = state.segmentsByLang[lang] || [];
    if (!segs.length) return;
    var btn = evt && evt.target;
    var orig = btn.textContent;
    btn.textContent = "..."; btn.disabled = true;

    fetch(API_URL + "/api/studio/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subtitles: segs, target: "es" }),
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.error) { alert("Error: " + data.error); return; }
        state.segmentsByLang[lang] = data.subtitles;
        if (segEditor) segEditor.renderSegments();
        if (timeline) timeline.updateCaption();
      })
      .catch(function (e) { alert("Error: " + e.message); })
      .finally(function () { btn.textContent = orig; btn.disabled = false; });
  }

  // ─── Render & Export ─────────────────────────────────────────────────────────
  function renderVideo(evt) {
    var lang = state.activeLang;
    var segs = state.segmentsByLang[lang] || [];
    if (!segs.length) return;
    var videoFullPath = "downloads/" + state.videoPath + "/" + state.videoFile;
    var style = {
      bg_color: ui.csBgColor ? ui.csBgColor.value : "#000000",
      font_color: ui.csColor ? ui.csColor.value : "#FFFFFF",
      opacity: ui.csBgOpacity ? ui.csBgOpacity.value : "0.8",
      font_size: ui.csSize ? Math.round(Number(ui.csSize.value) * 20) : 20,
    };
    var btn = evt && evt.target;
    var orig = btn.textContent;
    btn.textContent = "Renderizando..."; btn.disabled = true;

    fetch(API_URL + "/api/studio/render", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: videoFullPath, subtitles: segs, style: style }),
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.status === "ok") {
          alert("Video renderizado con éxito!");
          updateMainDownloads();
        } else { alert("Error: " + data.error); }
      })
      .catch(function (e) { alert("Error: " + e.message); })
      .finally(function () { btn.textContent = orig; btn.disabled = false; });
  }

  function exportSrt() {
    var lang = state.activeLang;
    var segs = state.segmentsByLang[lang] || [];
    if (!segs.length) return;
    var srt = SubtitleUtils.buildSrt(segs);
    var blob = new Blob([srt], { type: "text/plain;charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "subtitles" + (lang ? "_" + lang : "") + ".srt";
    a.click();
  }

  function refreshHistoryButtons(canUndo, canRedo) {
    if (ui.tlUndo) ui.tlUndo.disabled = !canUndo;
    if (ui.tlRedo) ui.tlRedo.disabled = !canRedo;
  }

  function restoreState(st) {
    state.segmentsByLang = st.segmentsByLang || {};
    state.orderedLangs = st.orderedLangs || [];
    state.activeLang = st.activeLang || "";
    state.dualTrackMode = st.dualTrackMode || false;
    state.dualTrackLangs = st.dualTrackLangs || [];
    state.trackStates = st.trackStates || {};
    if (segEditor) { segEditor.renderSegments(); segEditor.renderTabs(); }
    if (timeline) { timeline.renderTimeline(); timeline.updateCaption(); }
    CapStyle.setActiveTrack("subtitles", state.activeLang);
  }

  function onHistoryRestore() {
    if (segEditor) { segEditor.renderSegments(); segEditor.renderTabs(); }
    if (timeline) { timeline.renderTimeline(); timeline.updateCaption(); }
  }

  // ─── Init ────────────────────────────────────────────────────────────────────
  function init(_ui) {
    ui = _ui;

    history = EditorHistory.create({
      getState: getState,
      restoreState: restoreState,
      onRestore: onHistoryRestore,
      refreshButtons: refreshHistoryButtons,
    });

    timeline = Timeline.create({
      ui: ui,
      currentSegments: function () { return state.baseSegments; },
      visibleTracks: visibleTracks,
      activeLang: function () { return state.activeLang; },
      setActiveLang: setActiveLang,
      renderTabs: function () { segEditor && segEditor.renderTabs(); },
      renderCaptions: CapStyle.renderCaptions,
      toggleTrackHidden: toggleTrackHidden,
      toggleTrackLocked: toggleTrackLocked,
      snapshotSegments: snapshotSegs,
      pushHistory: history.push,
      renderSegments: function () { segEditor && segEditor.renderSegments(); },
    });

    segEditor = EditorSegments.create({
      ui: ui,
      getState: getState,
      setActiveLang: setActiveLang,
      setOrderedLangs: setOrderedLangs,
      setSegmentsForLang: setSegsForLang,
      trackLabel: trackLabel,
      translateSegments: function () { return Promise.resolve([]); },
      snapshotSegments: snapshotSegs,
      pushHistory: history.push,
      renderTimeline: function () { timeline.renderTimeline(); },
      highlightSegment: timeline.highlightSegment,
      updateCaption: function () { timeline.updateCaption(); },
    });

    segEditor.wireSegmentEditor();
    CapStyle.wireStyleControls(ui);
    CapStyle.renderPresets();

    // Quick extract buttons
    ui.extractAudio && ui.extractAudio.addEventListener("click", function (e) { extract("audio", e); });
    ui.extractVisual && ui.extractVisual.addEventListener("click", function (e) { extract("visual", e); });
    ui.extractBoth && ui.extractBoth.addEventListener("click", function (e) { extract("both", e); });

    // Translate button
    ui.translateBtn && ui.translateBtn.addEventListener("click", translateStudio);

    // Render & Export
    ui.renderBtn && ui.renderBtn.addEventListener("click", renderVideo);
    ui.exportSrtBtn && ui.exportSrtBtn.addEventListener("click", exportSrt);

    // Close
    ui.closeStudio && ui.closeStudio.addEventListener("click", close);

    // Undo/Redo
    ui.tlUndo && ui.tlUndo.addEventListener("click", function () { history.undo(); });
    ui.tlRedo && ui.tlRedo.addEventListener("click", function () { history.redo(); });

    // Keyboard shortcuts
    document.addEventListener("keydown", function (e) {
      if (!isOpen) return;
      if (e.ctrlKey && e.key === "z") { e.preventDefault(); history.undo(); }
      if (e.ctrlKey && e.shiftKey && e.key === "Z") { e.preventDefault(); history.redo(); }
      if (e.code === "Space" && document.activeElement === document.body) {
        e.preventDefault();
        ui.video.paused ? ui.video.play().catch(function () {}) : ui.video.pause();
      }
    });
  }

  function updateMainDownloads() {
    if (typeof loadDownloads === "function") loadDownloads();
  }

  return {
    init: init,
    open: open,
    close: close,
    extract: extract,
    setSubtitles: setSubtitles,
    getState: getState,
  };
})();
