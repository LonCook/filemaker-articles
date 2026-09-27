# Two-Way Demo Build Instructions

Target article:

`Beyond the Web Viewer Blob: The Blob Talks Back`

Subtitle: *Actions Out*

Source FileMaker file:

`/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_01_Context.fmp12`

Target FileMaker file:

`/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_02_TwoWay.fmp12`

Pre-edit backup:

`/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_02_TwoWay.prestrip-2026-07-19.fmp12`

## Source Status On 19 Jul 2026

The target demo is built and has passed the native two-action smoke test.

Verified sources:

- `/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_02_TwoWay.fmp12`
- `filemaker-web-viewer-series/article two/Flicks_WebViewer_Framework_02_TwoWay_fmp12.xml`
- `filemaker-web-viewer-series/article two/Summary.xml`
- `filemaker-web-viewer-series/article two/LIBRARY_CODE.tab`

The fresh DDR reports 14 scripts, four action globals, and no custom functions. The library export contains all eight retained module records. The code inserts below have been reconciled to those native sources; they are no longer provisional build contracts wearing source-code costumes.

## Scope Contract

This pass adds only:

- four global action-inspection fields
- one visible action-inspection area on `WV Framework - Demo`
- one `LIBRARY_CODE` action module at index `25`
- two buttons in the existing context renderer
- one FileMaker handler script
- three acknowledgement values in the existing context payload

Do not add:

- the ranked-list renderer
- native record arrays or data shaping
- production record mutation
- smart `ensure loaded` behavior as the main path
- automatic cache-rebuild triggers
- navigation drawers or production application chrome
- an action-history table
- a broad router framework
- external JavaScript frameworks

The visible teaching path remains:

```text
Build Context
  -> Load Viewer
  -> Push Context
  -> Click Web Viewer Action
  -> WV__Demo_Handle_Action
  -> optional acknowledgement push
```

## Expected Final Inventory

Starting from the fresh one-way DDR baseline, the expected two-way changes are:

| Item | One-way baseline | Two-way target |
| --- | ---: | ---: |
| Retained scripts | 13 | 14 |
| `LIBRARY_CODE` records | 7 | 8 |
| Teaching page root | 62 | 62 |
| Web Viewer object | `wv_main` | `wv_main` |

Expected retained module closure:

```text
62 -> 20, 25, 63
20 -> 21, 22, 23, 24
```

Expected retained modules:

| Index | Name |
| ---: | --- |
| 20 | `wv.platform.base.html` |
| 21 | `wv.platform.base.css` |
| 22 | `wv.platform.runtime.js` |
| 23 | `wv.platform.context.js` |
| 24 | `wv.platform.boot.js` |
| 25 | `wv.platform.actions.js` |
| 62 | `wv.page.framework.context.html` |
| 63 | `wv.renderer.framework.context.js` |

These are the visible names confirmed in the completed target export. Payload names are separate metadata; module `20`, for example, is named `wv.platform.base.html` while its payload name remains `wv.base.shell.html`. FileMaker has allowed both statements to be true, which is generous of it.

## Build Sequence

Follow the sequence in order. Later steps depend on earlier fields, modules, or scripts.

### 1. Close, Clone, And Back Up

1. Close `Flicks_WebViewer_Framework_01_Context.fmp12` in FileMaker Pro.
2. Confirm the target and backup paths do not already exist.
3. Duplicate the source to the target.
4. Duplicate the untouched target to the pre-edit backup.
5. Open only `Flicks_WebViewer_Framework_02_TwoWay.fmp12`.
6. Confirm the open file/window name before entering Manage Database.

Safe shell sequence, if preferred:

```zsh
source_file='/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_01_Context.fmp12'
target_file='/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_02_TwoWay.fmp12'
backup_file='/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_02_TwoWay.prestrip-2026-07-19.fmp12'

test ! -e "$target_file" && test ! -e "$backup_file" &&
cp -p "$source_file" "$target_file" &&
cp -p "$target_file" "$backup_file"
```

If either destination exists, stop and resolve it explicitly. Do not turn a build instruction into an overwrite instruction because the command was shorter.

### 2. Update Visible Identity

Keep internal framework object names reusable.

Set visible labels to:

- solution name: `Flicks Web Viewer Framework`
- release/version label: `Two-Way Demo`

Update retained `SOLUTION` fields if present:

- `SOLUTION::name`
- `SOLUTION::release_notes`
- any retained visible release/version field

Do not rename these layouts:

- `WV Framework - Demo`
- `WV Framework - Modules`
- `WV Framework - Sample Data`
- `SOLUTION`, if retained as a hidden utility layout

