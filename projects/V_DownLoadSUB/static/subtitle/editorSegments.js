// Segment list editor with inline editing, timestamps, multi-track language tabs
window.EditorSegments = (function () {
  var $ = SubtitleDOM.$;
  var $$ = SubtitleDOM.$$;
  var esc = SubtitleDOM.escapeHtml;
  var fc = SubtitleUtils.formatClock;
  var pc = SubtitleUtils.parseClock;

  function create(options) {
    var ui = options.ui;
    var getState = options.getState;
    var setActiveLang = options.setActiveLang;
    var setOrderedLangs = options.setOrderedLangs;
    var setSegmentsForLang = options.setSegmentsForLang;
    var trackLabel = options.trackLabel;
    var translateSegments = options.translateSegments;
    var snapshotSegments = options.snapshotSegments;
    var pushHistory = options.pushHistory;
    var renderTimeline = options.renderTimeline;
    var highlightSegment = options.highlightSegment;
    var updateCaption = options.updateCaption;

    var translatingLang = "";
    var textEditSnapshot = null;

    function visibleEditorLangs() {
      var state = getState();
      var langs = state.dualTrackMode && state.dualTrackLangs.indexOf(state.activeLang) >= 0
        ? state.dualTrackLangs : [state.activeLang];
      return langs.filter(function (lang, index) { return lang && langs.indexOf(lang) === index; });
    }

    function segmentsForLang(lang) {
      var state = getState();
      return state.segmentsByLang[lang] || [];
    }

    function setActiveLangFromElement(li) {
      var lang = li.dataset.lang;
      if (!lang || getState().activeLang === lang) return;
      setActiveLang(lang);
      renderTabs();
    }

    function segmentFromElement(li) {
      var lang = li.dataset.lang || getState().activeLang;
      var index = Number(li.dataset.index);
      var segments = segmentsForLang(lang);
      return { lang: lang, index: index, segments: segments, seg: segments[index] };
    }

    function segmentSeekTime(seg) {
      var start = Math.max(0, Number(seg.start) || 0);
      var end = isFinite(seg.end) ? Number(seg.end) : start + 0.5;
      return Math.min(start + 0.001, Math.max(start, end - 0.001));
    }

    function renderTabs() {
      var state = getState();
      if (!ui.langTabs) return;
      ui.langTabs.innerHTML = "";
      state.orderedLangs.forEach(function (lang) {
        var tab = document.createElement("button");
        tab.type = "button";
        tab.className = "tab" + (lang === state.activeLang ? " is-active" : "");
        tab.textContent = lang.toUpperCase();
        tab.addEventListener("click", function () {
          if (getState().activeLang === lang) return;
          setActiveLang(lang);
          renderTabs();
          renderSegments();
          updateCaption();
        });
        ui.langTabs.appendChild(tab);
      });
    }

    function renderSegments() {
      var state = getState();
      var langs = visibleEditorLangs();
      var isDual = state.dualTrackMode && langs.length > 1;
      ui.segList.innerHTML = "";
      ui.segList.classList.toggle("is-dual", isDual);
      var totalSegments = langs.reduce(function (count, lang) { return count + segmentsForLang(lang).length; }, 0);
      if (!totalSegments) {
        ui.segList.innerHTML = '<li class="seg-empty">Extrae audio o genera subtítulos para empezar.</li>';
        if (ui.segCount) ui.segCount.textContent = "";
        renderTimeline();
        return;
      }
      langs.forEach(function (lang) {
        var segments = segmentsForLang(lang);
        if (isDual) {
          var title = document.createElement("li");
          title.className = "seg-track-title";
          title.textContent = trackLabel(lang);
          ui.segList.appendChild(title);
        }
        segments.forEach(function (seg, index) {
          var li = document.createElement("li");
          li.className = "seg";
          li.dataset.lang = lang;
          li.dataset.index = String(index);
          li.innerHTML =
            '<div class="seg-row">' +
            '<button class="seg-play" type="button" title="Reproducir segmento"><svg width="11" height="11" viewBox="0 0 11 11"><path d="M3 2l5 3.5L3 9V2z" fill="currentColor"/></svg></button>' +
            '<input class="t-input t-start" value="' + fc(seg.start) + '" aria-label="Inicio" />' +
            '<span class="t-sep">→</span>' +
            '<input class="t-input t-end" value="' + fc(seg.end) + '" aria-label="Fin" />' +
            '<button class="seg-del" type="button" title="Eliminar segmento">✕</button>' +
            '</div>' +
            '<textarea class="seg-text" rows="2" spellcheck="false">' + esc(seg.text) + '</textarea>';
          ui.segList.appendChild(li);
        });
      });
      if (ui.segCount) ui.segCount.textContent = totalSegments + " segmentos";
      renderTimeline();
    }

    function wireSegmentEditor() {
      if (!ui.segList) return;

      ui.segList.addEventListener("input", function (event) {
        var li = event.target.closest(".seg");
        if (!li) return;
        var seg = segmentFromElement(li).seg;
        if (!seg) return;
        if (event.target.classList.contains("seg-text")) {
          seg.text = event.target.value;
          updateCaption();
        }
      });

      ui.segList.addEventListener("change", function (event) {
        var li = event.target.closest(".seg");
        if (!li) return;
        var info = segmentFromElement(li);
        if (!info.seg) return;
        var seg = info.seg, segments = info.segments;
        if (event.target.classList.contains("t-start") || event.target.classList.contains("t-end")) {
          var parsed = pc(event.target.value);
          if (parsed === null) {
            event.target.value = fc(event.target.classList.contains("t-start") ? seg.start : seg.end);
            return;
          }
          var before = snapshotSegments();
          if (event.target.classList.contains("t-start")) seg.start = parsed;
          else seg.end = parsed;
          if (seg.end <= seg.start) seg.end = seg.start + 0.5;
          segments.sort(function (a, b) { return a.start - b.start; });
          pushHistory(before);
          renderSegments();
          updateCaption();
        }
      });

      ui.segList.addEventListener("click", function (event) {
        var li = event.target.closest(".seg");
        if (!li) return;
        setActiveLangFromElement(li);
        var info = segmentFromElement(li);
        if (!info.seg) return;
        var seg = info.seg, segments = info.segments, index = info.index, lang = info.lang;
        if (event.target.closest(".seg-play")) {
          ui.video.currentTime = segmentSeekTime(seg);
          ui.video.play().catch(function () {});
        } else if (event.target.closest(".seg-del")) {
          var before = snapshotSegments();
          segments.splice(index, 1);
          pushHistory(before);
          renderSegments();
          updateCaption();
          return;
        } else if (!event.target.closest(".seg-text, .t-input")) {
          ui.video.currentTime = segmentSeekTime(seg);
          updateCaption();
        }
        highlightSegment(index, { lang: lang, scrollTimeline: true });
      });

      ui.segList.addEventListener("focusin", function (event) {
        var li = event.target.closest(".seg");
        if (!li) return;
        var isEditable = event.target.classList.contains("seg-text") || event.target.classList.contains("t-input");
        if (!isEditable) return;
        var info = segmentFromElement(li);
        if (!info.seg) return;
        setActiveLangFromElement(li);
        if (event.target.classList.contains("seg-text")) textEditSnapshot = snapshotSegments();
        var seekTime = segmentSeekTime(info.seg);
        if (Math.abs(ui.video.currentTime - seekTime) > 0.05) ui.video.currentTime = seekTime;
        highlightSegment(info.index, { lang: info.lang, scrollTimeline: true });
      });

      ui.segList.addEventListener("focusout", function (event) {
        if (!event.target.classList.contains("seg-text")) return;
        if (textEditSnapshot && snapshotSegments() !== textEditSnapshot) pushHistory(textEditSnapshot);
        textEditSnapshot = null;
      });

      if (ui.addSegBtn) {
        ui.addSegBtn.addEventListener("click", function () {
          var lang = getState().activeLang;
          var segments = segmentsForLang(lang);
          var t = ui.video.currentTime || 0;
          var before = snapshotSegments();
          segments.push({ start: t, end: t + 2, text: "" });
          segments.sort(function (a, b) { return a.start - b.start; });
          pushHistory(before);
          renderSegments();
          var createdIdx = segments.findIndex(function (s) { return s.start === t; });
          if (createdIdx >= 0) {
            var ta = $('.seg[data-lang="' + lang + '"][data-index="' + createdIdx + '"] .seg-text', ui.segList);
            if (ta) ta.focus();
          }
        });
      }

      // Add language button
      if (ui.langAddBtn) {
        ui.langAddBtn.addEventListener("click", function () {
          showLangPicker(function onPick(lang) {
            if (!lang) return;
            var state = getState();
            if (state.orderedLangs.indexOf(lang) >= 0) { alert("Ese idioma ya existe"); return; }
            var before = snapshotSegments();
            var sourceLang = state.orderedLangs[0];
            var sourceSegs = state.segmentsByLang[sourceLang] || [];
            setSegmentsForLang(lang, sourceSegs.length > 0 ? copySegments(sourceSegs) : []);
            setOrderedLangs(state.orderedLangs.concat([lang]));
            setActiveLang(lang);
            pushHistory(before);
            renderTabs();
            renderSegments();
            updateCaption();
          });
        });
      }
    }

    function copySegments(segs) {
      return segs.map(function (s) { return { start: s.start, end: s.end, text: s.text }; });
    }

    var langPickerCb = null;
    function showLangPicker(onPick) {
      var overlay = document.getElementById("langPicker");
      var input = document.getElementById("langPickerInput");
      if (!overlay || !input) return;
      langPickerCb = null;
      overlay.hidden = false;
      overlay.style.display = "flex";
      input.value = "";
      input.focus();
      var btns = overlay.querySelectorAll("[data-lang]");
      btns.forEach(function (b) { b.style.display = "flex"; });
      langPickerCb = function (lang) {
        overlay.hidden = true;
        overlay.style.display = "";
        if (onPick) onPick(lang);
      };
    }
    document.addEventListener("click", function (e) {
      var overlay = document.getElementById("langPicker");
      if (!overlay || overlay.hidden) return;
      var btn = e.target.closest("[data-lang]");
      if (btn && langPickerCb) { langPickerCb(btn.dataset.lang); return; }
      if (e.target === overlay && langPickerCb) { langPickerCb(""); return; }
    });
    document.addEventListener("input", function (e) {
      if (e.target.id !== "langPickerInput") return;
      var q = e.target.value.toLowerCase().trim();
      var overlay = document.getElementById("langPicker");
      if (!overlay) return;
      var btns = overlay.querySelectorAll("[data-lang]");
      btns.forEach(function (b) {
        var match = !q || b.textContent.toLowerCase().indexOf(q) >= 0 || b.dataset.lang.indexOf(q) >= 0;
        b.style.display = match ? "flex" : "none";
      });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Enter" && e.key !== "Escape") return;
      var overlay = document.getElementById("langPicker");
      if (!overlay || overlay.hidden) return;
      if (e.key === "Escape") { if (langPickerCb) langPickerCb(""); return; }
      if (e.key === "Enter") {
        e.preventDefault();
        var input = document.getElementById("langPickerInput");
        if (!input) return;
        var allBtns = overlay.querySelectorAll("[data-lang]");
        var visible = Array.prototype.filter.call(allBtns, function (b) { return b.style.display !== "none"; });
        if (visible.length === 1 && langPickerCb) { langPickerCb(visible[0].dataset.lang); return; }
        var val = input.value.trim().toLowerCase();
        if (/^[a-z]{2,3}(-[a-z]{2,4})?$/.test(val) && langPickerCb) { langPickerCb(val); }
      }
    });

    return {
      renderSegments: renderSegments,
      renderTabs: renderTabs,
      wireSegmentEditor: wireSegmentEditor,
      segmentsForLang: segmentsForLang,
    };
  }

  return { create: create };
})();
