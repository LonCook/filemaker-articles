/* ============================================================
   W V   P L A T F O R M   C O N T E X T
   Index: 23
   Name:  wv.platform.context.js
   Purpose:
     - Define the canonical context API:
         WV.setContext( ctx )
         WV.getContext()
     - Notify visualization hook:
         WV.onContextChange( ctx )
   Dependencies:
     - Requires LIB[22] (window.WV)
   ============================================================ */

(function () {

 if (!window.WV) {
  return;
 }

 // ------------------------------------------------------------
 // API
 // ------------------------------------------------------------

 WV.getContext = function () {
  try {
   return WV._state && WV._state.context ? WV._state.context : {};
  } catch (e) {
   return {};
  }
 };

 // Returns: "ok" | "noRender" | "err"
 WV.setContext = function (ctx) {

  try {

   if (!WV._state) WV._state = {};
   if (!WV._state.context) WV._state.context = {};

   // Normalize input
   if (!ctx || typeof ctx !== "object") {
    ctx = {};
   }

   // Replace (not merge) for predictable semantics
   WV._state.context = ctx;
   WV._state.lastUpdateTs = Date.now();
   WV._state._ctxLastOp = "replace";
   WV._state._ctxLastMerged = false;

   // --------------------------------------------------------
   // Normalize __wv meta (viewer index + page alias)
   // --------------------------------------------------------
   try {
    var wv = (ctx && ctx.__wv && typeof ctx.__wv === "object") ? ctx.__wv : {};

    // Ensure viewer object exists when we have a page
    if ((!wv.viewer || typeof wv.viewer !== "object") && wv.page !== undefined && wv.page !== null && wv.page !== "") {
     wv.viewer = { index: wv.page };
    }

    // Keep page <-> viewer.index in sync (without overwriting explicit values)
    if (wv.viewer && typeof wv.viewer === "object") {
     if ((wv.viewer.index === undefined || wv.viewer.index === null || wv.viewer.index === "")
      && (wv.page !== undefined && wv.page !== null && wv.page !== "")) {
      wv.viewer.index = wv.page;
     }

     if ((wv.page === undefined || wv.page === null || wv.page === "")
      && (wv.viewer.index !== undefined && wv.viewer.index !== null && wv.viewer.index !== "")) {
      wv.page = wv.viewer.index;
     }
    }

    ctx.__wv = wv;
   } catch (_e) {}

   // --------------------------------------------------------
   // Sync debug flags from __wv on every push
   // --------------------------------------------------------
   try {
    var wv2 = (ctx && ctx.__wv && typeof ctx.__wv === "object") ? ctx.__wv : {};
    var d = wv2.debug;
    var dStr = (typeof d === "string") ? d.toLowerCase() : null;

    // keep raw and boolean
    WV._state.debug_raw = (wv2 && wv2.debug !== undefined) ? wv2.debug : undefined;
    WV._state.debug =
     (d === true) || (d === 1) || (dStr === "true") || (dStr === "1") ||
     (typeof d === "string" && (d === "mini" || d === "full"));

    WV._state.debug_mode = (typeof wv2.debug_mode === "string") ? wv2.debug_mode : undefined;

    // Optional diagnostics
    if (wv2.debug_diag === true) {
     try {
      console.log("WV.setContext diag",
       { debug_raw: WV._state.debug_raw, debug_mode: WV._state.debug_mode, ctxOp: WV._state._ctxLastOp });
     } catch (_e2) {}
    }
   } catch (_e) {}

   // Notify visualization layer (preferred)
   if (typeof WV.onContextChange === "function") {

    var r = WV.onContextChange(ctx);

    if (typeof WV.render !== "function") {
     return "noRender";
    }

    if (r === "err") {
     return "err";
    }

    return "ok";
   }

   // Fallback: call render directly if present
   if (typeof WV.render === "function") {
    WV.render(ctx);
    return "ok";
   }

   return "noRender";

  } catch (e) {

   try { console.error("WV.setContext error:", e); } catch (_e) {}
   return "err";

  }

 };

 // ------------------------------------------------------------
 // Optional wrapper for FileMaker JS injection
 // Accepts object; returns "ok"|"noRender"|"err"
 // ------------------------------------------------------------

 window.WV_SET_CONTEXT = function (ctx) {
  try {
   return (window.WV && typeof WV.setContext === "function") ? WV.setContext(ctx) : "noWV";
  } catch (e) {
   return "err";
  }
 };

 // ------------------------------------------------------------
 // FileMaker bridge
 // Accepts raw JSON string OR object
 // Returns: "ok" | "noWV" | "err"
 //
 // NOTE:
 //   - WV.setContext can return "noRender" if page isn't ready.
 //   - For the FM contract, we treat noRender as "err" so ensure-loaded can reload+retry.
 // ------------------------------------------------------------

 window.WV_FM_PUSH = function (raw) {

  try {

   if (!window.WV || typeof WV.setContext !== "function") {
    return "noWV";
   }

   var ctx = raw;

   if (typeof raw === "string") {
    if (!raw) {
     ctx = {};
    } else {
     ctx = JSON.parse(raw);
    }
   }

   var r = WV.setContext(ctx);

   if (r === "ok") return "ok";
   if (r === "err") return "err";

   return "err";

  } catch (e) {

   try { console.error("WV_FM_PUSH error:", e); } catch (_e) {}
   return "err";

  }

 };

})();

