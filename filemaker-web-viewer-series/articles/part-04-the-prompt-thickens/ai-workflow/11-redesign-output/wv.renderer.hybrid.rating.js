/* ============================================================
   W V   H Y B R I D   R A T I N G   L A N D S C A P E
   Index: 44
   Name:  wv.renderer.hybrid.rating.js

   Purpose:
     - Coordinate a year/rating landscape, rating distribution,
       and selected-rank neighborhood from FileMaker-shaped rows
     - Show acknowledged FileMaker-owned focus and rating-band state
     - Report narrow selection and band intent through WV.sendAction

   Dependencies:
     - LIB[22] wv.platform.runtime.js
     - LIB[23] wv.platform.context.js
     - LIB[24] wv.platform.boot.js
     - LIB[25] wv.platform.actions.js

   Ownership:
     - Context owns selected movie, native found set, and rating band
     - Local state is limited to hover and in-flight band previews

   History:
     - 16 Aug 2026 — Lon Cook / AI performance : retain immediate
       in-flight selection and band feedback until FileMaker acknowledgement
     - 15 Aug 2026 — Lon Cook / AI correction : distinguish the
       rating-range selection with amber/gold while retaining coral
       for selected-movie focus
     - 15 Aug 2026 — Lon Cook / AI revision : replace the rejected
       minimum histogram closure with the approved three-view rating
       landscape while retaining the reviewed action contracts
     - 12 Aug 2026 — Lon Cook / AI review : correct pointer-band and
       numeric-null behavior in the initial histogram proposal
   ============================================================ */

