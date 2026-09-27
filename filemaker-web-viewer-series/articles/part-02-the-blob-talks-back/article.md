# Context In, Actions Out: Two-Way FileMaker Web Viewer Communication

<aside class="article-resources" aria-label="Article files">
  <a class="article-resources__repository" href="https://github.com/LonCook/filemaker-articles/tree/main/filemaker-web-viewer-series/articles/part-02-the-blob-talks-back">
    <img src="https://raw.githubusercontent.com/LonCook/filemaker-articles/main/assets/icons/mark-github-16.svg" alt="" width="18" height="18">
    <span>View this article's files on GitHub</span>
  </a>
  <a class="article-resources__download" href="https://github.com/LonCook/filemaker-articles/raw/refs/heads/main/filemaker-web-viewer-series/articles/part-02-the-blob-talks-back/demo/Flicks_WebViewer_Framework_02_TwoWay.fmp12" download>
    <img src="https://raw.githubusercontent.com/LonCook/filemaker-articles/main/assets/icons/file-arrow-down-16.svg" alt="" width="18" height="18">
    <span>Download the demo file: Flicks_WebViewer_Framework_02_TwoWay.fmp12</span>
  </a>
</aside>

Last round, we took the giant HTML blob apart and gave the pieces names. FileMaker assembled those pieces into a Web Viewer, built an explicit context payload, and pushed that payload into JavaScript. The renderer drew what it received. It did not query FileMaker, invent a second copy of application state, or develop opinions about which record should be current.

Everybody stayed in their lane. It was almost suspiciously well behaved.

That is where we left things:

```text
FileMaker -> Web Viewer
```

That one-way arrangement was deliberate. FileMaker owned the selected movie, the selected genre, the payload, and the timing; JavaScript owned the rendering. Clean boundary. Easy to inspect. Also read-only.

That is fine for a chart or a status panel. It becomes a little harder to defend after we draw a button. A button is a promise. If clicking it does nothing, we have not built an interaction; we have decorated a rectangle.

So this pass gives the viewer one disciplined way to talk back.

We will add two buttons to the context card. When the user clicks one, JavaScript will package the intent into a small JSON envelope and hand it to one FileMaker script. FileMaker will validate the envelope, show us exactly what arrived, update a few demo fields, and push an acknowledgement back into the viewer that is already loaded.

By the end, we can follow the whole trip without asking either side to take our word for it:

```text
FileMaker context
  -> Web Viewer render
  -> JavaScript action
  -> FileMaker handler
  -> context acknowledgement
```

Calling a FileMaker script from JavaScript is an established FileMaker capability, but we have not used it in this series yet. Last round stopped at the one-way context push. Here we add the return call and, more importantly, decide what happens around it: once JavaScript can talk back, who owns the decision?

Our answer stays simple:

```text
JavaScript reports intent.
FileMaker decides what that intent means.
```

The viewer can say, “The user clicked `Mark Movie` for this id.” It does not get to decide what is marked, which record changes, or whether the request is allowed. In this demo, FileMaker validates the request, records it in visible global fields, and acknowledges it without changing production data.

That ownership boundary is the work. Everything else is plumbing with better labels.

## You Are Not Expected To Hand-Write This JavaScript

If JavaScript is not part of your daily FileMaker work, the code ahead may look like the series has quietly changed its admission requirements. It has not.

The JavaScript in this demo was developed with an AI co-developer. I defined the job: the context shape, the action-envelope contract, the FileMaker handler name, the allowed return values, and the state the Web Viewer is not allowed to own. The AI helped produce and revise the JavaScript inside those boundaries. My part is to review the result against the contract and test the completed path in FileMaker; generated code is a draft, not evidence that the feature works.

That is part of why the module structure matters. “Make the Web Viewer interactive” is a broad request with excellent opportunities for confident improvisation. “Add `WV.sendAction` to module `25`; emit this JSON shape; call this FileMaker script; do not mutate application state” gives the AI a smaller job and gives us something specific to review.

We are not going to unpack that entire collaboration loop here. The prompting, context we give the AI, code review, native FileMaker testing, and revision cycle deserve their own pass. We will cover that workflow in an upcoming round.

For now, read the JavaScript as an implementation of the contract we are building—not as an entrance exam. You should understand what crosses the boundary and who owns the result. You do not need to produce every function from a blank editor and a determined expression.

## Why One-Way Context Was Not Enough

