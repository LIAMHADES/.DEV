// Interactive timeline with zoom, drag blocks, scrub, multi-track
window.Timeline = (function () {
  var $ = SubtitleDOM.$;
  var $$ = SubtitleDOM.$$;
  var esc = SubtitleDOM.escapeHtml;
  var fc = SubtitleUtils.formatClock;

  var TL_MIN_DUR = 0.3;
  var TL_HEADER_H = 26;
  var TL_ROW_H = 40;
  var TL_SCROLL_PAD = 8;
  var TL_MIN_ZOOM = 8;
  var TL_MAX_ZOOM = 300;
  var SCRUB_SEEK_MIN_INTERVAL = 45;
  var SCRUB_SEEK_EPSILON = 0.025;

  function create(options) {
    var ui = options.ui;
    var currentSegments = options.currentSegments;
    var visibleTracks = options.visibleTracks;
    var activeLang = options.activeLang;
    var setActiveLang = options.setActiveLang;
    var renderTabs = options.renderTabs;
    var renderCaptions = options.renderCaptions;
    var toggleTrackHidden = options.toggleTrackHidden;
    var toggleTrackLocked = options.toggleTrackLocked;
    var snapshotSegments = options.snapshotSegments;
    var pushHistory = options.pushHistory;
    var renderSegments = options.renderSegments;

    var tlPxPerSec = 10;
    var tlDuration = 0;
    var tlDrag = null;
    var scrubbing = false;
    var scrubRaf = 0;
    var scrubSeekRaf = 0;
    var scrubSeekTimer = 0;
    var scrubTargetT = 0;
    var scrubResumePlayback = false;
    var lastScrubSeekAt = 0;
    var playheadRaf = 0;
    var phAnchorMedia = 0;
    var phAnchorWall = 0;

    function getTracks() {
      var tracks = (visibleTracks && visibleTracks().filter(function (t) { return t.segments.length; })) || [];
      if (tracks.length) return tracks;
      return [{ lang: activeLang ? activeLang() : "", label: "", segments: currentSegments() }];
    }

    function segmentsForLang(lang) {
      var t = getTracks().find(function (tr) { return tr.lang === lang; });
      return t ? t.segments : currentSegments();
    }

    function trackForLang(lang) {
      return getTracks().find(function (tr) { return tr.lang === lang; });
    }

    function activeTrackLang() {
      return activeLang ? activeLang() : (getTracks()[0] || {}).lang || "";
    }

    function activateTrack(lang) {
      if (!lang || activeTrackLang() === lang) return;
      setActiveLang && setActiveLang(lang);
      renderTabs && renderTabs();
    }

    function segmentSeekTime(seg) {
      var start = Math.max(0, Number(seg.start) || 0);
      var end = isFinite(seg.end) ? Number(seg.end) : start + 0.5;
      return Math.min(start + 0.001, Math.max(start, end - 0.001));
    }

    function tlTotalDuration() {
      var segEnd = getTracks().reduce(function (max, track) {
        var last = track.segments[track.segments.length - 1];
        return Math.max(max, last ? last.end : 0);
      }, 0);
      return Math.max(tlDuration, segEnd, 1);
    }

    function renderTimeline() {
      if (!ui.timelineBlocks) return;
      var tracks = getTracks();
      var dur = tlTotalDuration();
      ui.timelineTrack.style.width = (dur * tlPxPerSec) + "px";
      if (ui.timeline) ui.timeline.classList.toggle("is-multitrack", tracks.length > 1);
      var blocksHeight = tracks.length * TL_ROW_H;
      ui.timelineBlocks.style.height = blocksHeight + "px";
      ui.timelineTrack.style.height = (TL_HEADER_H + blocksHeight) + "px";
      ui.timelineScroll.style.height = (TL_HEADER_H + blocksHeight + TL_SCROLL_PAD) + "px";

      var step = 1;
      if (tlPxPerSec < 10) step = 30;
      else if (tlPxPerSec < 22) step = 10;
      else if (tlPxPerSec < 45) step = 5;
      else if (tlPxPerSec < 90) step = 2;

      var ruler = "";
      for (var t = 0; t <= dur + 0.001; t += step) {
        var left = t * tlPxPerSec;
        ruler += '<span class="tl-tick" style="left:' + left + 'px"><i></i><b>' + fc(t) + '</b></span>';
      }
      ui.timelineRuler.innerHTML = ruler;

      ui.timelineBlocks.innerHTML = "";
      tracks.forEach(function (track, trackIndex) {
        var row = document.createElement("div");
        row.className = "tl-track-row";
        row.dataset.lang = track.lang;
        row.classList.toggle("is-hidden", !!track.hidden);
        row.classList.toggle("is-locked", !!track.locked);
        row.style.top = (trackIndex * TL_ROW_H) + "px";
        if (track.label) {
          var controls = document.createElement("div");
          controls.className = "tl-track-controls";
          controls.innerHTML =
            '<button class="tl-track-btn" type="button" data-action="visibility" title="' + (track.hidden ? "Mostrar" : "Ocultar") + ' track">' +
            '<svg viewBox="0 0 16 16"><path d="M1.5 8s2.4-4 6.5-4 6.5 4 6.5 4-2.4 4-6.5 4-6.5-4-6.5-4Z"/><circle cx="8" cy="8" r="1.8"/></svg>' +
            '</button>' +
            '<button class="tl-track-btn" type="button" data-action="lock" title="' + (track.locked ? "Desbloquear" : "Bloquear") + ' track">' +
            '<svg viewBox="0 0 16 16"><path d="M4.5 7V5.7a3.5 3.5 0 017 0V7"/><rect x="3.5" y="7" width="9" height="6.5" rx="1.4"/></svg>' +
            '</button>' +
            '<span class="tl-track-label">' + esc(track.label) + '</span>';
          row.appendChild(controls);
        }
        track.segments.forEach(function (seg, index) {
          var block = document.createElement("div");
          block.className = "tl-block";
          block.classList.toggle("is-hidden", !!track.hidden);
          block.classList.toggle("is-locked", !!track.locked);
          block.dataset.lang = track.lang;
          block.dataset.index = String(index);
          block.style.left = (seg.start * tlPxPerSec) + "px";
          block.style.width = Math.max(TL_MIN_DUR, seg.end - seg.start) * tlPxPerSec + "px";
          block.innerHTML =
            '<span class="tl-handle tl-handle-l" data-edge="start"></span>' +
            '<span class="tl-block-label">' + esc(seg.text || "—") + '</span>' +
            '<span class="tl-handle tl-handle-r" data-edge="end"></span>';
          row.appendChild(block);
        });
        ui.timelineBlocks.appendChild(row);
      });
      updateTimelinePlayhead();
    }

    function zoomTimeline(scale, anchorClientX) {
      var next = Math.max(TL_MIN_ZOOM, Math.min(TL_MAX_ZOOM, tlPxPerSec * scale));
      if (next === tlPxPerSec) return;
      var view = ui.timelineScroll;
      var anchorTime = null, anchorOffset = 0;
      if (view && typeof anchorClientX === "number") {
        var rect = view.getBoundingClientRect();
        anchorOffset = anchorClientX - rect.left;
        anchorTime = (view.scrollLeft + anchorOffset) / tlPxPerSec;
      }
      tlPxPerSec = next;
      renderTimeline();
      if (view && anchorTime !== null) {
        view.scrollLeft = Math.max(0, anchorTime * tlPxPerSec - anchorOffset);
      }
    }

    function updateTimelinePlayhead(timeOverride) {
      if (!ui.timelinePlayhead) return;
      var t = timeOverride != null ? timeOverride : (ui.video.currentTime || 0);
      var x = t * tlPxPerSec;
      ui.timelinePlayhead.style.transform = "translate3d(" + x + "px,0,0)";
      if (ui.tlClock) ui.tlClock.textContent = fc(t) + " / " + fc(tlTotalDuration());
      if (!ui.video.paused && ui.timelineScroll) {
        var view = ui.timelineScroll;
        if (x < view.scrollLeft + 60 || x > view.scrollLeft + view.clientWidth - 60) {
          view.scrollLeft = x - view.clientWidth * 0.4;
        }
      }
    }

    function setTimelineActive(idx, lang) {
      lang = lang || activeTrackLang();
      if (!ui.timelineBlocks) return;
      $$(".tl-block.is-active", ui.timelineBlocks).forEach(function (el) { el.classList.remove("is-active"); });
      if (idx >= 0) {
        var block = $('.tl-block[data-lang="' + lang + '"][data-index="' + idx + '"]', ui.timelineBlocks);
        if (block) block.classList.add("is-active");
      }
    }

    function clearScrubSeekQueue() {
      if (scrubSeekRaf) { cancelAnimationFrame(scrubSeekRaf); scrubSeekRaf = 0; }
      if (scrubSeekTimer) { window.clearTimeout(scrubSeekTimer); scrubSeekTimer = 0; }
    }

    function setVideoTimeForScrub(time, force) {
      var video = ui.video;
      var dur = tlTotalDuration();
      var target = Math.max(0, Math.min(dur, time));
      if (!force && Math.abs((video.currentTime || 0) - target) < SCRUB_SEEK_EPSILON) return;
      video.currentTime = target;
      lastScrubSeekAt = performance.now();
    }

    function scheduleScrubVideoSeek(force) {
      if (force) { clearScrubSeekQueue(); setVideoTimeForScrub(scrubTargetT, true); return; }
      if (!scrubbing || ui.video.seeking) return;
      if (Math.abs((ui.video.currentTime || 0) - scrubTargetT) < SCRUB_SEEK_EPSILON) return;
      var wait = Math.max(0, SCRUB_SEEK_MIN_INTERVAL - (performance.now() - lastScrubSeekAt));
      if (wait > 0) {
        if (!scrubSeekTimer) scrubSeekTimer = window.setTimeout(function () { scrubSeekTimer = 0; scheduleScrubVideoSeek(); }, wait);
        return;
      }
      if (scrubSeekRaf) return;
      scrubSeekRaf = requestAnimationFrame(function () {
        scrubSeekRaf = 0;
        if (!scrubbing || ui.video.seeking) return;
        setVideoTimeForScrub(scrubTargetT);
      });
    }

    function scheduleScrubFrame() {
      if (scrubRaf) return;
      scrubRaf = requestAnimationFrame(function () {
        scrubRaf = 0;
        updateCaption(scrubTargetT);
        scheduleScrubVideoSeek();
      });
    }

    function scrubToClientX(clientX) {
      var rect = ui.timelineTrack.getBoundingClientRect();
      var dur = tlTotalDuration();
      scrubTargetT = Math.max(0, Math.min(dur, (clientX - rect.left) / tlPxPerSec));
      scheduleScrubFrame();
    }

    function beginScrub(event) {
      scrubbing = true;
      scrubResumePlayback = !ui.video.paused;
      if (scrubResumePlayback) ui.video.pause();
      cancelAnimationFrame(playheadRaf);
      playheadRaf = 0;
      if (ui.timeline) ui.timeline.classList.add("is-scrubbing");
      ui.timelineTrack.setPointerCapture && ui.timelineTrack.setPointerCapture(event.pointerId);
      event.preventDefault();
      scrubToClientX(event.clientX);
    }

    function endScrub() {
      if (!scrubbing) return;
      scrubbing = false;
      if (scrubRaf) { cancelAnimationFrame(scrubRaf); scrubRaf = 0; }
      scheduleScrubVideoSeek(true);
      updateCaption();
      reanchorPlayhead();
      if (scrubResumePlayback) ui.video.play().catch(function () {});
      scrubResumePlayback = false;
      if (ui.timeline) ui.timeline.classList.remove("is-scrubbing");
    }

    function endTimelineDrag() {
      if (!tlDrag) return;
      var block = tlDrag.block, moved = tlDrag.moved, seg = tlDrag.seg, index = tlDrag.index, lang = tlDrag.lang, before = tlDrag.before;
      block.classList.remove("is-dragging");
      tlDrag = null;
      if (moved) pushHistory(before);
      var segments = segmentsForLang(lang);
      segments.sort(function (a, b) { return a.start - b.start; });
      renderSegments();
      if (!moved) {
        activateTrack(lang);
        ui.video.currentTime = segmentSeekTime(seg);
        var newIdx = segments.indexOf(seg);
        highlightSegment(newIdx >= 0 ? newIdx : index, { lang: lang, scrollSidebar: true });
      }
      updateCaption();
    }

    function togglePlay() {
      if (ui.video.paused) {
        ui.video.play().catch(function () {});
        if (ui.tlPlay) ui.tlPlay.textContent = "⏸";
      } else {
        ui.video.pause();
        if (ui.tlPlay) ui.tlPlay.textContent = "▶";
      }
    }

    function reanchorPlayhead() {
      phAnchorMedia = ui.video.currentTime || 0;
      phAnchorWall = performance.now();
    }

    function playheadLoop() {
      var real = ui.video.currentTime || 0;
      var rate = ui.video.playbackRate || 1;
      var predicted = phAnchorMedia + ((performance.now() - phAnchorWall) / 1000) * rate;
      if (Math.abs(real - predicted) > 0.18 || real < predicted - 0.03) { reanchorPlayhead(); predicted = real; }
      updateCaption(Math.min(predicted, tlTotalDuration()));
      playheadRaf = requestAnimationFrame(playheadLoop);
    }

    function scrollTimelineToBlock(index, lang) {
      lang = lang || activeTrackLang();
      var view = ui.timelineScroll;
      var seg = segmentsForLang(lang)[index];
      if (!view || !seg) return;
      var left = seg.start * tlPxPerSec;
      var right = Math.max(left + TL_MIN_DUR * tlPxPerSec, seg.end * tlPxPerSec);
      if (left < view.scrollLeft + 8 || right > view.scrollLeft + view.clientWidth - 8) {
        view.scrollLeft = Math.max(0, left - view.clientWidth * 0.3);
      }
    }

    function highlightSegment(index, opts) {
      opts = opts || {};
      var lang = opts.lang || activeTrackLang();
      setTimelineActive(index, lang);
      if (opts.touchSidebar !== false) {
        $$(".seg.is-active", ui.segList).forEach(function (el) { el.classList.remove("is-active"); });
        if (index >= 0) {
          var li = $('.seg[data-lang="' + lang + '"][data-index="' + index + '"]', ui.segList);
          if (li) { li.classList.add("is-active"); if (opts.scrollSidebar) li.scrollIntoView({ block: "nearest" }); }
        }
      }
      if (opts.scrollTimeline && index >= 0) scrollTimelineToBlock(index, lang);
    }

    function updateCaption(timeOverride) {
      var frameOnly = typeof timeOverride === "number";
      var current = frameOnly ? timeOverride : ui.video.currentTime;
      updateTimelinePlayhead(current);
      var tracks = getTracks();
      var editing = document.activeElement && document.activeElement.tagName === "TEXTAREA";
      if (!tracks.length || !ui.video.duration) {
        if (renderCaptions) renderCaptions([], current);
        if (!frameOnly) highlightSegment(-1, { touchSidebar: !editing });
        return;
      }
      var al = activeTrackLang();
      var captionTracks = tracks.filter(function (tr) { return !tr.hidden; }).map(function (tr) {
        var seg = tr.segments.find(function (s) { return current >= s.start && current <= s.end; });
        return { lang: tr.lang, label: tr.label, role: tr.role, text: seg ? seg.text : "", segment: seg };
      }).filter(function (tr) { return tr.text.trim(); });
      var activeTrack = tracks.find(function (tr) { return tr.lang === al; }) || tracks[0];
      var idx = activeTrack.segments.findIndex(function (s) { return current >= s.start && current <= s.end; });
      if (renderCaptions) renderCaptions(captionTracks, current);
      if (!frameOnly) highlightSegment(idx, { lang: activeTrack.lang, touchSidebar: !editing, scrollSidebar: !editing });
    }

    function updateCaptionFromMediaEvent() { if (!scrubbing) updateCaption(); }

    function wireTimeline() {
      ui.timelineTrack && ui.timelineTrack.addEventListener("pointerdown", function (event) {
        if (event.target.closest(".tl-block, .tl-track-controls")) return;
        beginScrub(event);
      });
      ui.timelineTrack && ui.timelineTrack.addEventListener("pointermove", function (event) {
        if (scrubbing) scrubToClientX(event.clientX);
      });
      ui.timelineTrack && ui.timelineTrack.addEventListener("pointerup", endScrub);
      ui.timelineTrack && ui.timelineTrack.addEventListener("pointercancel", endScrub);

      ui.timelineBlocks && ui.timelineBlocks.addEventListener("pointerdown", function (event) {
        if (event.target.closest(".tl-track-controls")) { event.stopPropagation(); return; }
        var block = event.target.closest(".tl-block");
        if (!block) return;
        var handle = event.target.closest(".tl-handle");
        var index = Number(block.dataset.index);
        var lang = block.dataset.lang || activeTrackLang();
        var seg = segmentsForLang(lang)[index];
        if (!seg) return;
        event.preventDefault();
        activateTrack(lang);
        var trackRec = trackForLang(lang);
        if (trackRec && trackRec.locked) {
          ui.video.currentTime = segmentSeekTime(seg);
          highlightSegment(index, { lang: lang, scrollSidebar: true });
          updateCaption();
          return;
        }
        tlDrag = {
          index: index, lang: lang, seg: seg, block: block,
          mode: handle ? handle.dataset.edge : "move",
          startX: event.clientX, origStart: seg.start, origEnd: seg.end,
          moved: false, before: snapshotSegments(),
        };
        block.setPointerCapture && block.setPointerCapture(event.pointerId);
        block.classList.add("is-dragging");
      });

      ui.timelineBlocks && ui.timelineBlocks.addEventListener("pointermove", function (event) {
        if (!tlDrag) return;
        var dx = event.clientX - tlDrag.startX;
        var dt = dx / tlPxPerSec;
        if (Math.abs(dx) > 3) tlDrag.moved = true;
        var dur0 = tlDrag.origEnd - tlDrag.origStart;
        var seg = tlDrag.seg, mode = tlDrag.mode;
        if (mode === "move") {
          var ns = Math.max(0, tlDrag.origStart + dt);
          seg.start = ns;
          seg.end = ns + dur0;
        } else if (mode === "start") {
          seg.start = Math.max(0, Math.min(tlDrag.origEnd - TL_MIN_DUR, tlDrag.origStart + dt));
        } else {
          seg.end = Math.max(tlDrag.origStart + TL_MIN_DUR, tlDrag.origEnd + dt);
        }
        tlDrag.block.style.left = (seg.start * tlPxPerSec) + "px";
        tlDrag.block.style.width = ((seg.end - seg.start) * tlPxPerSec) + "px";
        var li = $('.seg[data-lang="' + tlDrag.lang + '"][data-index="' + tlDrag.index + '"]', ui.segList);
        if (li) {
          var s = $(".t-start", li); if (s) s.value = fc(seg.start);
          var e = $(".t-end", li); if (e) e.value = fc(seg.end);
        }
        updateCaption();
      });

      ui.timelineBlocks && ui.timelineBlocks.addEventListener("pointerup", endTimelineDrag);
      ui.timelineBlocks && ui.timelineBlocks.addEventListener("pointercancel", endTimelineDrag);

      ui.timelineBlocks && ui.timelineBlocks.addEventListener("click", function (event) {
        var button = event.target.closest(".tl-track-btn");
        if (!button) return;
        event.preventDefault(); event.stopPropagation();
        var row = button.closest(".tl-track-row");
        var lang = row && row.dataset.lang;
        if (!lang) return;
        if (button.dataset.action === "visibility") toggleTrackHidden && toggleTrackHidden(lang);
        else if (button.dataset.action === "lock") toggleTrackLocked && toggleTrackLocked(lang);
      });

      if (ui.tlPlay) ui.tlPlay.addEventListener("click", togglePlay);
      if (ui.video) {
        ui.video.addEventListener("click", togglePlay);
        ui.video.addEventListener("play", function () {
          if (ui.timeline) ui.timeline.classList.add("is-playing");
          if (ui.tlPlay) ui.tlPlay.textContent = "⏸";
          cancelAnimationFrame(playheadRaf);
          reanchorPlayhead();
          playheadLoop();
        });
        ui.video.addEventListener("pause", function () {
          if (ui.timeline) ui.timeline.classList.remove("is-playing");
          if (ui.tlPlay) ui.tlPlay.textContent = "▶";
          cancelAnimationFrame(playheadRaf);
          playheadRaf = 0;
          updateTimelinePlayhead();
        });
        ui.video.addEventListener("seeked", reanchorPlayhead);
        ui.video.addEventListener("seeked", function () { if (scrubbing) scheduleScrubVideoSeek(); });
        ui.video.addEventListener("ratechange", reanchorPlayhead);
        ui.video.addEventListener("timeupdate", updateCaptionFromMediaEvent);
        ui.video.addEventListener("seeked", updateCaptionFromMediaEvent);
        ui.video.addEventListener("loadedmetadata", function () {
          tlDuration = isFinite(ui.video.duration) ? ui.video.duration : 0;
          renderTimeline();
        });
      }

      if (ui.timelineScroll) ui.timelineScroll.addEventListener("wheel", handleWheelZoom, { passive: false });
      if (ui.tlZoomIn) ui.tlZoomIn.addEventListener("click", function () { zoomTimeline(1.4); });
      if (ui.tlZoomOut) ui.tlZoomOut.addEventListener("click", function () { zoomTimeline(1 / 1.4); });
    }

    function handleWheelZoom(event) {
      if (!event.metaKey) return;
      var deltaY = event.deltaMode === 1 ? event.deltaY * 16 : event.deltaY;
      if (!deltaY) return;
      event.preventDefault();
      var clamped = Math.max(-500, Math.min(500, deltaY));
      zoomTimeline(Math.pow(2, -clamped / 500), event.clientX);
    }

    wireTimeline();

    return {
      renderTimeline: renderTimeline,
      highlightSegment: highlightSegment,
      updateCaption: updateCaption,
      updateTimelinePlayhead: updateTimelinePlayhead,
    };
  }

  return { create: create };
})();
