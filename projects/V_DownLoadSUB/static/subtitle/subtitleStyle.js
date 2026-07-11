// Caption style engine with 7 presets, drag/resize, word highlight, snap guides, keyboard
window.CaptionStyle = (function () {
  var $ = SubtitleDOM.$;
  var $$ = SubtitleDOM.$$;

  var FONT_STACKS = {
    sans: '"Outfit", "Segoe UI", system-ui, sans-serif',
    serif: 'Georgia, "Times New Roman", serif',
    rounded: '"Quicksand", "Trebuchet MS", system-ui, sans-serif',
    condensed: '"Arial Narrow", "Roboto Condensed", system-ui, sans-serif',
    mono: '"JetBrains Mono", ui-monospace, "SF Mono", monospace',
  };

  var CAPTION_PRESETS = [
    { id: "default",  name: "Default",  s: { font:"sans", size:1,    color:"#ffffff", weight:600, italic:false, align:"center", bgEnabled:true,  bgColor:"#06080b", bgOpacity:0.84, outline:false }},
    { id: "clean",    name: "Clean",    s: { font:"sans", size:1,    color:"#ffffff", weight:600, italic:false, align:"center", bgEnabled:false, bgColor:"#06080b", bgOpacity:0.84, outline:true  }},
    { id: "bold",     name: "Bold",     s: { font:"sans", size:1.12, color:"#ffffff", weight:700, italic:false, align:"center", bgEnabled:true,  bgColor:"#000000", bgOpacity:1,    outline:false }},
    { id: "pop",      name: "Pop",      s: { font:"rounded", size:1.06, color:"#fde047", weight:700, italic:false, align:"center", bgEnabled:false, bgColor:"#000000", bgOpacity:0.84, outline:true }},
    { id: "neon",     name: "Neon",     s: { font:"sans", size:1,    color:"#b8f060", weight:700, italic:false, align:"center", bgEnabled:true,  bgColor:"#06080b", bgOpacity:0.55, outline:false }},
    { id: "classic",  name: "Classic",  s: { font:"serif", size:1,   color:"#ffffff", weight:600, italic:false, align:"center", bgEnabled:false, bgColor:"#06080b", bgOpacity:0.84, outline:true }},
    { id: "terminal", name: "Terminal", s: { font:"mono",  size:0.92, color:"#ffffff", weight:600, italic:false, align:"center", bgEnabled:true,  bgColor:"#0a0d12", bgOpacity:0.9,  outline:false }},
  ];

  var defaultStyle = {
    font: "sans", size: 1, color: "#ffffff", weight: 600, italic: false, align: "center",
    bgEnabled: true, bgColor: "#06080b", bgOpacity: 0.84, outline: false,
    wordHighlight: false, position: "bottom", customX: 50, customY: 88,
  };

  var activePresetId = "default";
  var activeRole = "default";
  var activeLang = "";
  var stylesByTrack = {};
  var presetIdsByTrack = {};
  var dragState = null;
  var resizeState = null;
  var ui = {};
  var CAPTION_SIZE_MIN = 0.7;
  var CAPTION_SIZE_MAX = 1.6;
  var CAPTION_RESIZE_HIT_SIZE = 22;
  var SNAP_DISTANCE = 4;

  var CUSTOM_GUIDES = { x: 50, top: 12, middle: 50, bottom: 88 };
  var POSITION_POINTS = {
    top: { x: 50, y: 8 }, middle: { x: 50, y: 50 }, bottom: { x: 50, y: 92 }
  };

  // ─── Utilities ───────────────────────────────────────────────────────────────
  function hexToRgba(hex, alpha) {
    var h = String(hex || "#000000").replace("#", "");
    if (h.length === 3) h = h.split("").map(function (c) { return c + c; }).join("");
    var n = parseInt(h, 16);
    return "rgba(" + ((n >> 16) & 255) + "," + ((n >> 8) & 255) + "," + (n & 255) + "," + (alpha || 1) + ")";
  }

  function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

  function applyVisualStyle(el, s) {
    el.style.fontFamily = FONT_STACKS[s.font] || FONT_STACKS.sans;
    el.style.fontWeight = String(s.weight || 600);
    el.style.fontStyle = s.italic ? "italic" : "normal";
    el.style.textAlign = s.align || "center";
    el.style.color = s.color || "#ffffff";
    el.style.background = s.bgEnabled ? hexToRgba(s.bgColor, s.bgOpacity) : "transparent";
    el.style.textShadow = s.outline
      ? "0 1px 2px rgba(0,0,0,.95), 0 0 5px rgba(0,0,0,.85), 0 0 1px rgba(0,0,0,.9)"
      : s.bgEnabled ? "none" : "0 1px 3px rgba(0,0,0,.85)";
  }

  function trackStyleKey(role, lang) { return (role || "default") + ":" + (lang || "__default"); }

  function getStyle(role, lang) {
    var key = trackStyleKey(role, lang);
    if (!stylesByTrack[key]) stylesByTrack[key] = JSON.parse(JSON.stringify(defaultStyle));
    return stylesByTrack[key];
  }

  function activeStyle() { return getStyle(activeRole, activeLang); }
  function boxStyle(el) { return getStyle(el.dataset.role || "default", el.dataset.lang || ""); }

  // ─── Word highlight helpers ──────────────────────────────────────────────────
  function tokenizeText(text) {
    if (/\s/.test(text)) return text.split(/\s+/).filter(Boolean);
    if (/[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff\uac00-\ud7af]/.test(text)) return Array.from(text);
    return text ? [text] : [];
  }

  function appendWordText(text, word) {
    if (!text) return word;
    if (/^[,.;:!?%)\]}\u2026]/.test(word) || /[(\[{]$/.test(text)) return text + word;
    var cjk = /[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff\uac00-\ud7af]/;
    if (cjk.test(text.slice(-1)) && cjk.test(word.charAt(0))) return text + word;
    return text + " " + word;
  }

  function wordsText(words) { return words.reduce(function (text, w) { return appendWordText(text, w.text); }, "").trim(); }

  function estimatedWordsForSegment(seg) {
    var text = String(seg.text || "").trim();
    if (!text) return [];
    var textWords = tokenizeText(text);

    if (seg.words && seg.words.length && wordsText(seg.words).replace(/\s+/g, " ") === text.replace(/\s+/g, " ")) {
      return seg.words;
    }

    var start = isFinite(seg.start) ? seg.start : 0;
    var end = Math.max(start + 0.35, isFinite(seg.end) ? seg.end : start + 2);
    var duration = end - start;
    var totalWeight = textWords.reduce(function (sum, w) { return sum + Math.max(1, w.replace(/[^\p{L}\p{N}]/gu, "").length); }, 0);
    var cursor = start;

    return textWords.map(function (word, idx) {
      var weight = Math.max(1, word.replace(/[^\p{L}\p{N}]/gu, "").length);
      var isLast = idx === textWords.length - 1;
      var wordEnd = isLast ? end : cursor + (duration * weight) / totalWeight;
      var result = { start: cursor, end: Math.max(cursor + 0.05, wordEnd), text: word };
      cursor = result.end;
      return result;
    });
  }

  // ─── Caption layer ───────────────────────────────────────────────────────────
  function captionLayerRect() {
    var layer = ui.caption, vp = ui.videoPreview;
    if (!layer) return vp.getBoundingClientRect();
    var pr = vp.getBoundingClientRect();
    var vw = Number(ui.video.videoWidth) || 0, vh = Number(ui.video.videoHeight) || 0;
    var left = 0, top = 0, w = pr.width, h = pr.height;
    if (pr.width && pr.height && vw && vh) {
      var previewRatio = pr.width / pr.height, videoRatio = vw / vh;
      if (previewRatio > videoRatio) {
        h = pr.height; w = h * videoRatio; left = (pr.width - w) / 2;
      } else {
        w = pr.width; h = w / videoRatio; top = (pr.height - h) / 2;
      }
    }
    layer.style.left = left + "px"; layer.style.top = top + "px";
    layer.style.width = w + "px"; layer.style.height = h + "px";
    return layer.getBoundingClientRect();
  }

  function applyCaptionBoxStyle(box) {
    var s = boxStyle(box);
    applyVisualStyle(box, s);
    box.style.fontSize = "clamp(" + Math.round(13 * s.size) + "px," + (2.4 * s.size).toFixed(2) + "vw," + Math.round(28 * s.size) + "px)";
    box.style.padding = s.bgEnabled ? "0.22rem 0.6rem" : "0";
    if (s.position === "custom") {
      box.style.left = clamp(Number(s.customX) || 50, 0, 100) + "%";
      box.style.top = clamp(Number(s.customY) || 50, 0, 100) + "%";
      box.style.transform = "translate(-50%,-50%)";
    } else {
      var pt = POSITION_POINTS[s.position] || POSITION_POINTS.bottom;
      box.style.left = pt.x + "%"; box.style.top = pt.y + "%";
      box.style.transform = s.position === "top" ? "translate(-50%,0)" : s.position === "bottom" ? "translate(-50%,-100%)" : "translate(-50%,-50%)";
    }
  }

  function applyCaptionStyle() {
    $$(".caption-box", ui.caption).forEach(function (box) { applyCaptionBoxStyle(box); });
  }

  // ─── Word highlight rendering ────────────────────────────────────────────────
  function renderCaptionText(box, track, time) {
    var s = boxStyle(box);
    box.classList.toggle("is-word-highlight", !!s.wordHighlight);
    if (!s.wordHighlight || !track.segment) { box.textContent = track.text; return; }

    var words = estimatedWordsForSegment(track.segment);
    if (!words.length) { box.textContent = track.text; return; }

    box.replaceChildren();
    words.forEach(function (word, index) {
      if (index > 0) box.appendChild(document.createTextNode(" "));
      var span = document.createElement("span");
      span.className = "caption-word";
      span.classList.toggle("is-spoken", time >= word.start);
      span.textContent = word.text;
      box.appendChild(span);
    });
  }

  // ─── Caption rendering ──────────────────────────────────────────────────────
  function renderCaptions(tracks, time) {
    captionLayerRect();
    time = time || 0;
    var wanted = {};

    tracks.forEach(function (track) {
      var role = track.role || "default";
      var key = role + ":" + track.lang;
      wanted[key] = true;

      var box = ui.caption.querySelector('.caption-box[data-key="' + CSS.escape(key) + '"]');
      if (!box) {
        box = document.createElement("div");
        box.className = "caption-box caption-box--" + role;
        box.dataset.key = key;
        box.dataset.role = role;
        box.dataset.lang = track.lang;
        box.role = "button";
        box.tabIndex = 0;
        ui.caption.appendChild(box);
      }

      renderCaptionText(box, track, time);
      box.hidden = !track.text.trim();
      applyCaptionBoxStyle(box);
    });

    $$(".caption-box", ui.caption).forEach(function (box) {
      if (!wanted[box.dataset.key || ""]) box.remove();
    });
  }

  // ─── Presets ─────────────────────────────────────────────────────────────────
  function renderPresets() {
    if (!ui.stylePresets) return;
    ui.stylePresets.innerHTML = "";
    CAPTION_PRESETS.forEach(function (p) {
      var on = p.id === activePresetId;
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "preset" + (on ? " is-on" : "");
      btn.title = p.name;
      var prev = document.createElement("span"); prev.className = "preset-prev";
      var inner = document.createElement("span"); inner.textContent = "Aa";
      applyVisualStyle(inner, p.s);
      inner.style.padding = p.s.bgEnabled ? "1px 6px" : "0";
      inner.style.borderRadius = "4px"; inner.style.fontSize = "13px";
      prev.appendChild(inner);
      var name = document.createElement("span"); name.className = "preset-name"; name.textContent = p.name;
      btn.append(prev, name);
      btn.addEventListener("click", function () { applyPreset(p); });
      ui.stylePresets.appendChild(btn);
    });
  }

  function applyPreset(p) {
    var s = activeStyle();
    Object.keys(p.s).forEach(function (k) { s[k] = p.s[k]; });
    activePresetId = p.id;
    presetIdsByTrack[trackStyleKey(activeRole, activeLang)] = p.id;
    applyCaptionStyle();
    syncStyleControls();
    renderPresets();
  }

  function setActiveTrack(role, lang) {
    activeRole = role || "default";
    activeLang = lang || "";
    activePresetId = presetIdsByTrack[trackStyleKey(activeRole, activeLang)] || "default";
    syncStyleControls();
    renderPresets();
  }

  function setPresetPosition(position) {
    var boxes = $$(".caption-box", ui.caption);
    var target = boxes.find(function (b) { return (b.dataset.role||"default") === activeRole && (b.dataset.lang||"") === activeLang; }) || boxes[0];
    if (position === "custom") {
      if (!target) return;
      var rect = target.getBoundingClientRect(), lr = captionLayerRect();
      var x = ((rect.left+rect.width/2 - lr.left)/lr.width)*100;
      var y = ((rect.top+rect.height/2 - lr.top)/lr.height)*100;
      var s = boxStyle(target);
      s.position = "custom"; s.customX = x; s.customY = y;
      activePresetId = "";
      syncStyleControls(); renderPresets();
    } else { activeStyle().position = position; syncStyleControls(); }
    applyCaptionStyle();
  }

  function syncStyleControls() {
    var c = activeStyle();
    if (ui.csFont) ui.csFont.value = c.font;
    if (ui.csSize) ui.csSize.value = String(c.size);
    if (ui.csColor) ui.csColor.value = c.color;
    if (ui.csBold) ui.csBold.checked = c.weight >= 700;
    if (ui.csItalic) ui.csItalic.checked = !!c.italic;
    if (ui.csOutline) ui.csOutline.checked = !!c.outline;
    if (ui.csWordHighlight) ui.csWordHighlight.checked = !!c.wordHighlight;
    if (ui.csBg) ui.csBg.checked = !!c.bgEnabled;
    if (ui.csBgColor) ui.csBgColor.value = c.bgColor;
    if (ui.csBgOpacity) ui.csBgOpacity.value = String(c.bgOpacity);
    if (ui.csBgColor) ui.csBgColor.disabled = !c.bgEnabled;
    if (ui.csBgOpacity) ui.csBgOpacity.disabled = !c.bgEnabled;
    $$("button", ui.csPosition).forEach(function (b) { b.classList.toggle("is-on", b.dataset.pos === c.position); });
    $$("button", ui.csAlign).forEach(function (b) { b.classList.toggle("is-on", b.dataset.align === (c.align || "center")); });
  }

  function onManualStyleChange() { activePresetId = ""; applyCaptionStyle(); renderPresets(); }

  // ─── Drag/resize helpers ─────────────────────────────────────────────────────
  function captionCenterPercent(el) {
    var lr = captionLayerRect();
    var r = el.getBoundingClientRect();
    if (!lr.width || !lr.height) { var s = boxStyle(el); return { x: Number(s.customX)||50, y: Number(s.customY)||88 }; }
    return { x: ((r.left+r.width/2-lr.left)/lr.width)*100, y: ((r.top+r.height/2-lr.top)/lr.height)*100 };
  }

  function clampCaptionPoint(el, x, y) {
    var lr = captionLayerRect(), r = el.getBoundingClientRect();
    var hx = lr.width ? (r.width/2/lr.width)*100 : 0;
    var hy = lr.height ? (r.height/2/lr.height)*100 : 0;
    return { x: clamp(x, hx, 100-hx), y: clamp(y, hy, 100-hy) };
  }

  function snapPoint(el, point) {
    var x = point.x, y = point.y, snapX = false, snapY = "";
    if (Math.abs(x - CUSTOM_GUIDES.x) <= SNAP_DISTANCE) { x = CUSTOM_GUIDES.x; snapX = true; }
    var yGuides = [["top",CUSTOM_GUIDES.top],["middle",CUSTOM_GUIDES.middle],["bottom",CUSTOM_GUIDES.bottom]];
    var found = yGuides.find(function (g) { return Math.abs(y - g[1]) <= SNAP_DISTANCE; });
    if (found) { snapY = found[0]; y = found[1]; }
    return { point: clampCaptionPoint(el, x, y), snapX: snapX, snapY: snapY };
  }

  function updateGuides(snapX, snapY) {
    if (!ui.captionGuides) return;
    ui.captionGuides.hidden = !dragState;
    ui.captionGuides.classList.toggle("show-x", snapX);
    ui.captionGuides.classList.toggle("show-top", snapY === "top");
    ui.captionGuides.classList.toggle("show-middle", snapY === "middle");
    ui.captionGuides.classList.toggle("show-bottom", snapY === "bottom");
  }

  function isCaptionResizeHit(event, box) {
    var r = box.getBoundingClientRect();
    return event.clientX >= r.right - CAPTION_RESIZE_HIT_SIZE && event.clientY >= r.bottom - CAPTION_RESIZE_HIT_SIZE;
  }

  function setCustomPosition(el, x, y) {
    var s = boxStyle(el);
    var pt = clampCaptionPoint(el, x, y);
    s.position = "custom"; s.customX = pt.x; s.customY = pt.y;
    activePresetId = "";
    applyCaptionBoxStyle(el);
    syncStyleControls(); renderPresets();
  }

  function pointerPoint(event) {
    var pr = captionLayerRect();
    var x = ((event.clientX - dragState.offsetX - pr.left) / pr.width) * 100;
    var y = ((event.clientY - dragState.offsetY - pr.top) / pr.height) * 100;
    return clampCaptionPoint(dragState.el, x, y);
  }

  // ─── Resize ──────────────────────────────────────────────────────────────────
  function startResize(event, box) {
    event.preventDefault();
    setActiveTrack(box.dataset.role || "default", box.dataset.lang || "");
    syncStyleControls();
    resizeState = { el:box, pointerId:event.pointerId, startClientX:event.clientX, startClientY:event.clientY, startSize:Number(boxStyle(box).size)||1, started:false };
    ui.videoPreview.classList.add("is-caption-resizing");
    box.setPointerCapture && box.setPointerCapture(event.pointerId);
    box.focus({ preventScroll:true });
  }

  function moveResize(event) {
    if (!resizeState || event.pointerId !== resizeState.pointerId) return;
    event.preventDefault();
    var moved = Math.abs(event.clientX - resizeState.startClientX) > 2 || Math.abs(event.clientY - resizeState.startClientY) > 2;
    if (!resizeState.started && !moved) return;
    if (!resizeState.started) { resizeState.started = true; activePresetId = ""; renderPresets(); }
    var pr = ui.videoPreview.getBoundingClientRect();
    var base = Math.max(1, Math.min(pr.width, pr.height));
    var diag = (event.clientX - resizeState.startClientX + event.clientY - resizeState.startClientY) / base;
    var s = boxStyle(resizeState.el);
    s.size = clamp(resizeState.startSize + diag * 2.25, CAPTION_SIZE_MIN, CAPTION_SIZE_MAX);
    applyCaptionBoxStyle(resizeState.el);
    syncStyleControls();
  }

  function endResize(event) {
    if (!resizeState || event.pointerId !== resizeState.pointerId) return;
    resizeState.el.releasePointerCapture && resizeState.el.releasePointerCapture(event.pointerId);
    resizeState = null;
    ui.videoPreview.classList.remove("is-caption-resizing");
    syncStyleControls();
  }

  // ─── Drag ────────────────────────────────────────────────────────────────────
  function startDrag(event) {
    var box = event.target.closest(".caption-box");
    if (event.button !== 0 || !box || !box.textContent.trim()) return;
    if (isCaptionResizeHit(event, box)) { startResize(event, box); return; }

    event.preventDefault();
    setActiveTrack(box.dataset.role || "default", box.dataset.lang || "");
    syncStyleControls();
    var cr = box.getBoundingClientRect(), cx = cr.left + cr.width/2, cy = cr.top + cr.height/2;
    dragState = { el:box, pointerId:event.pointerId, offsetX:event.clientX-cx, offsetY:event.clientY-cy, startClientX:event.clientX, startClientY:event.clientY, started:false };
    box.setPointerCapture && box.setPointerCapture(event.pointerId);
    box.focus({ preventScroll:true });
  }

  function moveDrag(event) {
    if (resizeState) { moveResize(event); return; }
    if (!dragState || event.pointerId !== dragState.pointerId) return;
    var moved = Math.abs(event.clientX-dragState.startClientX) > 3 || Math.abs(event.clientY-dragState.startClientY) > 3;
    if (!dragState.started && !moved) return;
    if (!dragState.started) {
      dragState.started = true;
      ui.videoPreview.classList.add("is-caption-dragging");
      var pt = captionCenterPercent(dragState.el);
      setCustomPosition(dragState.el, pt.x, pt.y);
      updateGuides();
    }
    var snapped = snapPoint(dragState.el, pointerPoint(event));
    var s = boxStyle(dragState.el);
    s.customX = snapped.point.x; s.customY = snapped.point.y;
    applyCaptionBoxStyle(dragState.el);
    updateGuides(snapped.snapX, snapped.snapY);
  }

  function endDrag(event) {
    if (resizeState) { endResize(event); return; }
    if (!dragState || event.pointerId !== dragState.pointerId) return;
    dragState.el.releasePointerCapture && dragState.el.releasePointerCapture(event.pointerId);
    var dragged = dragState.started;
    dragState = null;
    if (dragged) { ui.videoPreview.classList.remove("is-caption-dragging"); updateGuides(); syncStyleControls(); }
  }

  // ─── Keyboard ────────────────────────────────────────────────────────────────
  function moveWithKeyboard(event) {
    var box = event.target.closest(".caption-box");
    if (!box) return;
    setActiveTrack(box.dataset.role || "default", box.dataset.lang || "");
    var s = boxStyle(box);
    var delta = event.shiftKey ? 5 : 1;
    var pt = s.position === "custom" ? { x: Number(s.customX)||50, y: Number(s.customY)||88 } : captionCenterPercent(box);
    if (event.key === "ArrowLeft") pt.x -= delta;
    else if (event.key === "ArrowRight") pt.x += delta;
    else if (event.key === "ArrowUp") pt.y -= delta;
    else if (event.key === "ArrowDown") pt.y += delta;
    else return;
    event.preventDefault();
    setCustomPosition(box, pt.x, pt.y);
  }

  // ─── Wire ────────────────────────────────────────────────────────────────────
  function wireStyleControls(_ui) {
    ui = _ui;
    captionLayerRect();
    if (ui.video) {
      ui.video.addEventListener("loadedmetadata", captionLayerRect);
      ui.video.addEventListener("loadeddata", captionLayerRect);
    }
    window.addEventListener("resize", captionLayerRect);
    if ("ResizeObserver" in window) new ResizeObserver(captionLayerRect).observe(ui.videoPreview);

    if (ui.styleToggle) ui.styleToggle.addEventListener("click", function () {
      var open = ui.styleControls.hidden;
      ui.styleControls.hidden = !open;
      ui.styleToggle.setAttribute("aria-expanded", String(open));
      ui.styleToggle.classList.toggle("is-open", open);
    });

    ui.csFont && ui.csFont.addEventListener("change", function () { activeStyle().font = ui.csFont.value; onManualStyleChange(); });
    ui.csSize && ui.csSize.addEventListener("input", function () { activeStyle().size = Number(ui.csSize.value); onManualStyleChange(); });
    ui.csColor && ui.csColor.addEventListener("input", function () { activeStyle().color = ui.csColor.value; onManualStyleChange(); });
    ui.csBold && ui.csBold.addEventListener("change", function () { activeStyle().weight = ui.csBold.checked ? 700 : 600; onManualStyleChange(); });
    ui.csItalic && ui.csItalic.addEventListener("change", function () { activeStyle().italic = ui.csItalic.checked; onManualStyleChange(); });
    ui.csOutline && ui.csOutline.addEventListener("change", function () { activeStyle().outline = ui.csOutline.checked; onManualStyleChange(); });
    ui.csWordHighlight && ui.csWordHighlight.addEventListener("change", function () {
      Object.keys(stylesByTrack).forEach(function (k) { stylesByTrack[k].wordHighlight = ui.csWordHighlight.checked; });
      defaultStyle.wordHighlight = ui.csWordHighlight.checked;
      onManualStyleChange();
    });
    ui.csBg && ui.csBg.addEventListener("change", function () { activeStyle().bgEnabled = ui.csBg.checked; syncStyleControls(); onManualStyleChange(); });
    ui.csBgColor && ui.csBgColor.addEventListener("input", function () { activeStyle().bgColor = ui.csBgColor.value; onManualStyleChange(); });
    ui.csBgOpacity && ui.csBgOpacity.addEventListener("input", function () { activeStyle().bgOpacity = Number(ui.csBgOpacity.value); onManualStyleChange(); });
    ui.csPosition && ui.csPosition.addEventListener("click", function (e) {
      var b = e.target.closest("button[data-pos]"); if (!b) return;
      setPresetPosition(b.dataset.pos || "bottom");
    });
    ui.csAlign && ui.csAlign.addEventListener("click", function (e) {
      var b = e.target.closest("button[data-align]"); if (!b) return;
      activeStyle().align = b.dataset.align || "center";
      onManualStyleChange(); syncStyleControls();
    });

    // Drag/resize/pointer events on caption layer
    if (ui.caption) {
      ui.caption.addEventListener("pointerdown", startDrag);
      ui.caption.addEventListener("pointermove", moveDrag);
      ui.caption.addEventListener("pointerup", endDrag);
      ui.caption.addEventListener("pointercancel", endDrag);
      ui.caption.addEventListener("keydown", moveWithKeyboard);
    }
  }

  return {
    CAPTION_PRESETS: CAPTION_PRESETS, FONT_STACKS: FONT_STACKS,
    renderCaptions: renderCaptions,
    renderPresets: renderPresets,
    setActiveTrack: setActiveTrack,
    applyCaptionStyle: applyCaptionStyle,
    wireStyleControls: wireStyleControls,
    getStyle: getStyle,
  };
})();
