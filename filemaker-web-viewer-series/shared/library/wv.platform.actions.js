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
     - "ok" means the request was handed to FileMaker.PerformScript.
     - FileMaker still validates the envelope and owns resulting state.
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

      global.FileMaker.PerformScript(
        "WV__Demo_Handle_Action",
        JSON.stringify(envelope)
      );

      return "ok";
    } catch (e) {
      try { console.error("WV.sendAction error:", e); } catch (_e) {}
      return "err";
    }
  };
})(window); 