A read-only Web Viewer is not a failed Web Viewer. Plenty of useful surfaces never need to send anything back: charts, summaries, dashboards, status panels, the occasional stern warning nobody reads.

But the moment we add a button, selectable row, filter control, or drill-down target, the user can express intent inside JavaScript. We need a path for that event to reach FileMaker.

When the page is running inside a FileMaker Web Viewer, FileMaker exposes `window.FileMaker.PerformScript`. The first argument is the FileMaker script name. The second is text that the script receives through `Get ( ScriptParameter )`.

We could build the whole request directly inside the button handler:

```js
markButton.addEventListener("click", function () {
  var ctx = WV.getContext();
  var defaults = ctx.defaults || {};

  var action = {
    "__wv_action": {
      "version": 1,
      "source": "wv.renderer.framework.context"
    },
    "type": "demo.mark_movie",
    "payload": {
      "movie_id": defaults.movie_id || "",
      "genre_id": defaults.genre_id || ""
    }
  };

  window.FileMaker.PerformScript(
    "WV__Demo_Handle_Action",
    JSON.stringify(action)
  );
});
```

That call asks FileMaker to run `WV__Demo_Handle_Action` with the serialized object as its script parameter. It does not synchronously return the FileMaker script result to JavaScript. Outside a FileMaker Web Viewer, `window.FileMaker` is not present at all.

The direct version is valid, but it makes the renderer responsible for details that every action will need:

- the FileMaker handler script name
- the action contract version
- the metadata shape
- JSON serialization
- the check for a native FileMaker bridge
- local error handling

Leave those details in each click handler and they will drift. One button sends an object. Another sends a bare id. A filter sends a return-delimited list because it was late and technically worked.

Each call is understandable on its own. Six months later, the collection becomes archaeology. You find a script name, a bare id, and a comment that says “used by Web Viewer,” which is technically documentation in the same way a luggage tag is a travel itinerary.

We can do better without building an action framework large enough to require governance.

Every button will use the same bridge. Every request will have the same outer shape. FileMaker receives one predictable object, validates it, records what happened, and decides whether anything else should change.

For this demo, the answer to that last question is no. The handler writes only to visible global demo fields. `MOVIE`, `GENRE`, ratings, rankings, and every other native record can remain unbothered.

That may feel anticlimactic when the button says `Mark Movie`. Good. We are proving the return path before attaching it to consequences. Plumbing is easier to inspect before the walls are closed and the carpet is wet.

## An Action Is Intent, Not State

Let us be slightly fussy about one word: intent.

The Web Viewer knows what the user did inside the viewer. It can tell us:

- the user clicked `Inspect Context`
- the user clicked `Mark Movie`
- the click happened while movie `MOVIE-...` and genre `GENRE-...` were in the current context

What it should not decide is:

- which FileMaker record becomes current
- whether a movie field should be modified
- whether a transaction should commit
- whether a different layout should open
- whether the action is even allowed

Those are FileMaker decisions.

In a tiny demo, this can look like ceremony. Both sides live in one file. One person wrote the code. We could let the click handler call whatever script it likes and be home in time for dinner.

The boundary earns its keep later: when the action changes a real record, when privilege sets matter, when the current layout is not the one the renderer expected, or when the same Web Viewer module turns up somewhere else. Boundaries are often most annoying five minutes before they become useful.

So instead of claiming that it changed anything, the renderer sends this:

```json
{
  "__wv_action": {
    "version": 1,
    "source": "wv.renderer.framework.context",
    "page": 62,
    "ts": "2026-07-20T02:44:24.933Z"
  },
  "type": "demo.mark_movie",
  "payload": {
    "movie_id": "MOVIE-D1B6EDFD-71C1-4904-B08B-350754D7DFDC",
    "genre_id": "GENRE-303185A0-4C08-48BC-95D3-932558B1DF5A"
  }
}
```

FileMaker receives that object and decides what `demo.mark_movie` means here.

For now it means: validate the envelope, display it, increment a counter, update a status field, and push acknowledgement context back to the loaded viewer.

That is all. No movie record is harmed in the making of this demonstration.

The action name may sound more ambitious than the result. This is intentional. The demo proves that FileMaker received the request; it does not use an article about messaging contracts as an excuse to smuggle in record mutation wearing a novelty moustache.

## The Action Envelope

“Action envelope” sounds grander than the object deserves. It is a small JSON object with three parts:

| Path | Purpose |
| --- | --- |
| `__wv_action` | framework metadata used for versioning and debugging |
| `type` | stable name for the user intent |
| `payload` | values needed for FileMaker to interpret that intent |