Do not add `02` or another pass-specific label to reusable script, field, layout, object, or module names.

### 3. Add Global Action Fields

In Manage Database, add these fields to `FOCUS`:

| Field | Type | Storage option | Initial value |
| --- | --- | --- | --- |
| `g_wv_action_json` | Text | Use global storage | empty |
| `g_wv_action_type` | Text | Use global storage | empty |
| `g_wv_action_count` | Number | Use global storage | `0` |
| `g_wv_action_status` | Text | Use global storage | `Waiting for an action` |

Do not add a table, relationship, auto-enter id, timestamp pair, or history record for these values.

Confirm the inherited fields still exist:

- `FOCUS::g_wv_context_json`
- `FOCUS::g_wv_status`
- `FOCUS::g_wv_module_index`
- `FOCUS::g_wv_demo_title`
- `FOCUS::g_wv_demo_movie_id`
- `FOCUS::g_wv_demo_genre_id`

### 4. Add The Action Inspection Area

On `WV Framework - Demo`, add a compact group outside the Web Viewer containing:

| Label | Field | Display |
| --- | --- | --- |
| Last action type | `FOCUS::g_wv_action_type` | single line |
| Action count | `FOCUS::g_wv_action_count` | single line |
| Action status | `FOCUS::g_wv_action_status` | single line or short multi-line |
| Last action JSON | `FOCUS::g_wv_action_json` | scrollable multi-line |

Keep `FOCUS::g_wv_context_json` visible at the same time. The reader must be able to compare context sent into the viewer with action JSON returned from it.

Do not resize the layout into a production dashboard. Preserve the inherited inputs, direct buttons, status, and `wv_main` object.

Before leaving Layout mode, select `wv_main`, open **Format > Web Viewer Setup...**, and enable:

`Allow JavaScript to perform FileMaker scripts`

This native option is off in the inherited one-way demo. `window.FileMaker.PerformScript` can exist in the page while FileMaker quietly declines to run the requested script if this box remains unchecked. Save the layout change before testing either action button.

### 5. Add Module 25

On `WV Framework - Modules`, create one `LIBRARY_CODE` record.

Set:

- index: `25`
- name: `wv.platform.actions.js`
- enabled: match the enabled value used by modules `22`, `23`, and `63`
- payload MIME: `application/javascript`
- payload name: `wv.platform.actions.js`
- payload public: off, matching the other inline JavaScript platform modules

Paste this complete code into the module code field:

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

Commit the record before leaving it.

### 6. Insert Module 25 Into The Page Dependency Order

Open module `62`, the existing context-demo page root.

The verified one-way closure is:

```text
62 -> 20, 63
20 -> 21, 22, 23, 24
```

Add an executable expansion token for module `25` after the base package token and before the renderer token:

```text
LIB[20]
LIB[25]
LIB[63]
```

Do not merely add `LIB[25]` to the comment header. It must appear in the code region where the render script expands dependencies.

Preserve the existing HTML/script wrapper structure in module `62`. The exact insertion point is the line immediately before the executable `LIB[63]` expansion. Do not move module `24` out of module `20`; this pass changes the page root closure, not the base-shell closure.

Update module `62`'s header dependency list to include module `25`.

Commit the record.

### 7. Update The Renderer Acknowledgement Rows

Open module `63`, `wv.renderer.framework.context.js`.

Inside `render(ctx)`, the inherited source already defines:

- `ctx`
- `defaults`
- `grid`
- `card`
- `el(...)`
- `addRow(...)`

After the existing `Pushes` and `Renders` rows, but before `card.appendChild(grid)`, add:

```js
var actionState = ctx.actions || {};

addRow(grid, "Actions handled", actionState.count || 0);
addRow(grid, "Last action", actionState.last_type || "None");
addRow(grid, "Action status", actionState.status || "Waiting for an action");
```

This keeps acknowledgement rendering driven by FileMaker context.

### 8. Add The Renderer Action Buttons

Still in module `63`, add this immediately after `card.appendChild(grid)` and before the raw JSON `<pre>` is created:

```js
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

Do not call `FileMaker.PerformScript` in module `63`. All renderer actions go through `WV.sendAction`.

### 9. Add Minimal Button Styles

In module `63`'s existing `ensureStyles()` CSS text, add rules equivalent to:

```css
.wv-context-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  margin-top: 1rem;
}

.wv-context-action {
  appearance: none;
  border: 1px solid rgba(201, 164, 74, 0.75);
  border-radius: 0.45rem;
  background: rgba(201, 164, 74, 0.12);
  color: inherit;
  cursor: pointer;
  font: inherit;
  padding: 0.6rem 0.85rem;
}

