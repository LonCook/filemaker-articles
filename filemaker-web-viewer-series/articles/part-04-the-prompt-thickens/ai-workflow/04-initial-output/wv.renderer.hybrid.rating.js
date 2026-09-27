/* ============================================================
   W V   H Y B R I D   R A T I N G   R E N D E R E R
   Index: 44
   Name:  wv.renderer.hybrid.rating.js

   Purpose:
     - Render a FileMaker-shaped rating distribution
     - Show acknowledged focus and rating-band state
     - Report narrow selection and band intent through WV.sendAction

   Dependencies:
     - LIB[22] wv.platform.runtime.js
     - LIB[23] wv.platform.context.js
     - LIB[24] wv.platform.boot.js
     - LIB[25] wv.platform.actions.js

   Exports:
     - Registers render(ctx) through WV.registerRenderer

   Ownership:
     - Context owns selected movie and rating band
     - Local state is limited to hover, keyboard preview, and pointer drag

   History:
     - 12 Aug 2026 — AI initial proposal : created for contract review
   ============================================================ */

(function (global) {
  "use strict";

  var WV = global.WV = global.WV || {};
  var BIN_COUNT = 16;
  var local = { dragStart: -1, dragEnd: -1, keyboardStart: -1, keyboardEnd: -1 };

  function text(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback || "";
    return String(value);
  }

  function number(value) {
    var n = Number(value);
    return Number.isFinite(n) ? n : null;
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
        rating: number(row.rating),
        rank: number(row.rank),
        selected: row.selected === true,
        order: order
      };
    }).filter(function (row) {
      return row.movieId && row.rating !== null;
    });
  }

  function makeBins(rows) {
    var values = rows.map(function (row) { return row.rating; });
    var min = Math.min.apply(Math, values);
    var max = Math.max.apply(Math, values);
    if (min === max) { min -= 0.5; max += 0.5; }
    var width = (max - min) / BIN_COUNT;
    var bins = [];
    for (var i = 0; i < BIN_COUNT; i += 1) {
      bins.push({
        index: i,
        lo: min + (i * width),
        hi: i === BIN_COUNT - 1 ? max : min + ((i + 1) * width),
        rows: []
      });
    }
    rows.forEach(function (row) {
      var index = Math.floor((row.rating - min) / width);
      index = Math.max(0, Math.min(BIN_COUNT - 1, index));
      bins[index].rows.push(row);
    });
    return { min: min, max: max, bins: bins };
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

  function binInBand(bin, band) {
    return band.active && bin.hi >= band.lo && bin.lo <= band.hi;
  }

  function previewRange() {
    var start = local.dragStart >= 0 ? local.dragStart : local.keyboardStart;
    var end = local.dragEnd >= 0 ? local.dragEnd : local.keyboardEnd;
    if (start < 0 || end < 0) return null;
    return { lo: Math.min(start, end), hi: Math.max(start, end) };
  }

  function clearTransient() {
    local.dragStart = -1;
    local.dragEnd = -1;
    local.keyboardStart = -1;
    local.keyboardEnd = -1;
  }

  function ensureStyles() {
    if (document.getElementById("wv-hybrid-rating-styles")) return;
    var style = document.createElement("style");
    style.id = "wv-hybrid-rating-styles";
    style.textContent = [
      ".wv-hybrid-page{box-sizing:border-box;min-height:100%;padding:18px;color:#eef1f4;background:linear-gradient(145deg,#10151b,#171d24);font:14px/1.4 system-ui,sans-serif}",
      ".wv-hybrid-card{border:1px solid rgba(255,255,255,.13);border-radius:14px;background:rgba(8,11,15,.72);padding:16px;box-shadow:0 14px 34px rgba(0,0,0,.24)}",
      ".wv-hybrid-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:12px}",
      ".wv-hybrid-kicker{color:#d8b65b;font-size:11px;font-weight:750;letter-spacing:.12em;text-transform:uppercase}",
      ".wv-hybrid-title{font-size:20px;font-weight:720;margin:3px 0 0}",
      ".wv-hybrid-summary{color:#aeb8c2;font-size:12px;text-align:right}",
      ".wv-hybrid-chart{display:block;width:100%;height:auto;overflow:visible}",
      ".wv-hybrid-bin{fill:#506c82;stroke:#0e141a;stroke-width:1;cursor:crosshair}",
      ".wv-hybrid-bin:hover,.wv-hybrid-bin:focus{fill:#7894a8;outline:none}",
      ".wv-hybrid-bin.is-band{fill:#caa44a}",
      ".wv-hybrid-bin.is-preview{fill:#e0bd63}",
      ".wv-hybrid-point{fill:#8fa6b8;stroke:#10151b;stroke-width:1.5;cursor:pointer}",
      ".wv-hybrid-point:hover,.wv-hybrid-point:focus{fill:#fff;stroke:#d8b65b;outline:none}",
      ".wv-hybrid-point.is-selected{fill:#ef8d72;stroke:#fff;stroke-width:2.5}",
      ".wv-hybrid-focus-line{stroke:#ef8d72;stroke-width:2;stroke-dasharray:4 4}",
      ".wv-hybrid-axis{fill:#96a3ae;font-size:11px}",
      ".wv-hybrid-controls{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:8px}",
      ".wv-hybrid-button{border:1px solid rgba(216,182,91,.7);border-radius:7px;background:rgba(216,182,91,.12);color:inherit;padding:7px 10px;font:inherit;cursor:pointer}",
      ".wv-hybrid-button:hover,.wv-hybrid-button:focus-visible{background:rgba(216,182,91,.24);outline:2px solid #d8b65b;outline-offset:2px}",
      ".wv-hybrid-note{color:#aeb8c2;font-size:12px}",
      ".wv-hybrid-empty,.wv-hybrid-error,.wv-hybrid-loading{display:grid;place-items:center;min-height:180px;color:#b9c2ca;border:1px dashed rgba(255,255,255,.18);border-radius:12px}",
      ".wv-hybrid-error{color:#ffb5a5}"
    ].join("");
    document.head.appendChild(style);
  }

  function renderError(root, message) {
    root.innerHTML = "";
    root.appendChild(el("div", "wv-hybrid-error", message));
  }

  function render(ctx) {
    ensureStyles();
    clearTransient();

    var root = document.querySelector("[data-wv-page='hybrid-rating']");
    if (!root) return;

    try {
      ctx = ctx && typeof ctx === "object" ? ctx : {};
      var ranked = ctx.ranked_view && typeof ctx.ranked_view === "object"
        ? ctx.ranked_view : {};
      var rows = normalizedRows(ranked);

      root.innerHTML = "";
      if (!rows.length) {
        root.appendChild(el("div", "wv-hybrid-empty",
          text(ranked.empty_message, "No ranked movies match the active FileMaker filter.")));
        return;
      }

      var data = makeBins(rows);
      var band = bandFrom(ranked);
      var selectedId = text(ranked.selected_movie_id);
      var selected = rows.filter(function (row) {
        return row.selected || (selectedId && row.movieId === selectedId);
      })[0] || null;

      var card = el("section", "wv-hybrid-card");
      var head = el("div", "wv-hybrid-head");
      var titleBlock = el("div");
      titleBlock.appendChild(el("div", "wv-hybrid-kicker", "FileMaker-owned ranked set"));
      titleBlock.appendChild(el("h2", "wv-hybrid-title", "Rating distribution"));
      head.appendChild(titleBlock);
      head.appendChild(el("div", "wv-hybrid-summary",
        rows.length + " movies · " + band.label + (selected ? " · Focus: " + selected.title : "")));
      card.appendChild(head);

      var chart = svg("svg", {
        "class": "wv-hybrid-chart",
        "viewBox": "0 0 760 250",
        "role": "group",
        "aria-label": "Rating distribution. Choose a movie marker for focus or choose histogram bins for a FileMaker rating band."
      });
      var maxCount = Math.max.apply(Math, data.bins.map(function (bin) { return bin.rows.length; }).concat([1]));
      var left = 38, top = 18, width = 684, bottom = 188, slot = width / data.bins.length;
      var live = el("div", "wv-hybrid-note", "Chart ready.");
      live.setAttribute("aria-live", "polite");

      function updatePreview() {
        var range = previewRange();
        Array.prototype.forEach.call(chart.querySelectorAll(".wv-hybrid-bin"), function (node, index) {
          node.classList.toggle("is-preview", !!range && index >= range.lo && index <= range.hi);
        });
      }

      function commitRange(start, end) {
        var loIndex = Math.min(start, end);
        var hiIndex = Math.max(start, end);
        var lo = data.bins[loIndex].lo;
        var hi = data.bins[hiIndex].hi;
        var result = send("hybrid.set_rating_band", { rating_lo: lo, rating_hi: hi });
        live.textContent = "Band request: " + result + ". Waiting for FileMaker acknowledgement.";
      }

      data.bins.forEach(function (bin, index) {
        var height = (bin.rows.length / maxCount) * 142;
        var rect = svg("rect", {
          "class": "wv-hybrid-bin" + (binInBand(bin, band) ? " is-band" : ""),
          "x": left + (index * slot) + 1,
          "y": bottom - height,
          "width": Math.max(2, slot - 2),
          "height": Math.max(1, height),
          "rx": 2,
          "tabindex": "0",
          "role": "button",
          "aria-label": bin.rows.length + " movies from " + bin.lo.toFixed(2) + " to " + bin.hi.toFixed(2)
        });
        rect.addEventListener("pointerdown", function (event) {
          local.dragStart = index;
          local.dragEnd = index;
          if (rect.setPointerCapture) rect.setPointerCapture(event.pointerId);
          updatePreview();
        });
        rect.addEventListener("pointerenter", function () {
          if (local.dragStart >= 0) { local.dragEnd = index; updatePreview(); }
        });
        rect.addEventListener("pointerup", function () {
          if (local.dragStart >= 0) commitRange(local.dragStart, local.dragEnd);
          local.dragStart = -1; local.dragEnd = -1; updatePreview();
        });
        rect.addEventListener("keydown", function (event) {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            if (local.keyboardStart < 0) {
              local.keyboardStart = index;
              local.keyboardEnd = index;
              live.textContent = "Band start selected. Use Shift+Left or Shift+Right, then press Enter to send.";
              updatePreview();
            } else {
              commitRange(local.keyboardStart, local.keyboardEnd);
              local.keyboardStart = -1; local.keyboardEnd = -1; updatePreview();
            }
          } else if (event.shiftKey && (event.key === "ArrowLeft" || event.key === "ArrowRight")) {
            event.preventDefault();
            if (local.keyboardStart < 0) local.keyboardStart = index;
            var delta = event.key === "ArrowLeft" ? -1 : 1;
            local.keyboardEnd = Math.max(0, Math.min(data.bins.length - 1,
              (local.keyboardEnd < 0 ? index : local.keyboardEnd) + delta));
            updatePreview();
          } else if (event.key === "Escape") {
            local.keyboardStart = -1; local.keyboardEnd = -1; updatePreview();
          }
        });
        chart.appendChild(rect);
      });

      rows.forEach(function (row, index) {
        var x = left + ((row.rating - data.min) / (data.max - data.min)) * width;
        var y = bottom + 13 + ((index % 3) * 8);
        var point = svg("circle", {
          "class": "wv-hybrid-point" + (selected && row.movieId === selected.movieId ? " is-selected" : ""),
          "cx": x,
          "cy": y,
          "r": selected && row.movieId === selected.movieId ? 5 : 3.2,
          "tabindex": "0",
          "role": "button",
          "aria-label": "Select " + row.title + ", rating " + row.rating.toFixed(2)
        });
        function requestSelection(event) {
          if (event && event.type === "keydown" && event.key !== "Enter" && event.key !== " ") return;
          if (event) event.preventDefault();
          var result = send("hybrid.select_movie", { movie_id: row.movieId });
          live.textContent = "Selection request: " + result + ". Waiting for FileMaker acknowledgement.";
        }
        point.addEventListener("click", requestSelection);
        point.addEventListener("keydown", requestSelection);
        chart.appendChild(point);
      });

      if (selected) {
        var focusX = left + ((selected.rating - data.min) / (data.max - data.min)) * width;
        chart.appendChild(svg("line", {
          "class": "wv-hybrid-focus-line", "x1": focusX, "x2": focusX, "y1": top, "y2": bottom
        }));
      }

      var minLabel = svg("text", { "class": "wv-hybrid-axis", "x": left, "y": 238 });
      minLabel.textContent = data.min.toFixed(2);
      chart.appendChild(minLabel);
      var maxLabel = svg("text", { "class": "wv-hybrid-axis", "x": left + width, "y": 238, "text-anchor": "end" });
      maxLabel.textContent = data.max.toFixed(2);
      chart.appendChild(maxLabel);
      card.appendChild(chart);

      var controls = el("div", "wv-hybrid-controls");
      var clear = el("button", "wv-hybrid-button", "Clear rating band");
      clear.type = "button";
      clear.disabled = !band.active;
      clear.addEventListener("click", function () {
        var result = send("hybrid.clear_rating_band", {});
        live.textContent = "Clear-band request: " + result + ". Waiting for FileMaker acknowledgement.";
      });
      controls.appendChild(clear);
      controls.appendChild(live);
      card.appendChild(controls);
      root.appendChild(card);
    } catch (error) {
      renderError(root, "The rating distribution could not render: " + text(error && error.message, "unknown error"));
    }
  }

  if (typeof WV.registerRenderer === "function") WV.registerRenderer(render);
  else WV.render = render;
})(window);