The metadata tells us which contract version we are looking at, which module sent it, which page was active, and when the browser created it. The payload carries stable FileMaker ids. The dotted action type gives the intent a name we can recognize six months from now without consulting the original author, a séance, or both.

None of this is especially glamorous.

Good.

Boring contracts are easier to inspect, log, validate, and replay. Exciting contracts are how integrations become oral tradition.

We keep the envelope small on purpose. It does not contain a copy of every viewer state value. It does not tell FileMaker to execute arbitrary logic. It does not pretend the client timestamp is authoritative. It carries enough context for FileMaker to understand the request and then stops talking.

Two action types are enough here:

| Button | Action type | Payload |
| --- | --- | --- |
| `Inspect Context` | `demo.inspect_context` | current title, movie id, and genre id |
| `Mark Movie` | `demo.mark_movie` | current movie id and genre id |

The first action makes the contract easy to inspect. The second gives us an action that sounds like a state change while still leaving the decision with FileMaker.

The viewer never says, “I marked the movie.”

It says, “The user asked to mark this movie.”

That one verb tense is doing useful architectural work.

## One JavaScript Bridge For Viewer Actions

In the previous pass, module `23`, `wv.platform.context.js`, handled context moving from FileMaker into JavaScript. We could stuff the return trip into that same module. It is right there. It has “context” in the name. This is how junk drawers begin.

Instead, we add one small platform module for the other direction:

| Index | Module | Purpose |
| ---: | --- | --- |
| `25` | `wv.platform.actions.js` | build action envelopes and send them to a FileMaker handler |

Keeping context-in and actions-out separate is not a sacred law. It is simply easier to inspect two modules with one job each than one bridge module with a growing collection of errands.

The context module owns `WV_FM_PUSH` and current viewer context. The action module owns `WV.sendAction`. A renderer can consume both without knowing the details of either bridge.

The public API is small:

```js
WV.sendAction(type, payload, options)
```

Here is the complete module contract for this pass. The code is AI-assisted; the public API and ownership rules are the human review boundary.

```js
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
```

The function is intentionally plain. It turns a missing payload into `{}`, rejects an empty action type, remembers the last envelope for debugging, checks for the FileMaker bridge, and returns a short local result. Nobody had to invent middleware. We are all coping.

That return value does need a careful reading.

`ok` means JavaScript successfully handed the request to `FileMaker.PerformScript`. It does not mean FileMaker validated the action, authorized it, completed it, or changed any state. `FileMaker.PerformScript` starts the FileMaker script; it is not a synchronous round trip with a tiny certificate of moral correctness.

The acknowledgement comes through context later.

If the same assembled page is opened in an ordinary browser harness, `WV.sendAction` returns `noFileMaker`. That is more useful than throwing an exception, and considerably more honest than returning `ok` because the button had a positive attitude.

![The wv.platform.actions.js module in FileMaker, showing WV.sendAction handing its action envelope to WV__Demo_Handle_Action.](<screenshots/07-wv-send-action.png>)

## The Renderer Reports Intent

The good news for module `63`, `wv.renderer.framework.context.js`, is that it does not get promoted. It remains the context-card renderer we already built. We give it two buttons and a small acknowledgement area; we do not give it a working knowledge of FileMaker script architecture.

It does not learn how FileMaker scripts work. It does not call `FileMaker.PerformScript` directly. It calls the platform action API.

The relevant renderer excerpt looks like this:

```js
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
```

Notice where the payload values come from: the current context FileMaker already supplied. The renderer does not query FileMaker again at click time. It renders one context and reports intent against that same context. Fewer moving targets; fewer opportunities to debug a value that changed somewhere between looking at it and clicking it.

This keeps the path inspectable:

```text
FOCUS fields
  -> context JSON
  -> renderer values
  -> action payload
  -> FileMaker handler
```

If the wrong movie id comes back, there are only a few sensible places to look. This is what a contract buys us: not an absence of bugs, but fewer square miles in which they can establish a settlement.

![The FileMaker demo after context is pushed, with the rendered context card and both action buttons visible inside wv_main.](<screenshots/02-context-after-push.png>)

![The renderer module in FileMaker, showing the action rows, button helper, and call to WV.sendAction.](<screenshots/08-renderer-action-buttons.png>)

## FileMaker Receives The Envelope

On the FileMaker side, we give the Web Viewer one front door:

`WV__Demo_Handle_Action`

The script receives `Get ( ScriptParameter )` as raw text. We do not assume it is valid because it came from our own viewer. Client input remains client input even when the client is sitting politely inside a FileMaker layout and using our variable names.

The handler does four things:

1. Validate the root object and required envelope fields.
2. Store the formatted action JSON and action type in visible global fields.
3. Increment the handled-action count and update status.
4. Rebuild and push context so the viewer can render FileMaker's acknowledgement.

The demo fields are:

| Field | Purpose |
| --- | --- |
| `FOCUS::g_wv_action_json` | pretty-printed last valid action envelope |
| `FOCUS::g_wv_action_type` | last handled action type |
| `FOCUS::g_wv_action_count` | number of valid actions handled by FileMaker |
| `FOCUS::g_wv_action_status` | short validation or handling status |

They are global fields because this is a teaching surface, not an action-history data model. A production log may be useful later. Adding a table now would mostly prove that we know how to add tables.

Here is the handler as exported from the completed demo DDR:

```text
# WV__Demo_Handle_Action
# Purpose: Receive an action envelope from the Web Viewer and make it visible in FileMaker.
# In: Get ( ScriptParameter ) as raw JSON.
# Out: JSON status object.
# Anchor: FOCUS. Demo teaching glue; does not update production records.
# Calls: WV__Demo_Build_Context, WV__Demo_Push_Context.

Set Error Capture [ On ]

Set Variable [ $_raw; Value:GetAsText ( Get ( ScriptParameter ) ) ]
Set Variable [ $_formatted; Value:JSONFormatElements ( $_raw ) ]
Set Variable [ $_json_error; Value:EvaluationError ( JSONFormatElements ( $_raw ) ) ]
Set Variable [ $_root_error; Value:EvaluationError ( JSONGetElementType ( $_raw ; "" ) ) ]

If [ IsEmpty ( $_raw ) or $_formatted = "?" or
     $_json_error <> 0 or $_root_error <> 0 or
     JSONGetElementType ( $_raw ; "" ) <> JSONObject ]
  Set Field By Name [ "FOCUS::g_wv_action_json"; $_raw ]
  Set Field By Name [ "FOCUS::g_wv_action_type"; "" ]
  Set Field By Name [ "FOCUS::g_wv_action_status"; "Rejected action: invalid JSON envelope." ]
  Exit Script [ Result: JSONSetElement ( "{}"
    ; [ "ok" ; 0 ; JSONBoolean ]
    ; [ "error" ; "invalid_json" ; JSONString ]
  ) ]
End If

Set Variable [ $_type; Value:GetAsText ( JSONGetElement ( $_raw ; "type" ) ) ]
Set Variable [ $_version; Value:GetAsNumber ( JSONGetElement ( $_raw ; "__wv_action.version" ) ) ]
Set Variable [ $_source; Value:GetAsText ( JSONGetElement ( $_raw ; "__wv_action.source" ) ) ]

Set Variable [ $_invalid_envelope; Value:Let ( [
  type_error = EvaluationError ( JSONGetElement ( $_raw ; "type" ) ) ;
  payload_error = EvaluationError ( JSONGetElementType ( $_raw ; "payload" ) ) ;
  meta_error = EvaluationError ( JSONGetElementType ( $_raw ; "__wv_action" ) ) ;
  version_error = EvaluationError ( JSONGetElement ( $_raw ; "__wv_action.version" ) ) ;
  source_error = EvaluationError ( JSONGetElement ( $_raw ; "__wv_action.source" ) )
] ;
  type_error <> 0 or payload_error <> 0 or meta_error <> 0 or
  version_error <> 0 or source_error <> 0 or
  IsEmpty ( $_type ) or IsEmpty ( $_source ) or $_version <> 1 or
  JSONGetElementType ( $_raw ; "type" ) <> JSONString or
  JSONGetElementType ( $_raw ; "payload" ) <> JSONObject or
  JSONGetElementType ( $_raw ; "__wv_action" ) <> JSONObject or
  JSONGetElementType ( $_raw ; "__wv_action.version" ) <> JSONNumber or
  JSONGetElementType ( $_raw ; "__wv_action.source" ) <> JSONString
) ]

If [ $_invalid_envelope ]
  Set Field By Name [ "FOCUS::g_wv_action_json"; $_formatted ]
  Set Field By Name [ "FOCUS::g_wv_action_type"; "" ]
  Set Field By Name [ "FOCUS::g_wv_action_status"; "Rejected action: envelope shape is not valid." ]
  Exit Script [ Result: JSONSetElement ( "{}"
    ; [ "ok" ; 0 ; JSONBoolean ]
    ; [ "error" ; "invalid_envelope" ; JSONString ]
  ) ]
End If

Set Variable [ $_known_action; Value:$_type = "demo.inspect_context" or $_type = "demo.mark_movie" ]

If [ not $_known_action ]
  Set Field By Name [ "FOCUS::g_wv_action_json"; $_formatted ]
  Set Field By Name [ "FOCUS::g_wv_action_type"; $_type ]
  Set Field By Name [ "FOCUS::g_wv_action_status"; "Rejected action: unknown type " & $_type ]
  Exit Script [ Result: JSONSetElement ( "{}"
    ; [ "ok" ; 0 ; JSONBoolean ]
    ; [ "error" ; "unknown_action" ; JSONString ]
    ; [ "type" ; $_type ; JSONString ]
  ) ]
End If

Set Variable [ $_count; Value:GetAsNumber ( GetField ( "FOCUS::g_wv_action_count" ) ) + 1 ]
Set Variable [ $_status; Value:"Handled " & $_type ]

Set Field By Name [ "FOCUS::g_wv_action_json"; $_formatted ]
Set Field By Name [ "FOCUS::g_wv_action_type"; $_type ]
Set Field By Name [ "FOCUS::g_wv_action_count"; $_count ]
Set Field By Name [ "FOCUS::g_wv_action_status"; $_status ]

Perform Script [ “WV__Demo_Build_Context”; Parameter: "" ]
Perform Script [ “WV__Demo_Push_Context”; Parameter: "" ]
Set Variable [ $_push_result; Value:GetAsText ( Get ( ScriptResult ) ) ]

Exit Script [ Result: JSONSetElement ( "{}"
  ; [ "ok" ; 1 ; JSONBoolean ]
  ; [ "type" ; $_type ; JSONString ]
  ; [ "count" ; $_count ; JSONNumber ]
  ; [ "push_result" ; $_push_result ; JSONString ]
) ]
```