(function (global) {
  "use strict";

  var WV = global.WV = global.WV || {};
  var BIN_COUNT = 14;
  var local = {
    dragStart: -1,
    dragEnd: -1,
    keyboardStart: -1,
    keyboardEnd: -1,
    pendingBandStart: -1,
    pendingBandEnd: -1,
    pendingMovieId: "",
    hoverMovieId: ""
  };

  function text(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback || "";
    return String(value);
  }

  function number(value) {
    if (value === undefined || value === null || value === "") return null;
    var n = Number(value);
    return Number.isFinite(n) ? n : null;
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function el(tag, className, value) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = value;
    return node;
  }

  function svg(tag, attrs) {
    var node = document.createElementNS("http://www.w3.org/2000/svg", tag);
    Object.keys(attrs || {}).forEach(function (key) {
      node.setAttribute(key, attrs[key]);
    });
    return node;
  }

  function send(type, payload) {
    return typeof WV.sendAction === "function"
      ? WV.sendAction(type, payload || {}, { source: "wv.renderer.hybrid.rating" })
      : "noBridge";
  }

  function normalizedRows(ranked) {
    return (Array.isArray(ranked.rows) ? ranked.rows : []).map(function (row, order) {
      row = row || {};
      return {
        movieId: text(row.movie_id),
        title: text(row.display_title, text(row.movie_id, "Untitled movie")),
        year: number(row.year),
        rating: number(row.rating),
        rank: number(row.rank),
        selected: row.selected === true,
        order: order
      };
    }).filter(function (row) {
      return row.movieId && row.rating !== null;
    });
  }

  function selectedRow(rows, ranked) {
    var selectedId = text(ranked.selected_movie_id);
    return rows.filter(function (row) {
      return row.selected || (selectedId && row.movieId === selectedId);
    })[0] || null;
  }

  function bandFrom(ranked) {
    var raw = ranked.rating_band && typeof ranked.rating_band === "object"
      ? ranked.rating_band : {};
    var lo = number(raw.rating_lo);
    var hi = number(raw.rating_hi);
    return {
      active: raw.active === true && lo !== null && hi !== null,
      lo: lo,
      hi: hi,
      label: text(raw.label, "All ratings")
    };
  }

  function makeBins(rows) {
    var values = rows.map(function (row) { return row.rating; });
    var min = Math.min.apply(Math, values);
    var max = Math.max.apply(Math, values);
    if (min === max) { min -= 0.5; max += 0.5; }
    var width = (max - min) / BIN_COUNT;
    var bins = [];
    var i;
    for (i = 0; i < BIN_COUNT; i += 1) {
      bins.push({
        index: i,
        lo: min + (i * width),
        hi: i === BIN_COUNT - 1 ? max : min + ((i + 1) * width),
        rows: []
      });
    }
    rows.forEach(function (row) {
      var index = Math.floor((row.rating - min) / width);
      bins[clamp(index, 0, BIN_COUNT - 1)].rows.push(row);
    });
    return { min: min, max: max, width: width, bins: bins };
  }

  function extent(values, fallbackMin, fallbackMax) {
    var usable = values.filter(function (value) { return value !== null; });
    if (!usable.length) return { min: fallbackMin, max: fallbackMax };
    var min = Math.min.apply(Math, usable);
    var max = Math.max.apply(Math, usable);
    if (min === max) { min -= 1; max += 1; }
    return { min: min, max: max };
  }

  function inBand(row, band) {
    return !band.active || (row.rating >= band.lo && row.rating <= band.hi);
  }

  function binInBand(bin, band) {
    return band.active && bin.hi > band.lo && bin.lo < band.hi;
  }

  function previewRange() {
    var start = local.dragStart >= 0 ? local.dragStart : local.keyboardStart;
    var end = local.dragEnd >= 0 ? local.dragEnd : local.keyboardEnd;
    if (start < 0 || end < 0) {
      start = local.pendingBandStart;
      end = local.pendingBandEnd;
    }
    if (start < 0 || end < 0) return null;
    return { lo: Math.min(start, end), hi: Math.max(start, end) };
  }

  function clearTransient() {
    local.dragStart = -1;
    local.dragEnd = -1;
    local.keyboardStart = -1;
    local.keyboardEnd = -1;
  }

  function clearPending() {
    local.pendingBandStart = -1;
    local.pendingBandEnd = -1;
    local.pendingMovieId = "";
  }

  function ensureStyles() {
    if (document.getElementById("wv-hybrid-rating-styles")) return;
    var style = document.createElement("style");
    style.id = "wv-hybrid-rating-styles";
    style.textContent = [
      ".wv-hybrid-page{box-sizing:border-box;min-height:100%;padding:12px;color:#ece8e1;background:radial-gradient(circle at 72% 0,rgba(76,104,101,.16),transparent 38%),linear-gradient(145deg,#0b0d0f,#15181a);font:13px/1.35 system-ui,-apple-system,BlinkMacSystemFont,\"Segoe UI\",sans-serif}",
      ".wv-landscape-shell{display:grid;gap:10px;min-height:100%}",
      ".wv-landscape-head{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:2px 2px 0}",
      ".wv-landscape-identity{display:flex;align-items:baseline;gap:18px;flex-wrap:wrap}",
      ".wv-landscape-title{margin:0;color:#de9675;font-size:19px;line-height:1;font-weight:780;letter-spacing:.045em;text-transform:uppercase}",
      ".wv-landscape-stat{color:#cfd4d3;font-size:12px;font-weight:680;letter-spacing:.03em;text-transform:uppercase}",
      ".wv-landscape-stat.is-filter{color:#70aaa5}",
      ".wv-landscape-focus{color:#eda57d;font-weight:650;text-align:right}",
      ".wv-landscape-grid{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(310px,1fr);gap:10px;min-height:0}",
      ".wv-landscape-side{display:grid;grid-template-rows:minmax(210px,1fr) auto;gap:10px;min-height:0}",
      ".wv-analytic-card{position:relative;min-width:0;border:1px solid rgba(255,255,255,.12);border-radius:9px;background:linear-gradient(160deg,rgba(28,30,31,.95),rgba(13,15,16,.97));box-shadow:inset 0 1px 0 rgba(255,255,255,.03),0 12px 28px rgba(0,0,0,.24);overflow:hidden}",
      ".wv-card-title{position:absolute;z-index:2;left:14px;top:11px;margin:0;color:#e2e4e1;font-size:13px;font-weight:700}",
      ".wv-chart-svg{display:block;width:100%;height:100%;min-height:280px;overflow:visible}",
      ".wv-dist-svg{display:block;width:100%;height:100%;min-height:215px}",
      ".wv-grid-line{stroke:rgba(255,255,255,.09);stroke-width:1}",
      ".wv-axis-line{stroke:rgba(255,255,255,.25);stroke-width:1}",
      ".wv-axis-label{fill:#aeb4b3;font-size:11px}",
      ".wv-band-zone{fill:rgba(216,182,91,.14);stroke:rgba(216,182,91,.74);stroke-width:1}",
      ".wv-landscape-point{fill:#6f9f9b;fill-opacity:.78;stroke:#111617;stroke-width:1.2;cursor:pointer;transition:r .12s,fill .12s,opacity .12s}",
      ".wv-landscape-point.is-out{opacity:.24}",
      ".wv-landscape-point:hover,.wv-landscape-point:focus{fill:#f0f3ef;stroke:#de9675;stroke-width:2;outline:none}",
      ".wv-landscape-point.is-selected{fill:#f2a074;fill-opacity:1;stroke:#ffe5d5;stroke-width:2.4;filter:drop-shadow(0 0 5px rgba(242,160,116,.7))}",
      ".wv-focus-rule{stroke:#f2a074;stroke-width:1.4;stroke-dasharray:4 4;opacity:.85}",
      ".wv-focus-label{fill:#f3b08e;font-size:11px;font-weight:700}",
      ".wv-hist-bin{fill:#547f7c;stroke:#111617;stroke-width:1;cursor:crosshair}",
      ".wv-hist-bin:hover,.wv-hist-bin:focus{fill:#80aaa6;outline:none}",
      ".wv-hist-bin.is-band{fill:#b18b2d}",
      ".wv-hist-bin.is-preview{fill:#d8b65b}",
      ".wv-hist-point{fill:#f2a074;stroke:#111617;stroke-width:1}",
      ".wv-dist-caption{position:absolute;left:14px;right:14px;bottom:7px;display:flex;justify-content:space-between;gap:12px;color:#969e9d;font-size:10px}",
      ".wv-neighborhood{padding:40px 10px 10px}",
      ".wv-neighbor-row{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px}",
      ".wv-neighbor{min-width:0;border:1px solid rgba(255,255,255,.14);border-radius:7px;background:rgba(255,255,255,.025);color:#d9ddda;padding:8px 7px;text-align:left;cursor:pointer}",
      ".wv-neighbor:hover,.wv-neighbor:focus-visible{border-color:#71aaa5;background:rgba(113,170,165,.1);outline:2px solid rgba(113,170,165,.5);outline-offset:1px}",
      ".wv-neighbor.is-selected{border-color:#de9675;background:linear-gradient(155deg,rgba(222,150,117,.16),rgba(222,150,117,.04));box-shadow:inset 0 0 0 1px rgba(222,150,117,.28)}",
      ".wv-neighbor-rank{color:#de9675;font-size:12px;font-weight:760}",
      ".wv-neighbor-rating{display:flex;align-items:center;gap:6px;margin:7px 0 4px;color:#eef1ed;font-size:14px;font-weight:700}",
      ".wv-neighbor-dot{width:12px;height:12px;border-radius:50%;background:#6f9f9b;box-shadow:0 0 0 1px rgba(255,255,255,.12)}",
      ".wv-neighbor.is-selected .wv-neighbor-dot{background:#f2a074;box-shadow:0 0 8px rgba(242,160,116,.65)}",
      ".wv-neighbor-title{display:block;overflow:hidden;color:#adb4b2;font-size:10px;line-height:1.25;text-overflow:ellipsis;white-space:nowrap}",
      ".wv-landscape-foot{display:flex;align-items:center;justify-content:space-between;gap:12px}",
      ".wv-ack{display:inline-flex;align-items:center;gap:7px;border:1px solid rgba(222,150,117,.55);border-radius:999px;background:rgba(222,150,117,.1);color:#efad89;padding:5px 10px;font-size:11px;font-weight:650}",
      ".wv-ack::before{content:'✓';display:grid;place-items:center;width:14px;height:14px;border:1px solid currentColor;border-radius:50%;font-size:9px}",
      ".wv-live{min-width:0;overflow:hidden;color:#9fa7a5;font-size:11px;text-overflow:ellipsis;white-space:nowrap}",
      ".wv-clear{border:1px solid rgba(222,150,117,.6);border-radius:6px;background:rgba(222,150,117,.08);color:#e6b29a;padding:6px 9px;font:inherit;cursor:pointer}",
      ".wv-clear:hover,.wv-clear:focus-visible{background:rgba(222,150,117,.18);outline:2px solid rgba(222,150,117,.55);outline-offset:1px}",
      ".wv-clear:disabled{cursor:default;opacity:.38}",
      ".wv-hybrid-empty,.wv-hybrid-error,.wv-hybrid-loading{display:grid;place-items:center;min-height:280px;color:#abb3b1;border:1px dashed rgba(255,255,255,.18);border-radius:9px}",
      ".wv-hybrid-error{color:#ffb39f}",
      "@media(max-width:620px){.wv-landscape-grid{grid-template-columns:1fr}.wv-landscape-side{grid-template-columns:1fr;grid-template-rows:auto auto}.wv-neighbor-row{grid-template-columns:repeat(5,minmax(0,1fr))}.wv-landscape-focus{display:none}}"
    ].join("");
    document.head.appendChild(style);
  }

  function requestSelection(row, live) {
    local.pendingMovieId = row.movieId;
    Array.prototype.forEach.call(document.querySelectorAll(".wv-landscape-point"), function (node) {
      var selected = node.getAttribute("data-movie-id") === row.movieId;
      node.classList.toggle("is-selected", selected);
      node.setAttribute("r", selected ? "7.5" : "4.6");
    });
    Array.prototype.forEach.call(document.querySelectorAll(".wv-neighbor"), function (node) {
      node.classList.toggle("is-selected", node.getAttribute("data-movie-id") === row.movieId);
    });
    var focus = document.querySelector(".wv-landscape-focus");
    if (focus) focus.textContent = "Updating FileMaker: " + row.title + " · Rank " + text(row.rank, "—");
    var result = send("hybrid.select_movie", { movie_id: row.movieId });
    live.textContent = "Selection request: " + result + ". Waiting for FileMaker acknowledgement.";
  }

  function onSelection(node, row, live) {
    node.addEventListener("click", function () { requestSelection(row, live); });
    node.addEventListener("keydown", function (event) {
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      requestSelection(row, live);
    });
  }

  function addTitle(node, title) {
    var titleNode = svg("title");
    titleNode.textContent = title;
    node.appendChild(titleNode);
  }

  function renderLandscape(card, rows, selected, band, live) {
    card.appendChild(el("h3", "wv-card-title", "Rating landscape"));
    var chart = svg("svg", {
      "class": "wv-chart-svg",
      "viewBox": "0 0 720 430",
      "role": "group",
      "aria-label": "Movie rating landscape by release year and global rating. Select a point to ask FileMaker to focus that movie."
    });
    var left = 62, right = 22, top = 54, bottom = 52;
    var width = 720 - left - right;
    var height = 430 - top - bottom;
    var yearExtent = extent(rows.map(function (row) { return row.year; }), 1990, 2030);
    var ratingExtent = extent(rows.map(function (row) { return row.rating; }), 0, 10);
    var yearPad = Math.max(1, (yearExtent.max - yearExtent.min) * 0.04);
    var ratingPad = Math.max(0.25, (ratingExtent.max - ratingExtent.min) * 0.1);
    var yearMin = yearExtent.min - yearPad;
    var yearMax = yearExtent.max + yearPad;
    var ratingMin = ratingExtent.min - ratingPad;
    var ratingMax = ratingExtent.max + ratingPad;

    function xFor(year) {
      var value = year === null ? yearMin : year;
      return left + ((value - yearMin) / (yearMax - yearMin)) * width;
    }

    function yFor(rating) {
      return top + ((ratingMax - rating) / (ratingMax - ratingMin)) * height;
    }

    var i;
    for (i = 0; i <= 5; i += 1) {
      var gx = left + ((width / 5) * i);
      var gy = top + ((height / 5) * i);
      chart.appendChild(svg("line", { "class": "wv-grid-line", x1: gx, x2: gx, y1: top, y2: top + height }));
      chart.appendChild(svg("line", { "class": "wv-grid-line", x1: left, x2: left + width, y1: gy, y2: gy }));
      var yearLabel = svg("text", { "class": "wv-axis-label", x: gx, y: top + height + 22, "text-anchor": "middle" });
      yearLabel.textContent = Math.round(yearMin + (((yearMax - yearMin) / 5) * i));
      chart.appendChild(yearLabel);
      var ratingLabel = svg("text", { "class": "wv-axis-label", x: left - 10, y: gy + 4, "text-anchor": "end" });
      ratingLabel.textContent = (ratingMax - (((ratingMax - ratingMin) / 5) * i)).toFixed(1);
      chart.appendChild(ratingLabel);
    }

    chart.appendChild(svg("line", { "class": "wv-axis-line", x1: left, x2: left + width, y1: top + height, y2: top + height }));
    chart.appendChild(svg("line", { "class": "wv-axis-line", x1: left, x2: left, y1: top, y2: top + height }));

    if (band.active) {
      var bandTop = yFor(band.hi);
      var bandBottom = yFor(band.lo);
      chart.appendChild(svg("rect", {
        "class": "wv-band-zone",
        x: left,
        y: bandTop,
        width: width,
        height: Math.max(1, bandBottom - bandTop)
      }));
    }

    rows.forEach(function (row) {
      var isSelected = selected && row.movieId === selected.movieId;
      var point = svg("circle", {
        "class": "wv-landscape-point" + (isSelected ? " is-selected" : "") + (inBand(row, band) ? "" : " is-out"),
        cx: xFor(row.year),
        cy: yFor(row.rating),
        r: isSelected ? 7.5 : 4.6,
        tabindex: "0",
        role: "button",
        "data-movie-id": row.movieId,
        "aria-label": "Select " + row.title + ", released " + text(row.year, "year unknown") + ", rating " + row.rating.toFixed(2) + ", rank " + text(row.rank, "unknown")
      });
      addTitle(point, row.title + " · " + row.rating.toFixed(2) + " · rank " + text(row.rank, "—"));
      onSelection(point, row, live);
      chart.appendChild(point);
    });

    if (selected) {
      var sx = xFor(selected.year);
      var sy = yFor(selected.rating);
      chart.appendChild(svg("line", { "class": "wv-focus-rule", x1: left, x2: left + width, y1: sy, y2: sy }));
      chart.appendChild(svg("line", { "class": "wv-focus-rule", x1: sx, x2: sx, y1: top, y2: top + height }));
      var focusLabel = svg("text", {
        "class": "wv-focus-label",
        x: clamp(sx + 10, left + 6, left + width - 185),
        y: clamp(sy - 11, top + 14, top + height - 8)
      });
      focusLabel.textContent = selected.title + " · " + selected.rating.toFixed(2);
      chart.appendChild(focusLabel);
    }

    var xTitle = svg("text", { "class": "wv-axis-label", x: left + (width / 2), y: 421, "text-anchor": "middle" });
    xTitle.textContent = "Release year";
    chart.appendChild(xTitle);
    var yTitle = svg("text", { "class": "wv-axis-label", x: 15, y: top + (height / 2), transform: "rotate(-90 15 " + (top + (height / 2)) + ")", "text-anchor": "middle" });
    yTitle.textContent = "Global rating";
    chart.appendChild(yTitle);
    card.appendChild(chart);
  }

  function renderDistribution(card, data, selected, band, live) {
    card.appendChild(el("h3", "wv-card-title", "Rating distribution"));
    var chart = svg("svg", {
      "class": "wv-dist-svg",
      "viewBox": "0 0 500 250",
      "role": "group",
      "aria-label": "Rating distribution. Drag across bins or use the keyboard to request a FileMaker rating band."
    });
    var left = 42, top = 48, width = 428, bottom = 201;
    var caption = null;
    var slot = width / data.bins.length;
    var maxCount = Math.max.apply(Math, data.bins.map(function (bin) { return bin.rows.length; }).concat([1]));

    function updatePreview() {
      var range = previewRange();
      Array.prototype.forEach.call(chart.querySelectorAll(".wv-hist-bin"), function (node, index) {
        node.classList.toggle("is-preview", !!range && index >= range.lo && index <= range.hi);
      });
    }

    function pointerBin(event) {
      var bounds = chart.getBoundingClientRect();
      if (!bounds.width) return 0;
      var viewX = (event.clientX - bounds.left) * (500 / bounds.width);
      return clamp(Math.floor((viewX - left) / slot), 0, data.bins.length - 1);
    }

    function commitRange(start, end) {
      var loIndex = Math.min(start, end);
      var hiIndex = Math.max(start, end);
      var lo = data.bins[loIndex].lo;
      var hi = data.bins[hiIndex].hi;
      local.pendingBandStart = loIndex;
      local.pendingBandEnd = hiIndex;
      updatePreview();
      if (caption && caption.firstChild) caption.firstChild.textContent = lo.toFixed(2) + "–" + hi.toFixed(2) + " · applying";
      var result = send("hybrid.set_rating_band", { rating_lo: lo, rating_hi: hi });
      live.textContent = "Band request: " + result + ". Waiting for FileMaker acknowledgement.";
    }

    [0, 1, 2, 3].forEach(function (index) {
      var y = top + (((bottom - top) / 3) * index);
      chart.appendChild(svg("line", { "class": "wv-grid-line", x1: left, x2: left + width, y1: y, y2: y }));
    });

    data.bins.forEach(function (bin, index) {
      var height = (bin.rows.length / maxCount) * (bottom - top - 8);
      var rect = svg("rect", {
        "class": "wv-hist-bin" + (binInBand(bin, band) ? " is-band" : ""),
        x: left + (index * slot) + 1,
        y: bottom - height,
        width: Math.max(2, slot - 2),
        height: Math.max(1, height),
        rx: 1.5,
        tabindex: "0",
        role: "button",
        "aria-label": bin.rows.length + " movies from " + bin.lo.toFixed(2) + " to " + bin.hi.toFixed(2)
      });
      rect.addEventListener("pointerdown", function (event) {
        local.dragStart = index;
        local.dragEnd = index;
        if (chart.setPointerCapture) chart.setPointerCapture(event.pointerId);
        updatePreview();
      });
      rect.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          if (local.keyboardStart < 0) {
            local.keyboardStart = index;
            local.keyboardEnd = index;
            live.textContent = "Band start selected. Extend with Shift+Arrow, then press Enter.";
            updatePreview();
          } else {
            commitRange(local.keyboardStart, local.keyboardEnd);
            local.keyboardStart = -1;
            local.keyboardEnd = -1;
            updatePreview();
          }
        } else if (event.shiftKey && (event.key === "ArrowLeft" || event.key === "ArrowRight")) {
          event.preventDefault();
          if (local.keyboardStart < 0) local.keyboardStart = index;
          local.keyboardEnd = clamp((local.keyboardEnd < 0 ? index : local.keyboardEnd) + (event.key === "ArrowLeft" ? -1 : 1), 0, data.bins.length - 1);
          updatePreview();
        } else if (event.key === "Escape") {
          clearTransient();
          updatePreview();
        }
      });
      chart.appendChild(rect);
    });

    chart.addEventListener("pointermove", function (event) {
      if (local.dragStart < 0) return;
      local.dragEnd = pointerBin(event);
      updatePreview();
    });
    chart.addEventListener("pointerup", function (event) {
      if (local.dragStart < 0) return;
      local.dragEnd = pointerBin(event);
      commitRange(local.dragStart, local.dragEnd);
      local.dragStart = -1;
      local.dragEnd = -1;
      updatePreview();
    });
    chart.addEventListener("pointercancel", function () {
      local.dragStart = -1;
      local.dragEnd = -1;
      updatePreview();
    });

    if (selected) {
      var selectedX = left + ((selected.rating - data.min) / (data.max - data.min)) * width;
      chart.appendChild(svg("line", { "class": "wv-focus-rule", x1: selectedX, x2: selectedX, y1: top, y2: bottom + 4 }));
      chart.appendChild(svg("circle", { "class": "wv-hist-point", cx: selectedX, cy: bottom + 4, r: 5.5 }));
    }

    var minLabel = svg("text", { "class": "wv-axis-label", x: left, y: 222 });
    minLabel.textContent = data.min.toFixed(2);
    chart.appendChild(minLabel);
    var maxLabel = svg("text", { "class": "wv-axis-label", x: left + width, y: 222, "text-anchor": "end" });
    maxLabel.textContent = data.max.toFixed(2);
    chart.appendChild(maxLabel);
    card.appendChild(chart);

    caption = el("div", "wv-dist-caption");
    caption.appendChild(el("span", "", band.active ? band.lo.toFixed(2) + "–" + band.hi.toFixed(2) : "No rating band"));
    caption.appendChild(el("span", "", "Drag bins to filter FileMaker"));
    card.appendChild(caption);
  }

  function neighborhood(rows, selected) {
    var sorted = rows.slice().sort(function (a, b) {
      var ar = a.rank === null ? Number.MAX_VALUE : a.rank;
      var br = b.rank === null ? Number.MAX_VALUE : b.rank;
      return ar - br || a.order - b.order;
    });
    if (!sorted.length) return [];
    var selectedIndex = selected ? sorted.map(function (row) { return row.movieId; }).indexOf(selected.movieId) : 0;
    if (selectedIndex < 0) selectedIndex = 0;
    var start = clamp(selectedIndex - 2, 0, Math.max(0, sorted.length - 5));
    return sorted.slice(start, start + 5);
  }

  function renderNeighborhood(card, rows, selected, live) {
    card.appendChild(el("h3", "wv-card-title", "Nearby in rank"));
    var wrap = el("div", "wv-neighborhood");
    var rowNode = el("div", "wv-neighbor-row");
    neighborhood(rows, selected).forEach(function (row) {
      var isSelected = selected && row.movieId === selected.movieId;
      var button = el("button", "wv-neighbor" + (isSelected ? " is-selected" : ""));
      button.type = "button";
      button.setAttribute("data-movie-id", row.movieId);
      button.setAttribute("aria-label", (isSelected ? "Selected. " : "Select ") + row.title + ", rank " + text(row.rank, "unknown") + ", rating " + row.rating.toFixed(2));
      button.appendChild(el("div", "wv-neighbor-rank", text(row.rank, "—")));
      var rating = el("div", "wv-neighbor-rating");
      rating.appendChild(el("span", "wv-neighbor-dot"));
      rating.appendChild(el("span", "", row.rating.toFixed(2)));
      button.appendChild(rating);
      button.appendChild(el("span", "wv-neighbor-title", row.title));
      button.addEventListener("click", function () { requestSelection(row, live); });
      rowNode.appendChild(button);
    });
    wrap.appendChild(rowNode);
    card.appendChild(wrap);
  }

  function renderError(root, message) {
    root.innerHTML = "";
    root.appendChild(el("div", "wv-hybrid-error", message));
  }

  function render(ctx) {
    ensureStyles();
    clearTransient();
    clearPending();
    var root = document.querySelector("[data-wv-page='hybrid-rating']");
    if (!root) return;

    try {
      ctx = ctx && typeof ctx === "object" ? ctx : {};
      var ranked = ctx.ranked_view && typeof ctx.ranked_view === "object" ? ctx.ranked_view : {};
      var rows = normalizedRows(ranked);
      root.innerHTML = "";
      if (!rows.length) {
        root.appendChild(el("div", "wv-hybrid-empty", text(ranked.empty_message, "No ranked movies match the active FileMaker filter.")));
        return;
      }

      var selected = selectedRow(rows, ranked);
      var band = bandFrom(ranked);
      var data = makeBins(rows);
      var shell = el("section", "wv-landscape-shell");
      var head = el("header", "wv-landscape-head");
      var identity = el("div", "wv-landscape-identity");
      identity.appendChild(el("h2", "wv-landscape-title", "Rating landscape"));
      identity.appendChild(el("span", "wv-landscape-stat", rows.length + " movies"));
      identity.appendChild(el("span", "wv-landscape-stat is-filter", band.label));
      head.appendChild(identity);
      head.appendChild(el("div", "wv-landscape-focus", selected ? "Focus: " + selected.title + " · Rank " + text(selected.rank, "—") : "No FileMaker selection"));
      shell.appendChild(head);

      var live = el("div", "wv-live", "Dashboard ready. FileMaker owns settled selection and filters.");
      live.setAttribute("aria-live", "polite");
      var grid = el("div", "wv-landscape-grid");
      var landscapeCard = el("section", "wv-analytic-card");
      renderLandscape(landscapeCard, rows, selected, band, live);
      grid.appendChild(landscapeCard);
      var side = el("div", "wv-landscape-side");
      var distributionCard = el("section", "wv-analytic-card");
      renderDistribution(distributionCard, data, selected, band, live);
      side.appendChild(distributionCard);
      var neighborhoodCard = el("section", "wv-analytic-card");
      renderNeighborhood(neighborhoodCard, rows, selected, live);
      side.appendChild(neighborhoodCard);
      grid.appendChild(side);
      shell.appendChild(grid);

      var foot = el("footer", "wv-landscape-foot");
      foot.appendChild(el("span", "wv-ack", selected ? "Selected in FileMaker" : "Waiting for FileMaker selection"));
      foot.appendChild(live);
      var clear = el("button", "wv-clear", "Clear rating band");
      clear.type = "button";
      clear.disabled = !band.active;
      clear.addEventListener("click", function () {
        var result = send("hybrid.clear_rating_band", {});
        live.textContent = "Clear-band request: " + result + ". Waiting for FileMaker acknowledgement.";
      });
      foot.appendChild(clear);
      shell.appendChild(foot);
      root.appendChild(shell);
    } catch (error) {
      renderError(root, "The rating landscape could not render: " + text(error && error.message, "unknown error"));
    }
  }

  if (typeof WV.registerRenderer === "function") WV.registerRenderer(render);
  else WV.render = render;
})(window);
