/* ============================================================
   W V   P L A T F O R M   B O O T
   Index: 24
   Name:  wv.platform.boot.js
   Purpose:
     - Safe render bridge + renderer registration
     - Debug HUD (toggle via __wv.debug + default via __wv.debug_mode)
     - Platform-owned renderCount (increments only on actual render)
     - HUD status coloring (gold default + green/red accents)
     - HUD scroll + no vertical clipping
     - Mode pill in header
     - BOOTSTRAP FAILSAFE: show HUD until first context arrives, then defer to ctx.__wv.debug
   Dependencies:
     - LIB[22] runtime
     - LIB[23] context
   ============================================================ */

(function () {

 if (!window.WV) return;

 WV._state = WV._state || {};
 WV._state.renderCount = WV._state.renderCount || 0;
 WV._state.hasRenderer = !!WV._state.hasRenderer;

 // --------------------------------------------
 // Track whether we have ever received a context
 // --------------------------------------------
 WV._state._ctxSeen = !!WV._state._ctxSeen;

 // ------------------------------------------------------------
 // Default render sentinel (so we can detect when a page replaces it)
 // ------------------------------------------------------------

 WV._state._defaultRenderFn = WV._state._defaultRenderFn || function (_ctx) {
  // default: do nothing
 };

 if (typeof WV.render !== "function") {
  WV.render = WV._state._defaultRenderFn;
 }

 // ------------------------------------------------------------
 // Debug HUD
 // ------------------------------------------------------------

 function ensureHud() {
  try {

   if (WV._hud && WV._hud.wrap) return;

   // --- wrapper ---
   var wrap = document.createElement("div");
   wrap.id = "wv-hud";
   wrap.style.position = "fixed";
   wrap.style.top = "6px";
   wrap.style.right = "6px";
   wrap.style.zIndex = "999999";

   // sizing (keep inside WV)
   wrap.style.width = "300px";
   wrap.style.maxWidth = "calc(100vw - 12px)";

   // height + clipping behavior (NO vertical clipping; body scrolls)
   wrap.style.maxHeight = "82vh";
   wrap.style.overflow = "hidden";

   // appearance
   wrap.style.borderRadius = "12px";
   wrap.style.background = "rgba(0,0,0,0.85)";
   wrap.style.border = "1px solid rgba(255,255,255,0.18)";
   wrap.style.boxShadow = "0 8px 26px rgba(0,0,0,0.35)";

   // allow HUD interactions (header toggle + body scroll)
   wrap.style.pointerEvents = "auto";

   // typography
   wrap.style.fontFamily = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace";
   wrap.style.fontSize = "8px";
   wrap.style.lineHeight = "1.2";

   // --- header (sticky + clickable) ---
   var header = document.createElement("div");
   header.style.position = "sticky";
   header.style.top = "0";
   header.style.padding = "7px 10px";
   header.style.borderBottom = "1px solid rgba(255,255,255,0.12)";
   header.style.background = "rgba(0,0,0,0.85)";
   header.style.borderTopLeftRadius = "12px";
   header.style.borderTopRightRadius = "12px";

   header.style.pointerEvents = "auto";
   header.style.cursor = "default";
   header.style.userSelect = "none";
   header.style.webkitUserSelect = "none";

   // header row (title + pill)
   var headRow = document.createElement("div");
   headRow.style.display = "flex";
   headRow.style.alignItems = "center";
   headRow.style.justifyContent = "space-between";
   headRow.style.gap = "8px";

   // title line
   var title = document.createElement("div");
   title.textContent = "WV DEBUG HUD";
   title.style.fontWeight = "600";
   title.style.letterSpacing = "0.4px";
   title.style.color = "#95821D";

   // pill
   var pill = document.createElement("div");
   pill.textContent = "FULL";
   pill.style.fontSize = "8px";
   pill.style.fontWeight = "700";
   pill.style.letterSpacing = "0.6px";
   pill.style.padding = "2px 6px";
   pill.style.borderRadius = "999px";
   pill.style.border = "1px solid rgba(149,130,29,0.55)";
   pill.style.background = "rgba(149,130,29,0.14)";
   pill.style.color = "#95821D";
   pill.style.flex = "0 0 auto";
   pill.style.userSelect = "none";
   pill.style.webkitUserSelect = "none";

   headRow.appendChild(title);
   headRow.appendChild(pill);
   header.appendChild(headRow);

   // --- body (scrollable) ---
   var body = document.createElement("div");
   body.style.margin = "0";
   body.style.padding = "8px 10px";
   body.style.whiteSpace = "pre-wrap";

   // body is the only scroll region
   body.style.overflow = "auto";
   body.style.overflowX = "hidden";
   body.style.webkitOverflowScrolling = "touch";

   // allow scroll / text selection inside HUD if desired
   body.style.pointerEvents = "auto";

   wrap.appendChild(header);
   wrap.appendChild(body);

   document.documentElement.appendChild(wrap);

   WV._hud = {
    wrap: wrap,
    header: header,
    title: title,
    pill: pill,
    body: body,
    last: "",
    mode: "full"
   };

   // ------------------------------------------------------------
   // Toggle handlers (FileMaker-proof) — UPDATED
   // ------------------------------------------------------------

   (function () {

    function doToggle(ev) {
     try {
      WV._hud.mode = (WV._hud.mode === "mini") ? "full" : "mini";
      // bust cache so you always see an immediate change
      WV._hud.last = "";
      hudUpdate(true);
     } catch (e) {}
    }

    function bind(el) {
     if (!el) return;

     var lastTs = 0;
     var lastX  = 0;
     var lastY  = 0;

     function getXY(ev) {
      try {
       if (ev && ev.touches && ev.touches.length) {
        return {
         x: ev.touches[0].clientX || 0,
         y: ev.touches[0].clientY || 0
        };
       }
       return { x: ev.clientX || 0, y: ev.clientY || 0 };
      } catch (e) {
       return { x: 0, y: 0 };
      }
     }

     function maybeToggle(ev) {
      try {

       // Native dblclick when it actually fires
       if (ev && ev.type === "dblclick") {
        if (ev.preventDefault) ev.preventDefault();
        if (ev.stopPropagation) ev.stopPropagation();
        doToggle(ev);
        return;
       }

       // Some builds expose click-count here
       if (ev && typeof ev.detail === "number" && ev.detail === 2) {
        if (ev.preventDefault) ev.preventDefault();
        if (ev.stopPropagation) ev.stopPropagation();
        doToggle(ev);
        return;
       }

       // Single click toggles directly
       if (ev && ev.type === "click") {
        if (ev.preventDefault) ev.preventDefault();
        if (ev.stopPropagation) ev.stopPropagation();
        doToggle(ev);
        return;
       }

       var now = Date.now();
       var pt  = getXY(ev);

       var dt = now - (lastTs || 0);
       var dx = Math.abs((pt.x || 0) - (lastX || 0));
       var dy = Math.abs((pt.y || 0) - (lastY || 0));

       lastTs = now;
       lastX  = pt.x || 0;
       lastY  = pt.y || 0;

       // Two clicks/taps within 340ms and within 10px => toggle
       if (dt > 0 && dt < 340 && dx <= 10 && dy <= 10) {
        if (ev && ev.preventDefault) ev.preventDefault();
        if (ev && ev.stopPropagation) ev.stopPropagation();
        doToggle(ev);
       }

      } catch (e) {}
     }

     // Capture phase helps in FM WV
     el.addEventListener("dblclick",  maybeToggle, true);
     el.addEventListener("click",     maybeToggle, true);
    }

    // Bind to header + its children only
    bind(header);
    bind(title);
    bind(pill);

   })();

  } catch (e) {}
 }

 function normalizeDebugFlag(val) {
  var out = { raw: val, isFalse: false, isTrue: false, mode: "" };
  try {
   if (val === true || val === 1) { out.isTrue = true; return out; }
   if (val === false || val === 0) { out.isFalse = true; return out; }

   if (typeof val === "string") {
    var v = val.toLowerCase();
    if (v === "false" || v === "0" || v === "") { out.isFalse = true; return out; }
    if (v === "true" || v === "1") { out.isTrue = true; return out; }
    if (v === "mini" || v === "full") { out.isTrue = true; out.mode = v; return out; }
   }
  } catch (_e) {}
  return out;
 }

 function normalizeMode(val) {
  try {
   if (typeof val === "string" && (val === "mini" || val === "full")) return val;
  } catch (_e) {}
  return "";
 }

 // ------------------------------------------------------------
 // HUD visibility + mode resolution
 // ------------------------------------------------------------

 function resolveHudMode() {
  try {
   var ctx = (typeof WV.getContext === "function") ? WV.getContext() : {};
   var wv  = (ctx && ctx.__wv && typeof ctx.__wv === "object") ? ctx.__wv : {};

   var dInfo = normalizeDebugFlag(wv.debug);
   var mInfo = normalizeMode(wv.debug_mode);

   // --------------------------------------------
   // Bootstrap failsafe:
   // Show until first context arrives, then obey ctx.__wv.debug
   // --------------------------------------------
   if (!WV._state._ctxSeen) {
    return { show: true, mode: (WV._hud && WV._hud.mode) ? WV._hud.mode : "full", diag: { raw: wv.debug, show: true, mode: (WV._hud && WV._hud.mode) ? WV._hud.mode : "full" } };
   }

   // HARD OFF: explicit false means hide regardless of debug_mode
   if (dInfo.isFalse) {
    return { show: false, mode: "full", diag: { raw: wv.debug, show: false, mode: "full" } };
   }

   // Determine whether HUD is enabled
   var enabled = dInfo.isTrue || !!dInfo.mode || (mInfo === "mini" || mInfo === "full");

   if (!enabled) {
    return { show: false, mode: "full", diag: { raw: wv.debug, show: false, mode: "full" } };
   }

   // Requested mode (only matters if enabled)
   var requested = (mInfo === "mini" || mInfo === "full") ? mInfo :
    (dInfo.mode === "mini" || dInfo.mode === "full") ? dInfo.mode :
    "full";

   // Keep local toggle if present; context only seeds initial default
   var mode =
    (WV._hud && (WV._hud.mode === "mini" || WV._hud.mode === "full"))
     ? WV._hud.mode
     : requested;

   return { show: true, mode: mode, diag: { raw: wv.debug, show: true, mode: mode } };

  } catch (e) {
   return { show: false, mode: "full", diag: { raw: undefined, show: false, mode: "full" } };
  }
 }

 function esc(s) {
  try {
   return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
  } catch (e) {
   return "";
  }
 }

 function line(label, value, color) {
  var c = color || "#95821D";
  return '<div style="color:' + c + '"><span style="opacity:.85">' + esc(label) + '</span> ' + esc(value) + '</div>';
 }

 function hudText(mode) {
  try {

   var ctx = (typeof WV.getContext === "function") ? WV.getContext() : {};
   var wv  = (ctx && ctx.__wv && typeof ctx.__wv === "object") ? ctx.__wv : {};

   var GOLD  = "#95821D";
   var GREEN = "#36D26E";
   var RED   = "#FF5C5C";
   var DIM   = "rgba(149,130,29,0.70)";

   var hasRenderer = !!WV._state.hasRenderer;
   var pending     = !!WV._state.pendingContext;

   var rendererColor = hasRenderer ? GREEN : (pending ? RED : GOLD);

   // FIX: page fallback to __wv.viewer.index
   var pageVal = (wv.page !== undefined && wv.page !== null && wv.page !== "") ? wv.page :
    (wv.viewer && wv.viewer.index !== undefined ? wv.viewer.index : "");

   var out = "";
   out += line("renderCount:", String(WV._state.renderCount || 0), GOLD);
   out += line("hasRenderer:", String(hasRenderer), rendererColor);
   out += line("pendingContext:", String(pending), pending ? (hasRenderer ? GOLD : RED) : DIM);
   out += line("page:", String(pageVal), GOLD);
   out += line("lastUpdateTs:", String(WV._state.lastUpdateTs || ""), DIM);

   if (mode === "mini") {
    return out;
   }

   var dump = "";
   try {
    dump = JSON.stringify(ctx, null, 2);
   } catch (_e) {
    dump = "[ctx stringify error]";
   }

   out += '<div style="height:6px"></div>';
   out += '<div style="color:' + DIM + '; opacity:.95">ctx:</div>';
   out += '<div style="color:' + DIM + '; white-space:pre-wrap">' + esc(dump) + '</div>';

   return out;

  } catch (e) {
   return '<div style="color:#95821D">renderCount: ' + esc(WV._state.renderCount || 0) + '</div>' +
          '<div style="color:#FF5C5C">(err building HUD text)</div>';
  }
 }

 function hudUpdate(force) {
  try {

   ensureHud();

   var r = resolveHudMode();
   if (!WV._hud || !WV._hud.wrap || !WV._hud.body) return;

   WV._hud.wrap.style.display = r.show ? "block" : "none";
   if (!r.show) return;

   // persist mode
   WV._hud.mode = r.mode;

   // pill text
   if (WV._hud.pill) {
    WV._hud.pill.textContent = (r.mode === "mini") ? "MINI" : "FULL";
   }

   WV._hud.wrap.style.maxHeight = (r.mode === "mini") ? "18vh" : "82vh";

   WV._hud.body.style.height =
    (r.mode === "mini")
     ? "calc(18vh - 44px)"
     : "calc(82vh - 44px)";

   var t = hudText(r.mode);

   if (force || t !== WV._hud.last) {
    WV._hud.body.innerHTML = t;
    WV._hud.last = t;
   }

  } catch (e) {}
 }

 // ------------------------------------------------------------
 // Renderer detection
 // ------------------------------------------------------------

 function detectRenderer() {
  try {

   if (typeof WV.render === "function" && WV.render !== WV._state._defaultRenderFn) {
    WV._state.hasRenderer = true;
    return true;
   }

   return !!WV._state.hasRenderer;

  } catch (e) {
   return !!WV._state.hasRenderer;
  }
 }

 // ------------------------------------------------------------
 // Safe render (platform-owned render count + hud update)
 // ------------------------------------------------------------

 WV._safeRender = WV._safeRender || function (ctx) {

  try {

   WV._state.renderCount = (WV._state.renderCount || 0) + 1;

   if (typeof WV.render === "function") {
    WV.render(ctx || {});
   }

   hudUpdate();
   return "ok";

  } catch (e) {

   try { console.error("WV.render error:", e); } catch (_e) {}
   hudUpdate();
   return "err";

  }

 };

 // ------------------------------------------------------------
 // Renderer registration (optional convenience)
 // ------------------------------------------------------------

 WV.registerRenderer = WV.registerRenderer || function (fn) {

  try {

   if (typeof fn === "function") {
    WV.render = fn;
    WV._state.hasRenderer = true;

    if (WV._state.pendingContext) {
     var c = WV._state.pendingContext;
     WV._state.pendingContext = null;
     WV._safeRender(c);
    }
   }

   hudUpdate();
   return "ok";

  } catch (e) {

   try { console.error("WV.registerRenderer error:", e); } catch (_e) {}
   hudUpdate();
   return "err";

  }

 };

 // ------------------------------------------------------------
 // Context change hook (INSTALL UNCONDITIONALLY)
 // ------------------------------------------------------------

 WV.onContextChange = function (ctx) {

  try {

   var wasSeen = !!WV._state._ctxSeen;

   // mark that context has arrived
   WV._state._ctxSeen = true;

   var has = detectRenderer();

   if (!has) {
    WV._state.pendingContext = ctx;
    hudUpdate();
    return "noRender";
   }

   if (!wasSeen) {
    try {
     var wv = (ctx && ctx.__wv && typeof ctx.__wv === "object") ? ctx.__wv : {};
     if (wv.debug_diag === true) {
      console.log("WV ctxSeen flipped", { ctxSeen: true });
     }
    } catch (_e) {}
   }

   return WV._safeRender(ctx);

  } catch (e) {

   hudUpdate();
   return "err";

  }

 };

 // One HUD update at boot
 hudUpdate();

})();

