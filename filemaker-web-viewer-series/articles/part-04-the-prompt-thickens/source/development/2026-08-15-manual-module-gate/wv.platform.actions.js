/* ============================================================
   W V   A C T I O N S
   Index: 25
   Name:  wv.platform.actions.js

   Purpose:
     - Build small action envelopes from Web Viewer user intent
     - Send those envelopes to a FileMaker handler script

   Dependencies:
     - LIB[22] wv.platform.runtime.js
     - LIB[23] wv.platform.context.js

   Exports:
     - WV.sendAction( type, payload, options )

   Public API:
     - WV.sendAction( type, payload, options )

   Notes:
     - "ok" means the request was handed directly to FileMaker.PerformScript.
     - FileMaker still validates the envelope and owns resulting state.

   Modified:
     - 16 Aug 2026 — Lon Cook / AI native-retry correction : remove the
       ineffective browser-driven reconstruction retry; FileMaker now owns
       post-transition context recovery.
     - 16 Aug 2026 — Lon Cook / AI ready-retry repair : retry a viewer-ready
       context request while FileMaker is completing a record transition,
       then stop immediately when authoritative context is received.
     - 16 Aug 2026 — Lon Cook / AI viewer-ready repair : request the existing
       FileMaker-owned context after a reconstructed viewer finishes loading.
     - 16 Aug 2026 — Lon Cook / AI direct-dispatch repair : keep the
       FileMaker bridge call inside the originating user event; the deferred
       timer could strand valid intents before WV__Demo_Handle_Action ran.
     - 16 Aug 2026 — Lon Cook / AI bounded-dispatch repair : remove the
       acknowledgement-held native lock; dispatch the first intent after the
       browser event returns and rate-limit newer intent to one latest action
       per 100 ms, so a delayed/lost context push cannot deadlock the bridge.
     - 16 Aug 2026 — Lon Cook / AI input-drain repair : coalesce the initial
       pointer-event burst for 100 ms before making exactly one native call
       with the latest intent.
     - 16 Aug 2026 — Lon Cook / AI re-entrancy repair : retain the native
       request lock through a short post-ack drain window so the latest
       coalesced intent cannot re-enter FileMaker before its handler returns.
     - 16 Aug 2026 — Lon Cook / AI acknowledgement repair : release the
       native request lock when WV_FM_PUSH receives authoritative context,
       rather than relying on a second FileMaker-to-viewer call.
     - 16 Aug 2026 — Lon Cook / AI structural repair : allow one native
       request in flight, coalesce newer intent, and release it only after
       FileMaker pushes authoritative acknowledgement context.
     - 16 Aug 2026 — Lon Cook / AI performance : defer the native bridge
       call until the originating browser event stack has returned.
   ============================================================ */

(function (global) {
  "use strict";

  var WV = global.WV = global.WV || {};

  function isObject(value) {
    return value && typeof value === "object" && !Array.isArray(value);
  }

  function currentMeta() {
    var ctx = {};

    try {
      ctx = typeof WV.getContext === "function" ? WV.getContext() : {};
    } catch (_e) {
      ctx = {};
    }

    return isObject(ctx.__wv) ? ctx.__wv : {};
  }

  // Returns: "ok" | "badType" | "noFileMaker" | "err"
  WV.sendAction = function (type, payload, options) {
    try {
      options = isObject(options) ? options : {};
      payload = isObject(payload) ? payload : {};
      type = typeof type === "string" ? type.trim() : "";

      if (!type) {
        return "badType";
      }

      var meta = currentMeta();
      var envelope = {
        "__wv_action": {
          "version": 1,
          "source": options.source || "wv.platform.actions",
          "page": meta.page || null,
          "ts": new Date().toISOString()
        },
        "type": type,
        "payload": payload
      };

      WV._state = WV._state || {};
      WV._state.lastActionEnvelope = envelope;

      if (!global.FileMaker ||
          typeof global.FileMaker.PerformScript !== "function") {
        return "noFileMaker";
      }

      WV._state.actionInFlight = true;
      WV._state.actionCoalesced = false;

      global.FileMaker.PerformScript(
        "WV__Demo_Handle_Action",
        JSON.stringify(envelope)
      );

      WV._state.actionInFlight = false;
      return "ok";
    } catch (e) {
      WV._state = WV._state || {};
      WV._state.actionInFlight = false;
      try { console.error("WV.sendAction error:", e); } catch (_e) {}
      return "err";
    }
  };
})(window);