.wv-context-action:hover,
.wv-context-action:focus-visible {
  background: rgba(201, 164, 74, 0.22);
  outline: none;
}

.wv-context-action-note {
  margin-top: 0.65rem;
  opacity: 0.75;
}
```

Match the existing color variables if the renderer already provides them. Do not introduce a new theme or component system for two buttons.

Commit module `63`.

### 10. Create `WV__Demo_Handle_Action`

Create one FileMaker script named exactly:

`WV__Demo_Handle_Action`

Place it with the existing `WV__Demo_*` scripts.

Use the exact 44-step script exported by the completed demo DDR:

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

Important handler behavior:

- invalid JSON is rejected
- a non-object root is rejected
- missing or mistyped `type`, `payload`, or `__wv_action` is rejected
- a missing source or action contract version other than `1` is rejected
- unknown action types are rejected
- rejected actions do not increment the handled count
- valid demo actions update only global `FOCUS` fields
- no `MOVIE`, `GENRE`, rating, or ranking field is modified

### 11. Extend `WV__Demo_Build_Context`

Open the inherited `WV__Demo_Build_Context` script.

Do not replace its existing call to:

`. webviewer . context . build ( -index ; -movie_id ; -genre_id ) : json`

Confirm that call receives this dependency-free JSON parameter:

```text
JSONSetElement ( "{}"
  ; [ "index" ; $_index ; JSONNumber ]
  ; [ "movie_id" ; $_movie_id ; JSONString ]
  ; [ "genre_id" ; $_genre_id ; JSONString ]
)
```

Do not substitute a `#()` parameter helper. The stripped demo does not include that custom function; FileMaker will turn the missing calculation into `?` error text, which is not especially persuasive JSON.

Immediately after the current step:

```text
Set Variable [ $_context_json; Value:Get ( ScriptResult ) ]
```

add a step that preserves an invalid framework result but extends a valid one:

```text
Set Variable [ $_context_json; Value:Let (
  [
    base = $_context_json ;
    valid = EvaluationError ( JSONFormatElements ( base ) ) = 0 ;
    action_count = GetAsNumber ( GetField ( "FOCUS::g_wv_action_count" ) ) ;
    action_type = GetAsText ( GetField ( "FOCUS::g_wv_action_type" ) ) ;
    action_status = GetAsText ( GetField ( "FOCUS::g_wv_action_status" ) )
  ] ;
  Case (
    not valid ; base ;
    JSONSetElement ( base
      ; [ "__wv.source" ; "article_02_demo" ; JSONString ]
      ; [ "actions.count" ; action_count ; JSONNumber ]
      ; [ "actions.last_type" ; action_type ; JSONString ]
      ; [ "actions.status" ; Case (
          IsEmpty ( action_status ) ; "Waiting for an action" ; action_status
        ) ; JSONString ]
    )
  )
) ]
```

Leave the rest of the inherited script intact:

- format the display JSON
- write `FOCUS::g_wv_context_json`
- update `FOCUS::g_wv_status`
- exit with raw context JSON

The expected context extension is:

```json
{
  "actions": {
    "count": 1,
    "last_type": "demo.mark_movie",
    "status": "Handled demo.mark_movie"
  }
}
```

Do not add action acknowledgement inside `. webviewer . context . build ...` for this article. Keeping the three demo fields in `WV__Demo_Build_Context` makes the teaching addition visible and avoids broadening the framework helper before the pattern has settled.

### 12. Keep Direct Loading Intact

Do not change the inherited visible scripts:

- `WV__Demo_Load_Viewer`
- `WV__Demo_Push_Context`
- `WV__Demo_Run_All`
- `WV__Demo_Rebuild_Library`

`WV__Demo_Run_All` should still run only:

1. `WV__Demo_Build_Context`
2. `WV__Demo_Load_Viewer`
3. `WV__Demo_Push_Context`

The user action happens after that sequence, inside `wv_main`.

Retain `. webviewer . ensure loaded ...` scripts only as carry-forward framework code. Do not wire them to the new demo buttons or make them the primary path.

### 13. Rebuild The Library And Reload

After all module edits:

1. Commit the current `LIBRARY_CODE` record.
2. Click `Rebuild Library` on `WV Framework - Modules`.
3. Confirm `WV__Demo_Rebuild_Library` returns a status object with `ok: true`.
4. Confirm `$$wv_loaded_map` was cleared by the inherited script.
5. Return to `WV Framework - Demo`.
6. Click `Load Viewer`.
7. Click `Push Context`.

