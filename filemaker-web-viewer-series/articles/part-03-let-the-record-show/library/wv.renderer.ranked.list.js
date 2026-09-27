/* ============================================================
   W V   R A N K E D   L I S T   R E N D E R E R
   Index: 42
   Name:  wv.renderer.ranked.list.js

   Purpose:
     - Render FileMaker-shaped ranked movie rows
     - Show deliberate loading, empty, populated, and selected states
     - Report row-selection intent through WV.sendAction

   Dependencies:
     - LIB[22] wv.platform.runtime.js
     - LIB[23] wv.platform.context.js
     - LIB[24] wv.platform.boot.js
     - LIB[25] wv.platform.actions.js

   Exports:
     - Registers a renderer with WV.registerRenderer( fn )

   Public API:
     - None

   Notes:
     - This renderer does not query FileMaker.
     - A row is selected only when FileMaker marks it selected in context.
     - The JavaScript was developed with AI assistance inside this contract.

   History:
     - 01 Aug 2026 — Lon Cook — lon@portagebay.com : expose the acknowledged native found-set position with the ranked view.
     - 01 Aug 2026 — Lon Cook — lon@portagebay.com : created
   ============================================================ */

(function () {
  "use strict";

  if (!window.WV) return;

  function value(value, fallback) {
    if (value === undefined || value === null || value === "") {
      return fallback === undefined ? "" : String(fallback);
    }
    return String(value);
  }

  function number(value, digits) {
    var parsed = Number(value);
    if (!isFinite(parsed)) return "—";
    return typeof digits === "number" ? parsed.toFixed(digits) : String(parsed);
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  function ensureRoot() {
    var root = document.getElementById("wv-root");
    if (!root) {
      root = document.createElement("div");
      root.id = "wv-root";
      document.body.appendChild(root);
    }
    return root;
  }

  function ensureStyles() {
    if (document.getElementById("wv-ranked-list-style")) return;

    var style = document.createElement("style");
    style.id = "wv-ranked-list-style";
    style.textContent =
      ".wv-ranked-page{height:100%;padding:16px;overflow:auto;background:var(--wv-bg-main,#141414);color:var(--wv-text-1,#fff);}" +
      ".wv-ranked-shell{max-width:780px;margin:0 auto;}" +
      ".wv-ranked-eyebrow{color:var(--wv-accent-1,#CFA100);font-size:11px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;}" +
      ".wv-ranked-title{font-size:24px;line-height:1.15;margin:5px 0 4px;}" +
      ".wv-ranked-summary{color:var(--wv-text-2,rgba(255,255,255,.78));font-size:13px;margin-bottom:14px;}" +
      ".wv-ranked-list{display:grid;gap:7px;}" +
      ".wv-ranked-row{width:100%;display:grid;grid-template-columns:48px minmax(0,1fr) 92px;gap:12px;align-items:center;padding:10px 12px;border:1px solid rgba(255,255,255,.11);border-radius:7px;background:rgba(255,255,255,.035);color:inherit;text-align:left;font:inherit;cursor:pointer;}" +
      ".wv-ranked-row:hover,.wv-ranked-row:focus-visible{border-color:rgba(201,164,74,.72);background:rgba(201,164,74,.09);outline:none;}" +
      ".wv-ranked-row.is-selected{border-color:var(--wv-accent-1,#CFA100);background:rgba(201,164,74,.17);box-shadow:inset 3px 0 0 var(--wv-accent-1,#CFA100);}" +
      ".wv-ranked-rank{color:var(--wv-accent-1,#CFA100);font-size:18px;font-variant-numeric:tabular-nums;}" +
      ".wv-ranked-name{font-size:14px;font-weight:650;overflow-wrap:anywhere;}" +
      ".wv-ranked-meta{color:var(--wv-text-3,rgba(255,255,255,.6));font-size:11px;margin-top:2px;}" +
      ".wv-ranked-rating{text-align:right;font-variant-numeric:tabular-nums;}" +
      ".wv-ranked-rating strong{display:block;font-size:16px;}" +
      ".wv-ranked-rating span{color:var(--wv-text-3,rgba(255,255,255,.6));font-size:10px;text-transform:uppercase;}" +
      ".wv-ranked-empty,.wv-ranked-loading{padding:28px 16px;border:1px dashed rgba(255,255,255,.16);border-radius:7px;color:var(--wv-text-2,rgba(255,255,255,.78));text-align:center;}" +
      ".wv-ranked-action-note{min-height:18px;margin-top:10px;color:var(--wv-text-3,rgba(255,255,255,.6));font-size:11px;}";

    document.head.appendChild(style);
  }

  function render(ctx) {
    ctx = ctx || {};

    var root = ensureRoot();
    var ranked = ctx.ranked_view || {};
    var filter = ranked.filter || {};
    var actions = ctx.actions || {};
    var rows = Array.isArray(ranked.rows) ? ranked.rows : [];

    ensureStyles();
    root.innerHTML = "";
    root.classList.add("wv-theme-gold");

    var page = el("section", "wv-ranked-page");
    var shell = el("div", "wv-ranked-shell");
    var actionNote = el("div", "wv-ranked-action-note", value(actions.status, "Waiting for a selection"));

    shell.appendChild(el("div", "wv-ranked-eyebrow", "Native FileMaker records"));
    shell.appendChild(el("h1", "wv-ranked-title", "Ranked Movies"));
    var nativePosition = number(ranked.current_record_number, 0);
    var nativeCount = number(ranked.native_found_count, 0);
    var nativeSummary = nativeCount > 0
      ? " · native record " + nativePosition + " of " + nativeCount
      : " · native found set empty";

    shell.appendChild(el(
      "div",
      "wv-ranked-summary",
      value(filter.label, "All Genres") + " · " + number(ranked.count, 0) + " movies" + nativeSummary
    ));

    if (!rows.length) {
      shell.appendChild(el(
        "div",
        "wv-ranked-empty",
        value(ranked.empty_message, "No ranked movies match the active filter.")
      ));
    } else {
      var list = el("div", "wv-ranked-list");

      rows.forEach(function (record) {
        record = record || {};

        var movieId = value(record.movie_id);
        var row = el("button", "wv-ranked-row" + (record.selected === true ? " is-selected" : ""));
        row.type = "button";
        row.setAttribute("data-movie-id", movieId);
        row.setAttribute("aria-pressed", record.selected === true ? "true" : "false");

        row.appendChild(el("div", "wv-ranked-rank", "#" + number(record.rank, 0)));

        var identity = el("div", "wv-ranked-identity");
        identity.appendChild(el("div", "wv-ranked-name", value(record.display_title, "Untitled movie")));
        identity.appendChild(el("div", "wv-ranked-meta", "Stable id: " + movieId));
        row.appendChild(identity);

        var rating = el("div", "wv-ranked-rating");
        rating.appendChild(el("strong", "", number(record.rating, 2)));
        rating.appendChild(el("span", "", "rating"));
        row.appendChild(rating);

        row.addEventListener("click", function () {
          var result = typeof WV.sendAction === "function"
            ? WV.sendAction("ranked.select_movie", { movie_id: movieId }, {
                source: "wv.renderer.ranked.list"
              })
            : "noBridge";

          actionNote.textContent = "Selection request: " + result + ". Waiting for FileMaker acknowledgement.";
        });

        list.appendChild(row);
      });

      shell.appendChild(list);
    }

    shell.appendChild(actionNote);
    page.appendChild(shell);
    root.appendChild(page);
  }

  if (typeof WV.registerRenderer === "function") {
    WV.registerRenderer(render);
  } else {
    WV.render = render;
    WV._state = WV._state || {};
    WV._state.hasRenderer = true;
  }
})();