![WV__Demo_Handle_Action in the native FileMaker Script Workspace.](<screenshots/05-handler-script.png>)

The validation is intentionally visible. We check that the root is a JSON object, that `type` is a non-empty JSON string, that both `payload` and `__wv_action` are objects, and that the metadata carries version `1` plus a non-empty source. It is not glamorous code. It is the code that keeps “but the button only sends valid JSON” from becoming an incident report.

This is not a complete production authorization layer. It is enough to demonstrate the boundary honestly. The demo accepts only its two named action types; a well-formed surprise is still a surprise.

A production handler would also validate each action's payload shape, check current record and privilege context, route the request to focused scripts, and return or log more specific errors. That comes later, when the demo has real actions worth authorizing. A broad action router here would be a lovely framework in search of a reason.

The handler also does not trust the action timestamp, source label, or page index as FileMaker state. Those values are diagnostic metadata. FileMaker can use them when debugging; it should not confuse “the client said this” with “the application established this.”

## FileMaker Acknowledges Through Context

There is one small wrinkle. JavaScript starts the FileMaker handler, but `FileMaker.PerformScript` does not hand the script result back as a neat synchronous reply. The button knows it placed the call. It does not know what FileMaker decided.

Fortunately, we already have a return path. FileMaker can push new context.

The context we built last time gains one small `actions` object:

```json
{
  "__wv": {
    "page": 62,
    "source": "article_02_demo",
    "ts": "7/19/2026 7:44:24 PM"
  },
  "defaults": {
    "genre_id": "GENRE-303185A0-4C08-48BC-95D3-932558B1DF5A",
    "movie_id": "MOVIE-D1B6EDFD-71C1-4904-B08B-350754D7DFDC",
    "title": "Flicks Web Viewer Framework"
  },
  "actions": {
    "count": 2,
    "last_type": "demo.mark_movie",
    "status": "Handled demo.mark_movie"
  }
}
```

The action envelope and the context acknowledgement are different objects with different owners.

| Object | Built by | Meaning |
| --- | --- | --- |
| action envelope | JavaScript | “The user expressed this intent.” |
| context acknowledgement | FileMaker | “FileMaker handled the intent and this is the resulting viewer state.” |

That distinction prevents the renderer from congratulating itself too early, a habit software acquires remarkably quickly when `ok` is available as a string.