Do not test action buttons against a viewer loaded before the cache rebuild. That only proves old code remains old when left undisturbed.

## Verification Sequence

### A. One-Way Regression Test

Run these separately:

1. `WV__Demo_Build_Context`
2. `WV__Demo_Load_Viewer`
3. `WV__Demo_Push_Context`

Confirm:

- module index is `62`
- object name is `wv_main`
- `FOCUS::g_wv_context_json` is valid JSON
- `__wv.source` is `article_02_demo`
- the context card renders current title, movie id, and genre id
- the action buttons are visible
- the push result is `ok`

### B. Inspect Context Action

Click `Inspect Context` inside `wv_main`.

Confirm:

- `WV__Demo_Handle_Action` runs
- `FOCUS::g_wv_action_type` is `demo.inspect_context`
- `FOCUS::g_wv_action_count` increments by one
- `FOCUS::g_wv_action_status` is `Handled demo.inspect_context`
- `FOCUS::g_wv_action_json` is valid, formatted JSON
- `payload.title`, `payload.movie_id`, and `payload.genre_id` match current context
- the viewer acknowledgement shows the new count and last type

### C. Mark Movie Action

Click `Mark Movie` inside `wv_main`.

Confirm:

- `FOCUS::g_wv_action_type` is `demo.mark_movie`
- the count increments again
- `payload.movie_id` and `payload.genre_id` match current context
- the acknowledgement returns through context without a full viewer reload
- no native movie, genre, rating, or ranking record changes

### D. Browser-Harness Guard

If a browser harness is available, load the assembled page outside FileMaker and click an action button.

Confirm:

- the renderer remains usable
- the button note reports `noFileMaker`
- no JavaScript exception is required for this expected condition

Do not use browser-harness captures as article screenshots. All article screenshots must come from the native `.fmp12` demo.

### E. Invalid JSON Test

Run `WV__Demo_Handle_Action` manually with a non-JSON script parameter such as:

```text
not json
```

Confirm:

- status says `Rejected action: invalid JSON envelope.`
- the handled count does not increment
- the script returns `{"ok":false,"error":"invalid_json"}` after formatting

### F. Invalid Shape Test

Run the handler manually with:

```json
{
  "type": "demo.inspect_context",
  "payload": "not an object",
  "__wv_action": {}
}
```

Confirm the handler returns `invalid_envelope` and does not increment the count.

### G. Unknown Action Test

Run the handler manually with:

```json
{
  "__wv_action": {
    "version": 1,
    "source": "manual_test"
  },
  "type": "demo.uninvited_architecture",
  "payload": {}
}
```

Confirm the handler returns `unknown_action`, displays the rejected type, and does not increment the count.

## Native Screenshot Capture List

Capture these only after the smoke tests pass:

1. `WV Framework - Demo` with loaded context card and both action buttons visible in `wv_main`.
2. `WV Framework - Demo` after `Inspect Context`, with FileMaker action fields and JSON visible outside the viewer.
3. `WV Framework - Demo` after `Mark Movie`, with acknowledgement values visible inside the viewer.
4. Script Workspace showing the complete `WV__Demo_Handle_Action` script.
5. `WV Framework - Modules` showing records `20`, `21`, `22`, `23`, `24`, `25`, `62`, and `63`.
6. Module `25` showing `WV.sendAction` and `FileMaker.PerformScript`.
7. Module `63` showing the renderer button handlers.

Use the native FileMaker file for every screenshot. A browser mockup is useful for visual testing; it is not evidence of a native FileMaker demo artifact.

## Completed Export And Article Reconciliation

The completed native source set is stored in:

`filemaker-web-viewer-series/article two/`

It contains:

- `Flicks_WebViewer_Framework_02_TwoWay_fmp12.xml`
- `Summary.xml`
- `LIBRARY_CODE.tab`

Reconciliation completed on 19 Jul 2026:

1. `WV__Demo_Handle_Action` now matches the exact 44-step DDR script; the provisional `Refresh Window` steps and separate validation variables were removed.
2. `wv.platform.actions.js` matches module `25` in `LIBRARY_CODE.tab`.
3. The renderer excerpt matches the action rows and buttons in exported module `63`.
4. The article payload examples use the successful native `demo.mark_movie` run at `2026-07-20T02:44:24.933Z`.
5. The DDR reports 14 scripts and no custom functions.
6. The module export contains eight records, with executable order `LIB[25]` before `LIB[63]` in root module `62`.
7. The obsolete editorial source warning has been removed from the article.

The native file remains the source; the article explains the file. This arrangement saves us from correcting working software until it agrees with an older paragraph.
