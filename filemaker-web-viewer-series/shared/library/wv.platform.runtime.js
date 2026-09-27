/* ============================================================
   W V   P L A T F O R M   R U N T I M E
   Index: 22
   Name:  wv.platform.runtime.js
   Purpose:
     - Establish window.WV namespace + core lifecycle
     - Provide a stable API surface for all WV pages
     - Health check for “already loaded” gating
     - Optional debug HUD (driven by ctx.__wv.debug)
   ============================================================ */

(function () {

 // ------------------------------------------------------------
 // Bootstrap namespace
 // ------------------------------------------------------------

 if (!window.WV) {
  window.WV = {};
 }

 // Prevent re-init (if page scripts re-run)
 if (WV._platformInitialized) {
  return;
 }
 WV._platformInitialized = true;

 // ------------------------------------------------------------
 // Internal state
 // ------------------------------------------------------------

 WV._state = WV._state || {};
 WV._state.context = WV._state.context || {};
 WV._state.lastUpdateTs = WV._state.lastUpdateTs || null;

 WV._state.pushCount = WV._state.pushCount || 0;
 WV._state.renderCount = WV._state.renderCount || 0;

 WV._state.hasRenderer = !!WV._state.hasRenderer;
 WV._state.pendingContext = WV._state.pendingContext || null;

 // ------------------------------------------------------------
 // Health check (used by FM gating)
 // ------------------------------------------------------------

 WV.ping = function () {
  return "ok";
 };

 window.WV_PING = function () {
  try {
   return (window.WV && typeof WV.ping === "function") ? WV.ping() : "";
  } catch (e) {
   return "";
  }
 };

 // ------------------------------------------------------------
 // Safe JSON stringify helper (pages can use this)
 // ------------------------------------------------------------

 WV.safeJsonStringify = function (obj, fallback) {
  try {
   return JSON.stringify(obj, null, 2);
  } catch (e) {
   try { return String(obj); } catch (_e) {}
   return fallback || "";
  }
 };

 // ------------------------------------------------------------
 // Debug HUD (enabled by ctx.__wv.debug)
 // ------------------------------------------------------------

 WV._hudEnsure = function () {

  try {

   var id = "wv-debug-hud";
   var el = document.getElementById(id);

   if (!el) {
    el = document.createElement("div");
    el.id = id;
    el.style.position = "absolute";
    el.style.right = "8px";
    el.style.bottom = "8px";
    el.style.zIndex = "999999";
    el.style.padding = "8px 10px";
    el.style.borderRadius = "10px";
    el.style.fontFamily = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace";
    el.style.fontSize = "11px";
    el.style.lineHeight = "1.25";
    el.style.background = "rgba(0,0,0,0.55)";
    el.style.color = "rgba(255,255,255,0.9)";
    el.style.border = "1px solid rgba(255,255,255,0.18)";
    el.style.backdropFilter = "blur(6px)";
    el.style.whiteSpace = "pre";
    el.style.pointerEvents = "none";
    document.body.appendChild(el);
   }

   return el;

  } catch (e) {
   return null;
  }

 };

 WV._hudSetVisible = function (on) {
  try {
   var el = document.getElementById("wv-debug-hud");
   if (el) el.style.display = on ? "block" : "none";
  } catch (e) {}
 };

 WV._hudRender = function () {

  try {

   var ctx = WV.getContext ? WV.getContext() : (WV._state.context || {});
   var wv = (ctx && ctx.__wv && typeof ctx.__wv === "object") ? ctx.__wv : {};

   var debugOn = !!(wv.debug);

   // lazily create
   if (!debugOn) {
    WV._hudSetVisible(false);
    return;
   }

   var el = WV._hudEnsure();
   if (!el) return;

   WV._hudSetVisible(true);

   var lines = [];
   lines.push("WV DEBUG");
   lines.push("----------------");
   lines.push("page:    " + (wv.page !== undefined ? String(wv.page) : "—"));
   lines.push("ts:      " + (wv.ts || "—"));
   lines.push("pushes:  " + String(WV._state.pushCount || 0));
   lines.push("renders: " + String(WV._state.renderCount || 0));
   lines.push("ready:   " + (WV.ready ? String(!!WV.ready()) : "—"));
   lines.push("renderer:" + String(!!WV._state.hasRenderer));
   lines.push("queued:  " + String(!!WV._state.pendingContext));

   el.textContent = lines.join("\n");

  } catch (e) {}

 };

})();

