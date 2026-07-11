// Subtitle utilities — format, parse, build SRT
window.SubtitleUtils = (function () {
  function formatClock(seconds) {
    var c = Math.max(0, isFinite(seconds) ? seconds : 0);
    var m = Math.floor(c / 60);
    var s = Math.floor(c % 60);
    var cs = Math.round((c - Math.floor(c)) * 100);
    var p = function (n) { return String(n).padStart(2, "0"); };
    return m + ":" + p(s) + "." + p(cs);
  }

  function formatSrtTime(seconds) {
    var c = Math.max(0, isFinite(seconds) ? seconds : 0);
    var h = Math.floor(c / 3600);
    var m = Math.floor((c % 3600) / 60);
    var s = Math.floor(c % 60);
    var ms = Math.floor((c - Math.floor(c)) * 1000);
    var p = function (n, l) { return String(n).padStart(l || 2, "0"); };
    return p(h) + ":" + p(m) + ":" + p(s) + "," + p(ms, 3);
  }

  function parseClock(value) {
    var match = String(value).trim().match(/^(\d+):(\d{1,2})(?:[.,](\d{1,3}))?$/);
    if (!match) return null;
    var m = Number(match[1]);
    var s = Number(match[2]);
    var frac = match[3] ? Number("0." + match[3]) : 0;
    return m * 60 + s + frac;
  }

  function buildSrt(segments) {
    return segments
      .map(function (s, i) {
        return (i + 1) + "\n" + formatSrtTime(s.start) + " --> " + formatSrtTime(s.end) + "\n" + s.text;
      })
      .join("\n\n");
  }

  return { formatClock: formatClock, formatSrtTime: formatSrtTime, parseClock: parseClock, buildSrt: buildSrt };
})();