When the user clicks `Mark Movie`, the button can display `Action send result: ok` immediately. That means the bridge call was made. The acknowledgement area changes only after FileMaker validates the envelope, updates its fields, rebuilds context, and pushes that context back.

The full loop is now visible:

```text
FileMaker owns current context
  -> JavaScript renders it
  -> user clicks a viewer button
  -> JavaScript reports intent
  -> FileMaker validates and records the action
  -> FileMaker pushes acknowledged context
  -> JavaScript renders the new context
```

We have two-way communication without two competing owners.

![The FileMaker demo after Inspect Context, with the received action type, count, status, and action JSON visible beside the Web Viewer.](<screenshots/03-inspect-context-handled.png>)

![The FileMaker demo after Mark Movie, with FileMaker's acknowledgement rendered back inside wv_main and the handled action visible in the native fields.](<screenshots/04-mark-movie-handled.png>)

## Loading Order Matters

There is one easy way to make the new buttons look completely useless: load the renderer before the action module it calls.

Module `25` has to exist before module `63` asks for `WV.sendAction`.

The previous demo used this dependency closure:

```text
62 -> 20, 63
20 -> 21, 22, 23, 24
```

This version adds module `25` between the base package and renderer:

```text
62 -> 20, 25, 63
20 -> 21, 22, 23, 24
```

The page root still owns the demo-specific assembly. The base shell still owns its CSS, runtime, context bridge, and boot code. We are adding one dependency, not renegotiating the entire family tree.

After changing module records, the same cache contract still applies:

1. Commit the `LIBRARY_CODE` record.
2. Click `Rebuild Library` on `WV Framework - Modules`.
3. Reload `wv_main`.
4. Push current context.

We still do not hide this behind smart `ensure loaded` behavior. That improvement has a place later. Here, visible loading and visible cache rebuilds make the action path easier to prove.

![The native FileMaker module inventory for the two-way demo, including platform module 25 and renderer module 63.](<screenshots/06-module-inventory.png>)

## Walkthrough: Complete The Round Trip

If you skipped ahead to see the button actually do something, welcome. This is the payoff. The envelopes, module boundaries, and ownership rules above exist so the next few clicks are understandable rather than merely impressive.

We are going to send context into the Web Viewer, click an action inside it, watch the envelope arrive in FileMaker, and then watch FileMaker send acknowledgement context back. One complete round trip; both sides visible.

Open `WV Framework - Demo` in `Flicks_WebViewer_Framework_02_TwoWay.fmp12`. We will run the steps separately once so you can see each boundary. `Run All` is still there for later, when it has earned the right to be convenient.

The layout should still show the original inputs, context JSON, status field, and Web Viewer object named `wv_main`. It should now also show:

- last action type
- action count
- action status
- last action JSON

Keep both JSON fields visible. Think of them as the receipts for the trip:

```text
context JSON into the viewer
action JSON out of the viewer
```

Before the first run, select `wv_main` in Layout mode, open **Format > Web Viewer Setup...**, and enable `Allow JavaScript to perform FileMaker scripts`. Save the layout. The one-way demo had no reason to grant that permission, so the inherited checkbox is off. This is the sort of perfectly sensible default that can consume an indecent amount of afternoon.

### Step 1: Build Context

Choose a movie and genre, then click `Build Context`.

Confirm that `FOCUS::g_wv_context_json` contains valid JSON. Before any action has been handled, the `actions` object may show zero, an empty last type, and a waiting status.

Expected result: FileMaker has prepared the current context. The Web Viewer has not been asked to infer anything, contact anything, or helpfully remember what happened last time. A quiet start is still a start.

### Step 2: Load The Viewer

Click `Load Viewer`.

This still calls the direct load path for module `62` and object `wv_main`. The only difference is what gets assembled: module `25` is now in the package, and module `63` has buttons that know how to use it.

Expected result: the page shell loads and says `Waiting for context`. The renderer is registered, but the buttons are not visible yet because we have not given it anything to render. If the debug HUD is enabled, it should report `hasRenderer: true`; `renderCount` may still be zero. This is the assembled viewer waiting for the next step, not a renderer that has wandered off during installation.

![The Web Viewer immediately after Load Viewer: the shell is waiting for context while the debug HUD confirms that the renderer is registered.](<screenshots/01-waiting-after-load.png>)

### Step 3: Push Context

Click `Push Context`.

Expected result: the waiting surface is replaced by the rendered context card. It shows the current title, movie id, genre id, action acknowledgement values from `FOCUS::g_wv_context_json`, and the `Inspect Context` and `Mark Movie` buttons. At this point the action count should still be zero. We have installed a doorbell; nobody has pressed it.

If the context values appear but the buttons do not, check module `63`, rebuild the library, and reload the viewer before editing the handler. The handler cannot remove a button it has never met.

This is still the same context path. We are not replacing it; we are adding the return trip.

### Step 4: Inspect Context From The Viewer

Now click `Inspect Context` inside `wv_main`.

Expected result on the FileMaker layout:

- `FOCUS::g_wv_action_type` becomes `demo.inspect_context`
- `FOCUS::g_wv_action_count` increments
- `FOCUS::g_wv_action_status` becomes `Handled demo.inspect_context`
- `FOCUS::g_wv_action_json` shows the full formatted envelope

Expected result inside the viewer:

- the local note first shows `Action send result: ok`
- after FileMaker pushes acknowledgement context, the action count and last action values update

Watch the order. The first status belongs to JavaScript: the call was placed. The second belongs to FileMaker: the envelope was accepted and new context came back. They are related; they are not the same claim. That distinction is easy to lose when both messages happen quickly and everything is feeling cooperative.

### Step 5: Send A State-Looking Action

Now click `Mark Movie`.

Expected result on the FileMaker layout:

- `FOCUS::g_wv_action_type` becomes `demo.mark_movie`
- `FOCUS::g_wv_action_count` increments again; if you began with zero, it is now `2`
- `FOCUS::g_wv_action_status` becomes `Handled demo.mark_movie`
- `FOCUS::g_wv_action_json` shows the formatted `demo.mark_movie` envelope with the current movie and genre ids

Expected result inside the viewer:

- `Actions handled` becomes `2`
- `Last action` becomes `demo.mark_movie`
- `Action status` becomes `Handled demo.mark_movie`

Now inspect the selected movie record.

It should be unchanged.

The button reported intent. The demo handler chose a harmless teaching response. FileMaker kept ownership of the decision, including the decision not to mutate anything.

This is not a missing feature. It is the feature being demonstrated.

## Debugging The Two Directions Separately

Once the arrows point both ways, the usual debugging instinct is to stare at the entire loop and announce that “the Web Viewer” is broken. This is accurate in the broadest possible sense and useful in no sense at all.

Instead, ask how far the message traveled.

### The Button Does Nothing

First confirm that the viewer is running inside FileMaker.

If the same page is open in a browser harness, `window.FileMaker` will not exist and `WV.sendAction` should return `noFileMaker`. That is expected. A browser preview can test rendering and local event wiring; it cannot manufacture the native FileMaker bridge through enthusiasm.

Inside FileMaker, inspect the local button note:

- `noBridge` means the renderer cannot see `WV.sendAction`; check module `25` and dependency order.
- `badType` means the renderer passed an empty action type.
- `noFileMaker` means the native bridge is unavailable.
- `err` means the send function threw; inspect the Web Viewer console.
- `ok` means JavaScript called `FileMaker.PerformScript`; continue on the FileMaker side.

If the note says `ok` but the FileMaker fields remain unchanged, check `wv_main` in **Format > Web Viewer Setup...** and confirm `Allow JavaScript to perform FileMaker scripts` is enabled. The JavaScript bridge can accept the call while the Web Viewer object is still not permitted to run the script. Both sides are behaving as configured, which is rarely as comforting as it sounds.

### FileMaker Receives Bad JSON

Inspect `FOCUS::g_wv_action_json` before changing renderer layout code.

If the root JSON is invalid, inspect `JSON.stringify(envelope)` and the raw script parameter. If the JSON is valid but the handler rejects the shape, inspect `type`, `payload`, and `__wv_action`.

Do not start by changing CSS. CSS has many talents. Repairing a malformed JSON envelope is not among them, despite what some debugging sessions seem to imply.

### FileMaker Fields Change But The Viewer Does Not

The action-out path worked.

Check the acknowledgement path:

- Does `WV__Demo_Build_Context` include `actions.count`, `actions.last_type`, and `actions.status`?
- Did it write the new JSON to `FOCUS::g_wv_context_json`?
- Did `WV__Demo_Push_Context` return `ok`?
- Is the renderer reading `ctx.actions`?

Do not rewrite `WV.sendAction`. The request already arrived.

### The Action Contains The Wrong Id

Compare the values in this order:

1. `FOCUS::g_wv_context_json`
2. the values rendered in the context card
3. `payload` in `FOCUS::g_wv_action_json`

The first mismatch tells you which boundary failed. This is more productive than staring at the completed loop and declaring it “some kind of timing issue,” the traditional blessing placed upon integrations when evidence has become inconvenient.

## FileMaker Still Owns The Application

This is the moment when the ownership boundary gets tested. It was easy to say FileMaker owned the application while JavaScript could only render. Now JavaScript has a voice. It still does not get the keys.

FileMaker owns:

- native records and relationships
- current layout and record context
- selected movie and genre values
- context construction
- action validation
- action authorization and routing
- resulting application state
- acknowledgement context

JavaScript owns:

- rendering the context it receives
- local DOM event handling
- packaging user intent into an action envelope
- handing that envelope to the named FileMaker script
- rendering later acknowledgement context

The action envelope is not an instruction JavaScript is entitled to have obeyed. It is a request crossing a boundary. FileMaker can accept it, reject it, reinterpret it, or decide that the current record context makes it irrelevant.

That becomes especially important when the actions stop being harmless. A later handler may select a FileMaker record, open a detail card, update a rating, or change a ranking. The renderer can still report a stable action type and payload. FileMaker can evaluate privileges, current state, record locking, validation, and transaction rules where those concerns already live.

The Web Viewer remains a strong interface surface. It does not need to become a second application tier with a partial memory of FileMaker rules and a very confident event listener.

## Where The AI Co-Developer Fits

We are deliberately keeping the AI workflow in the background for now, but it is not a secret ingredient. The action module and renderer changes were developed with AI assistance.

The important connection here is the boundary. Without `WV.sendAction`, an AI-generated renderer can scatter direct `FileMaker.PerformScript` calls through click handlers, each with its own script name, parameter shape, and assumptions. Everything may still work, but the renderer is slowly becoming an unlabeled switchboard—every button has its own line into FileMaker, and the only routing diagram is the memory of whoever wired it. Memory, as usual, has not been versioned.

With one action API, the AI has a constrained job: call the named function with a known action type and payload. The FileMaker handler keeps validation and application decisions on the FileMaker side. That gives generated code a landing zone and gives us a reviewable contract.

In an upcoming pass, we will slow down and show the actual co-development loop: how the task is framed, what module and payload context the AI receives, how the output is reviewed, what gets tested in the native file, and how the next revision is constrained. For this pass, the reader only needs to know where the JavaScript came from and why we did not ask it to design the application while it was here.

## What We Are Not Adding Yet

This demo remains thin.

It does not add:

- the Flicks ranked-list renderer
- native FileMaker record arrays in the payload
- production record mutation
- automatic cache rebuild triggers
- smart `ensure loaded` behavior as the visible path
- navigation drawers, dashboard chrome, or production controls
- a general-purpose action router
- an action-history table

Those are not rejected ideas. They can wait; add them now and the return path we are trying to inspect disappears under the furniture.

The visible sequence remains:

```text
Build Context
  -> Load Viewer
  -> Push Context
  -> Click Web Viewer Action
  -> Handle In FileMaker
  -> Push Acknowledgement Context
```

There is enough machinery here to prove the round trip and the ownership rule. More machinery would make the demo look busier without making the contract clearer, a familiar achievement in framework work.

## Where This Goes Next

Next pass, the context gets something more substantial to carry.

FileMaker will shape native records into a richer JSON payload, and the Web Viewer will move toward the ranked-list surface from Flicks. The action envelope we just added comes with us; a row click or filter change can report intent through the same bridge while FileMaker continues to own native state.

That is why we stop here. We want the return path settled before repeated rows, selected-state rules, and real record data arrive. Otherwise the interesting renderer will get all the attention while the ownership contract quietly wanders off, which is how we end up maintaining two applications and insisting one of them is “just the Web Viewer.”

## Takeaway

We started with a viewer that could receive context and render it. Now it can talk back. The important part is that talking back does not create a second owner.

JavaScript packages user intent into a small action envelope. FileMaker validates the envelope, decides what it means, and pushes new context when the viewer needs to see the result. The Web Viewer gets to be interactive without becoming a second application tier that knows almost—but not quite—enough about the rules.

That is the pattern:

```text
Context in.
Actions out.
FileMaker owns the result.
```

Next pass, the payload gets native FileMaker records and the renderer finally earns something more interesting to draw. The action bridge comes with us; the custody arrangement does not change.
