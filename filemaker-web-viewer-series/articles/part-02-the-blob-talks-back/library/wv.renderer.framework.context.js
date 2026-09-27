/* ============================================================
   W V   R E N D E R E R
   Index: 63
   Name:  wv.renderer.framework.context.js

   Purpose:
     - Two-way context and action renderer for the framework demo
     - Renders the JSON context FileMaker pushes into the Web Viewer
     - Reports user intent through WV.sendAction

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
     - All user intent leaves through WV.sendAction.
     - FileMaker remains the owner of application state.
   ============================================================ */

(function () {

 if (!window.WV) return;

 function text(value, fallback) {
  if (value === undefined || value === null || value === "") {
   return fallback || "Not provided";
  }
  return String(value);
 }

 function el(tag, className, value) {
  var node = document.createElement(tag);
  if (className) node.className = className;
  if (value !== undefined && value !== null) node.textContent = String(value);
  return node;
 }

 function addRow(parent, label, value) {
  var row = el("div", "wv-context-row");
  row.appendChild(el("div", "wv-context-label", label));
  row.appendChild(el("div", "wv-context-value", text(value)));
  parent.appendChild(row);
 }

 function ensureStyles() {
  if (document.getElementById("wv-framework-context-style")) return;

  var style = document.createElement("style");
  style.id = "wv-framework-context-style";
  style.textContent =
   ".wv-context-page{" +
    "width:100%;height:100%;min-height:100%;" +
    "display:flex;align-items:center;justify-content:center;" +
    "padding:18px;box-sizing:border-box;" +
    "background:var(--wv-bg-main,#141414);" +
    "color:var(--wv-text-1,#fff);" +
    "font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;" +
   "}" +
   ".wv-context-card{" +
    "width:min(680px,100%);" +
    "border:1px solid rgba(255,255,255,.14);" +
    "background:rgba(0,0,0,.26);" +
    "border-radius:8px;" +
    "padding:18px 20px;" +
    "box-shadow:0 18px 42px rgba(0,0,0,.28);" +
   "}" +
   ".wv-context-eyebrow{" +
    "font-size:11px;text-transform:uppercase;letter-spacing:.08em;" +
    "color:var(--wv-accent-1,#CFA100);font-weight:700;margin-bottom:6px;" +
   "}" +
   ".wv-context-title{" +
    "font-size:24px;line-height:1.15;margin:0 0 4px 0;font-weight:750;" +
   "}" +
   ".wv-context-note{" +
    "font-size:13px;line-height:1.4;margin:0 0 16px 0;color:var(--wv-text-2,rgba(255,255,255,.78));" +
   "}" +
   ".wv-context-grid{" +
    "display:grid;grid-template-columns:120px 1fr;gap:8px 14px;margin:14px 0 0 0;" +
   "}" +
   ".wv-context-row{display:contents;}" +
   ".wv-context-label{" +
    "font-size:11px;color:var(--wv-text-3,rgba(255,255,255,.6));text-transform:uppercase;" +
   "}" +
   ".wv-context-value{" +
    "font-size:13px;color:var(--wv-text-1,#fff);font-variant-numeric:tabular-nums;overflow-wrap:anywhere;" +
   "}" +
   ".wv-context-actions{" +
    "display:flex;flex-wrap:wrap;gap:.65rem;margin-top:1rem;" +
   "}" +
   ".wv-context-action{" +
    "appearance:none;border:1px solid rgba(201,164,74,.75);border-radius:.45rem;" +
    "background:rgba(201,164,74,.12);color:inherit;cursor:pointer;font:inherit;" +
    "padding:.6rem .85rem;" +
   "}" +
   ".wv-context-action:hover,.wv-context-action:focus-visible{" +
    "background:rgba(201,164,74,.22);outline:none;" +
   "}" +
   ".wv-context-action-note{margin-top:.65rem;opacity:.75;}" +
   ".wv-context-json{" +
    "margin-top:16px;padding:12px;max-height:180px;overflow:auto;" +
    "border-radius:6px;background:rgba(255,255,255,.06);" +
    "border:1px solid rgba(255,255,255,.10);" +
    "font:11px/1.35 ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,'Liberation Mono','Courier New',monospace;" +
    "color:rgba(255,255,255,.82);white-space:pre-wrap;" +
   "}";

  document.head.appendChild(style);
 }

 function render(ctx) {
  ctx = ctx || {};

  var root = document.getElementById("wv-root");
  if (!root) {
   root = document.createElement("div");
   root.id = "wv-root";
   document.body.appendChild(root);
  }

  ensureStyles();

  var meta = ctx.__wv || {};
  var defaults = ctx.defaults || {};
  var state = WV._state || {};

  root.innerHTML = "";
  root.classList.add("wv-theme-gold");

  var page = el("section", "wv-context-page");
  var card = el("div", "wv-context-card");

  card.appendChild(el("div", "wv-context-eyebrow", "Context received"));
  card.appendChild(el("h1", "wv-context-title", text(defaults.title, "Untitled context")));
  card.appendChild(el("p", "wv-context-note", "These values came from FileMaker; the Web Viewer is only rendering the context it was handed. A radical concept, apparently."));

  var grid = el("div", "wv-context-grid");
  addRow(grid, "Movie ID", defaults.movie_id);
  addRow(grid, "Genre ID", defaults.genre_id);
  addRow(grid, "Page", meta.page);
  addRow(grid, "Source", meta.source);
  addRow(grid, "Timestamp", meta.ts);
  addRow(grid, "Pushes", state.pushCount || 0);
  addRow(grid, "Renders", state.renderCount || 0);

  var actionState = ctx.actions || {};
  addRow(grid, "Actions handled", actionState.count || 0);
  addRow(grid, "Last action", actionState.last_type || "None");
  addRow(grid, "Action status", actionState.status || "Waiting for an action");

  card.appendChild(grid);

  var actionBar = el("div", "wv-context-actions");
  var actionNote = el("div", "wv-context-action-note", "No action sent yet.");

  function addActionButton(label, type, payload) {
   var button = el("button", "wv-context-action", label);
   button.type = "button";

   button.addEventListener("click", function () {
    var result = typeof WV.sendAction === "function"
     ? WV.sendAction(type, payload, {
       source: "wv.renderer.framework.context"
      })
     : "noBridge";

    actionNote.textContent = "Action send result: " + result;
   });

   actionBar.appendChild(button);
  }

  addActionButton("Inspect Context", "demo.inspect_context", {
   title: defaults.title || "",
   movie_id: defaults.movie_id || "",
   genre_id: defaults.genre_id || ""
  });

  addActionButton("Mark Movie", "demo.mark_movie", {
   movie_id: defaults.movie_id || "",
   genre_id: defaults.genre_id || ""
  });

  card.appendChild(actionBar);
  card.appendChild(actionNote);

  var raw = el("pre", "wv-context-json");
  raw.textContent = WV.safeJsonStringify ? WV.safeJsonStringify(ctx, "{}") : JSON.stringify(ctx, null, 2);
  card.appendChild(raw);

  page.appendChild(card);
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

