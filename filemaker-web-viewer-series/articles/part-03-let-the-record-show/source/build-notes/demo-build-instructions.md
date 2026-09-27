# Ranked Views Demo Build Instructions

Target article:

`Beyond the Web Viewer Blob: Let the Record Show`

Subtitle:

`Native FileMaker Records In, Ranked Views Out`

Completed cumulative source:

`/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_02_TwoWay.fmp12`

Completed target:

`/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_03_RankedViews.fmp12`

Read-only production reference:

`/Users/loncook/Documents/Databases:Invoices/Flicks clone.fmp12`

Pre-edit backups created during the native build:

- `/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_03_RankedViews.prestrip-2026-08-01.fmp12`
- `/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_03_RankedViews.pre-native-navigation-2026-08-01.fmp12`

## Source Status On 2 Aug 2026

The target is built and has passed the native ranked-selection round trip.

Fresh source exports used for the build:

| Source | DDR | `LIBRARY_CODE` export |
| --- | --- | --- |
| completed two-way demo | 1 Aug 2026, 19:17 PDT | 1 Aug 2026, 19:18 PDT |
| read-only production reference | 1 Aug 2026, 19:19 PDT | 1 Aug 2026, 19:22 PDT |
| completed ranked target | 2 Aug 2026, 00:18 PDT | 1 Aug 2026, 23:21 PDT |

Export folders:

- `filemaker-web-viewer-series/article three/source/2026-08-01-two-way/`
- `filemaker-web-viewer-series/article three/source/2026-08-01-production/`
- `filemaker-web-viewer-series/article three/source/2026-08-01-final-target/`

The final target DDR reports:

- 8 base tables
- 11 table occurrences
- 5 relationships
- 14 scripts
- 4 layouts
- 8 value lists
- 0 custom functions

Those counts match the two-way source. This pass does not add schema, layouts, relationships, scripts, value lists, or custom functions. It changes the context and behavior of retained objects, changes `WV Framework - Demo` to a `MOVIE` layout context, and adds two `LIBRARY_CODE` records.

The final library export contains ten records. The exported code for modules `41` and `42` matches the checked-in source files after normalizing FileMaker vertical-tab line endings.

The code and steps below are reconciled to the final target exports. They are not provisional placeholders.

## What The Production Reference Contributed

The production file remained read-only.

Its DDR established the source-backed ranked-list vocabulary:

- native layout `UI__Ranked_List`
- `RANKED_UI::focusMovieID`
- `MOVIE_GLOBAL_RATING::global_rating`
- `MOVIE_GLOBAL_RATING::global_rank_order`
- native row-selection script `UI__Ranked_FocusRow_Set`
- `MOVIE`, `MOVIE_GLOBAL_RATING`, `MOVIE_GENRE`, and `GENRE` source tables

The production library did not contain the teaching ranked-list page and renderer used here. Production indexes `41` and `42` belong to dashboard modules, not this ranked surface. The demo therefore creates purpose-built teaching modules at `41` and `42`; it does not relabel production module code or reconstruct it from screenshots.

Do not copy these production subsystems into the target:

- `RANKED_UI`
- `UI_SELECTEDGENRE`
- production ranked layout objects and portal calculations
- production navigation scripts
- production dashboard modules
- production mutation, rating, or cache behavior

The production reference supplied evidence. It did not receive edits and did not become the target by degrees.

## Scope Contract

This pass adds or changes only:

- the `WV Framework - Demo` layout context and native record witness
- the existing `WV__Demo_Build_Context` script
- the existing `WV__Demo_Handle_Action` script
- the existing `WV__Demo_Run_All` convenience script
- module `41`, `wv.page.ranked.list.html`
- module `42`, `wv.renderer.ranked.list.js`
- visible ranked JSON, native current-record, and action diagnostics

Do not add:

- new tables or relationships
- full production ranked-list chrome
- a native FileMaker list reserved for the next pass
- broad production record mutation
- JavaScript queries against FileMaker data
- browser-owned authoritative selection
- a general-purpose action router
- a second action bridge
- the full AI prompt/review/test workflow
- the final production dirty-token, cache-version, loaded-map, retry, and deployment pattern

The visible explicit path remains:

```text
Build Context
  -> Load Web Viewer
  -> Push Context
```

The ranked interaction adds:

```text
Click ranked Web Viewer row
  -> WV.sendAction
  -> WV__Demo_Handle_Action
  -> validate stable id against current ranked_view.rows
  -> navigate native MOVIE found set
  -> rebuild context
  -> reload viewer after native navigation
  -> push acknowledgement context
```

`Run` may use the retained `ensure loaded` helper after the explicit path works.

## Expected Final Inventory

### Native records retained from the cumulative demo

| Base table | Final records | Use in this pass |
| --- | ---: | --- |
| `MOVIE` | 100 | stable id, display title/year, native found set and current record |
| `MOVIE_GLOBAL_RATING` | 100 | rating and `global_rank_order` |
| `MOVIE_GENRE` | 302 | genre membership |
| `GENRE` | 10 | filter id and display label |
| `FOCUS` | 66 | retained global demo and action fields |
| `LIBRARY_CODE` | 10 | eight inherited modules plus ranked page/renderer |

No sample records need to be copied from `Flicks clone.fmp12`; the completed two-way demo already contains the retained sample data.

### Final module inventory

| Index | Name | Status |
| ---: | --- | --- |
| 20 | `wv.platform.base.html` | inherited |
| 21 | `wv.platform.base.css` | inherited |
| 22 | `wv.platform.runtime.js` | inherited |
| 23 | `wv.platform.context.js` | inherited |
| 24 | `wv.platform.boot.js` | inherited |
| 25 | `wv.platform.actions.js` | inherited |
| 41 | `wv.page.ranked.list.html` | new |
| 42 | `wv.renderer.ranked.list.js` | new |
| 62 | `wv.page.framework.context.html` | inherited |
| 63 | `wv.renderer.framework.context.js` | inherited |

Verified executable dependency closure:

```text
41 -> 20, 25, 42
20 -> 21, 22, 23, 24
```

### Retained global fields

No new fields are required. Confirm these existing global fields remain available in `FOCUS`:

| Field | Type | Storage | Use |
| --- | --- | --- | --- |
| `g_wv_demo_title` | Text | global | inherited visible title; no longer required by ranked rows |
| `g_wv_demo_movie_id` | Text | global | FileMaker-owned selected movie id |
| `g_wv_demo_genre_id` | Text | global | active genre filter id |
| `g_wv_context_json` | Text | global | formatted ranked-view context |
| `g_wv_status` | Text | global | build/load/push/ensure status |
| `g_wv_module_index` | Number | global | page index, set to `41` |
| `g_wv_action_json` | Text | global | last valid or rejected action envelope |
| `g_wv_action_type` | Text | global | last action type |
| `g_wv_action_count` | Number | global | handled-action count |
| `g_wv_action_status` | Text | global | handler validation or navigation status |

## Build Sequence

Follow the dependency order. The renderer cannot validate fields that do not exist, and FileMaker cannot acknowledge a row the page never loaded.

### 1. Close, Clone, And Back Up

1. Close `Flicks_WebViewer_Framework_02_TwoWay.fmp12` in FileMaker Pro.
2. Confirm the target and backup paths before copying.
3. Duplicate the completed two-way source to the ranked target.
4. Duplicate the untouched target to the pre-edit backup.
5. Open only `Flicks_WebViewer_Framework_03_RankedViews.fmp12` for editing.
6. Keep `Flicks clone.fmp12` closed except during read-only inspection and export.

Example safe shell sequence:

```zsh
source_file='/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_02_TwoWay.fmp12'
target_file='/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_03_RankedViews.fmp12'
backup_file='/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_03_RankedViews.prestrip-2026-08-01.fmp12'

test ! -e "$target_file" && test ! -e "$backup_file" &&
cp -p "$source_file" "$target_file" &&
cp -p "$target_file" "$backup_file"
```

If either destination exists, stop. A cumulative demo is not improved by accidentally replacing the previous cumulative demo.

### 2. Export The Two Sources Before Naming Anything New

From the completed two-way demo, export:

- XML DDR
- `Summary.xml`
- all retained `LIBRARY_CODE` records as tab-delimited data

From the read-only production reference, export:

- XML DDR
- `Summary.xml`
- relevant `LIBRARY_CODE` records

Confirm from those exports:

- inherited fields and script names
- module indexes `20–25` and `62–63`
- production ranked layout and focus behavior
- source table and field names
- production indexes `41/42` are not the teaching ranked modules

Do not name a teaching module `wv.renderer.viz.multi.js` because production index `42` happened to have that name. Index evidence and purpose evidence are both required; numbers alone are not a dependency contract.

### 3. Update The Demo Layout Context

Open `WV Framework - Demo` in Layout mode.

Set **Show records from** to:

`MOVIE`

Retain:

- layout name `WV Framework - Demo`
- Web Viewer object name `wv_main`
- context JSON field
- action JSON field
- genre selector
- status and action diagnostic fields
- `Build Context`, `Load Web Viewer`, `Push Context`, and `Run` buttons

Add a compact native current-record witness:

| Visible value | Source |
| --- | --- |
| current movie title/year | `MOVIE::title_year_display` |
| current stable movie id | `MOVIE::ID` |

Keep the native record toolbar visible in Browse mode. The final interaction must expose FileMaker's current record and found count; a global selected id is not sufficient evidence of native navigation.

Place the objects so the layout remains a thin teaching surface:

- `wv_main` on the left
- context and action JSON in the center
- native title/id, genre, status, action diagnostics, and buttons on the right

Do not add a portal, navigation drawer, dashboard shell, or production menu.

Confirm `wv_main` still allows JavaScript to perform FileMaker scripts.

### 4. Create Module 41

On `WV Framework - Modules`, create one `LIBRARY_CODE` record.

Set:

- index: `41`
- name: `wv.page.ranked.list.html`
- enabled: `1`
- payload MIME: match the existing HTML page modules
- payload name: `wv.page.ranked.list.html`
- payload public: off, matching the retained inline modules

Paste the complete source from:

`filemaker-web-viewer-series/article three/source/wv.page.ranked.list.html`

The source-backed page is:

```html
<!-- ============================================================
   W V   R A N K E D   L I S T   P A G E
   Index: 41
   Name:  wv.page.ranked.list.html

   Purpose:
     - Assemble the ranked-list teaching surface
     - Keep the initial loading state visible before FileMaker pushes context

   Dependencies:
     - LIB[20] wv.platform.base.html
     - LIB[21] wv.platform.base.css
     - LIB[22] wv.platform.runtime.js
     - LIB[23] wv.platform.context.js
     - LIB[24] wv.platform.boot.js
     - LIB[25] wv.platform.actions.js
     - LIB[42] wv.renderer.ranked.list.js

   Exports:
     - Page markup for the ranked-list renderer

   Public API:
     - None

   Notes:
     - FileMaker supplies the ordered records and authoritative selection.
     - JavaScript renders rows and reports selection intent through WV.sendAction.

   History:
     - 01 Aug 2026 — Lon Cook — lon@portagebay.com : created
   ============================================================ -->

‡‡LIB[20]‡‡

<!-- PAGE_HEAD -->
<title>Ranked Movies</title>

<!-- PAGE_BODY -->
<section class="wv-ranked-page" data-wv-page="ranked-list">
  <div class="wv-ranked-loading" role="status">Loading ranked records…</div>
</section>

<!-- PAGE_SCRIPTS -->
<script>
  ‡‡LIB[25]‡‡
  ‡‡LIB[42]‡‡
</script>
```

### 5. Create Module 42

Create another `LIBRARY_CODE` record.

Set:

- index: `42`
- name: `wv.renderer.ranked.list.js`
- enabled: `1`
- payload MIME: `application/javascript`
- payload name: `wv.renderer.ranked.list.js`
- payload public: off

Paste the complete source from:

`filemaker-web-viewer-series/article three/source/wv.renderer.ranked.list.js`

Do not retype the renderer from an article screenshot. The source file and final library export are the authorities.

The required renderer behaviors are:

1. use the initial page markup as the loading state
2. read only `ctx.ranked_view`, `ctx.actions`, and their documented children
3. render the supplied array with `rows.forEach`
4. use `record.selected === true` for selected styling and `aria-pressed`
5. render `ranked.empty_message` when the array is empty
6. send only `ranked.select_movie` with `payload.movie_id`
7. call `WV.sendAction`, not `FileMaker.PerformScript`
8. show the native found-set position from returned context

The source-backed action insert is:

```js
row.addEventListener("click", function () {
  var result = typeof WV.sendAction === "function"
    ? WV.sendAction("ranked.select_movie", { movie_id: movieId }, {
        source: "wv.renderer.ranked.list"
      })
    : "noBridge";

  actionNote.textContent =
    "Selection request: " + result +
    ". Waiting for FileMaker acknowledgement.";
});
```

The renderer header must keep both history entries newest-first:

```text
History:
  - 01 Aug 2026 — Lon Cook — lon@portagebay.com : expose the acknowledged native found-set position with the ranked view.
  - 01 Aug 2026 — Lon Cook — lon@portagebay.com : created
```

### 6. Extend `WV__Demo_Build_Context`

Modify the inherited script; do not create a numbered replacement.

The complete paste-ready FMXML is:

`filemaker-web-viewer-series/article three/fmxmlsnippets/WV__Demo_Build_Context_Ranked.fmxmlsnippet.xml`

Final header, preserved verbatim:

```text
# Purpose: Build the ranked-view context from native FileMaker records and show the reader the payload.
# In: FOCUS::g_wv_demo_movie_id, FOCUS::g_wv_demo_genre_id
# Out: FOCUS::g_wv_module_index, FOCUS::g_wv_context_json, FOCUS::g_wv_status; exits with raw context JSON.
# Anchor: MOVIE on WV Framework - Demo. Native rows come from MOVIE, MOVIE_GLOBAL_RATING, MOVIE_GENRE, and GENRE.
# Calls: None. FileMaker establishes the ranked found set, shapes the rendering contract, and exposes its current native record.
# Modified: 01 Aug 2026, 21hr22PT — Lon Cook — lon@portagebay.com : establish the ranked native found set and bind selection to the current MOVIE record.
# Modified: 01 Aug 2026, 19hr34PT — Lon Cook — lon@portagebay.com : shape native ranked-view records and FileMaker-owned selected state.
# Modified: 19 Jul 2026, 20hr24PT — Lon Cook - lon@portagebay.com : added FileMaker-owned action acknowledgement state.
```

The script has 59 steps in the final DDR.

Implement it in these dependency blocks:

#### 6A. Resolve filter and select native facts

Set module index `41` and read:

- `FOCUS::g_wv_demo_movie_id`
- `FOCUS::g_wv_demo_genre_id`

Resolve the genre label with:

```filemaker
ExecuteSQL (
  "SELECT \"name\" FROM \"GENRE\" WHERE \"ID\" = ?" ;
  "" ; "" ; $_genre_id
)
```

Select these fields in this order:

```text
MOVIE::ID
MOVIE::title_year_display
MOVIE::year
MOVIE_GLOBAL_RATING::global_rating
MOVIE_GLOBAL_RATING::global_rank_order
```

Join `MOVIE_GLOBAL_RATING` on `id_movie`. When a genre is active, join `MOVIE_GENRE` and constrain `id_genre`. Order by `global_rank_order`, then `title_year_display`.

Use `Char ( 29 )` as the field separator and `Char ( 30 )` as the row separator.

#### 6B. Fail visibly on query error

If `$_rows_text` begins with `?`, build a zero-row contract with:

- page `41`
- source `ranked_views_demo`
- contract version `1`
- current filter id and label
- empty selected id
- `count: 0`
- `rows: []`
- explicit query error and status

Exit before attempting a find.

#### 6C. Establish the native found set

Convert the first field of every SQL row into `$_ranked_ids`.

Go to:

`WV Framework - Demo` (`MOVIE`)

Enter Find mode and create one request per ranked id:

```text
Set Field [ MOVIE::ID; "==" & GetValue ( $_ranked_ids ; $_request_index ) ]
New Record/Request
```

If no ranked ids exist, search for the impossible sentinel:

```text
==__wv_no_ranked_match__
```

Perform the find. Do not replace this with a global id field; the native found set is part of the demo contract.

#### 6D. Build ordered row JSON

For each SQL row, set:

```filemaker
json = JSONSetElement ( json
  ; [ "[" & i & "].movie_id" ; movie_id ; JSONString ]
  ; [ "[" & i & "].display_title" ; Case ( IsEmpty ( display_title ) ; movie_id ; display_title ) ; JSONString ]
  ; [ "[" & i & "].year" ; year ; JSONNumber ]
  ; [ "[" & i & "].rating" ; rating ; JSONNumber ]
  ; [ "[" & i & "].rank" ; rank ; JSONNumber ]
  ; [ "[" & i & "].order" ; i + 1 ; JSONNumber ]
)
```

Use `global_rank_order` when it is greater than zero; otherwise fall back to `i + 1`.

#### 6E. Reconcile FileMaker-owned selection

Confirm `FOCUS::g_wv_demo_movie_id` exists in `$_rows_json`.

Selection fallback order:

1. empty when native found count is zero
2. retained selected id when it exists in the current array
3. current `MOVIE::ID`

Navigate the native found set to the selected id, then set:

`FOCUS::g_wv_demo_movie_id`

Add `selected` to every row by comparing its `movie_id` with the reconciled FileMaker id.

#### 6F. Build final context

Set these exact keys and types:

| Path | Type |
| --- | --- |
| `__wv.page` | JSONNumber |
| `__wv.page_name` | JSONString |
| `__wv.source` | JSONString |
| `__wv.contract_version` | JSONNumber |
| `__wv.ts` | JSONString |
| `ranked_view.filter.genre_id` | JSONString |
| `ranked_view.filter.label` | JSONString |
| `ranked_view.selected_movie_id` | JSONString |
| `ranked_view.count` | JSONNumber |
| `ranked_view.native_found_count` | JSONNumber |
| `ranked_view.current_record_number` | JSONNumber |
| `ranked_view.current_record_id` | JSONString |
| `ranked_view.empty_message` | JSONString |
| `ranked_view.rows` | JSONArray |
| `actions.count` | JSONNumber |
| `actions.last_type` | JSONString |
| `actions.status` | JSONString |

Write formatted JSON to `FOCUS::g_wv_context_json`, write the build summary to `FOCUS::g_wv_status`, and exit with raw JSON.

### 7. Extend `WV__Demo_Handle_Action`

Modify the inherited handler. Preserve all inherited modification entries verbatim and add each new entry above the earlier list.

The complete paste-ready FMXML is:

`filemaker-web-viewer-series/article three/fmxmlsnippets/WV__Demo_Handle_Action_Ranked.fmxmlsnippet.xml`

Final header:

```text
# Purpose: Receive an action envelope from the Web Viewer and make it visible in FileMaker.
# In: Get ( ScriptParameter ) as raw JSON.
# Out: JSON status object.
# Anchor: MOVIE on WV Framework - Demo. Demo teaching glue; does not update production records.
# Calls: WV__Demo_Build_Context, WV__Demo_Load_Viewer, WV__Demo_Push_Context.
# Modified: 01 Aug 2026, 22hr42PT — Lon Cook — lon@portagebay.com : reload the ranked module after native record navigation before pushing acknowledgement context.
# Modified: 01 Aug 2026, 21hr22PT — Lon Cook — lon@portagebay.com : navigate the ranked native found set to the requested MOVIE record before acknowledgement.
# Modified: 01 Aug 2026, 19hr34PT — Lon Cook — lon@portagebay.com : validate ranked stable-id intent and acknowledge FileMaker-owned selection.
# Modified: 19 Jul 2026, 20hr24PT — Lon Cook - lon@portagebay.com : created
```

The final handler has 71 steps.

Keep the inherited invalid-JSON, invalid-envelope, and unknown-action branches. Extend the known-action calculation only with:

```filemaker
$_type = "ranked.select_movie"
```

For the ranked action, read:

- `__wv_action.page`
- `__wv_action.source`
- `payload.movie_id`

Reject the request unless:

- page is `41`
- source is `wv.renderer.ranked.list`
- `payload.movie_id` is a non-empty JSON string
- current `FOCUS::g_wv_context_json` contains a ranked rows array
- one current row has the requested id

Rejected status:

```text
Rejected ranked selection: the movie id is not valid in the current FileMaker context.
```

Rejected result:

```filemaker
JSONSetElement ( "{}"
  ; [ "ok" ; 0 ; JSONBoolean ]
  ; [ "error" ; "invalid_ranked_selection" ; JSONString ]
  ; [ "movie_id" ; $_payload_movie_id ; JSONString ]
)
```

For a valid ranked selection:

1. go to `WV Framework - Demo` on `MOVIE`
2. go to the first native record
3. walk the current found set until `MOVIE::ID = $_payload_movie_id`
4. write current `MOVIE::ID` to `FOCUS::g_wv_demo_movie_id`
5. increment the inherited action count
6. write action JSON, type, count, and native selection status
7. rebuild ranked context
8. pause `.5` second
9. reload `WV__Demo_Load_Viewer`
10. pause `1` second
11. push acknowledgement context

The reload after native navigation is required by the completed target. Native record navigation can reinitialize the Web Viewer; pushing immediately produced a race in the first native test. Do not remove the reload and pauses merely because the happy path sometimes wins.

This is still teaching glue. It does not edit `MOVIE`, `GENRE`, `MOVIE_GLOBAL_RATING`, or `MOVIE_GENRE` records.

### 8. Update `WV__Demo_Run_All`

Replace the inherited direct three-script wrapper with the source-backed push-first convenience path after the explicit load and push buttons work.

Paste-ready FMXML:

`filemaker-web-viewer-series/article three/fmxmlsnippets/WV__Demo_Run_All.fmxmlsnippet.xml`

The final script has 16 steps and retains this header history:

```text
# WV__Demo_Run_All
# Purpose: Build ranked-view context, then let the retained loader push first and reload only when required.
# In: FOCUS::g_wv_demo_genre_id and FOCUS::g_wv_demo_movie_id.
# Out: FOCUS::g_wv_context_json, FOCUS::g_wv_status; exits with the ensure-loaded result.
# Anchor: FOCUS. Explicit Load Viewer and Push Context buttons remain available for layer-by-layer debugging.
# Calls: WV__Demo_Build_Context; . webviewer . ensure loaded ( index ; -object_name ; -context_json ; -movie_id ; -genre_id ; ... ) :
# Modified: 01 Aug 2026, 20hr18PT — Lon Cook — lon@portagebay.com : route the cumulative ranked-view run through the retained push-first loader.
# Modified: 06 Jul 2026, Codex - created Article 1 demo teaching wrapper.
```

After `WV__Demo_Build_Context`, call the retained ensure-loaded script with:

```filemaker
JSONSetElement ( "{}"
  ; [ "index" ; 41 ; JSONNumber ]
  ; [ "object_name" ; "wv_main" ; JSONString ]
  ; [ "context_json" ; $_context_json ; JSONString ]
  ; [ "force_reload" ; 0 ; JSONNumber ]
)
```

Write a visible status using:

```filemaker
"Run all: " & JSONGetElement ( $_ensure_result ; "status" ) &
  " — " & JSONGetElement ( $_ensure_result ; "message" ) &
  " — did_reload=" & JSONGetElement ( $_ensure_result ; "did_reload" )
```

Do not remove the explicit `Load Web Viewer` and `Push Context` buttons. `Run` is a convenience path, not a replacement for layer-by-layer diagnosis.

### 9. Commit, Rebuild, Load, And Push

After editing modules `41` and `42`:

1. Commit the current `LIBRARY_CODE` record.
2. Click `Rebuild Library` on `WV Framework - Modules`.
3. Confirm the rebuild result reports success.
4. Confirm `$$wv_loaded_map` is cleared by the inherited rebuild script.
5. Return to `WV Framework - Demo`.
6. Click `Build Context`.
7. Click `Load Web Viewer`.
8. Observe `Loading ranked records…`.
9. Click `Push Context`.
10. Confirm repeated rows replace the loading state.

Do not begin with `Run`. The explicit path proves the page, renderer, cache, and context boundaries before `ensure loaded` is allowed to decide anything.

## Verification Sequence

### A. Native Ranked Context

Choose `Sci-Fi` and click `Build Context`.

Confirm:

- native found count is `33`
- `FOCUS::g_wv_module_index` is `41`
- `__wv.page` is `41`
- `__wv.page_name` is `ranked_list`
- `__wv.source` is `ranked_views_demo`
- `__wv.contract_version` is `1`
- `ranked_view.filter.label` is `Sci-Fi`
- `ranked_view.count` is `33`
- `ranked_view.native_found_count` is `33`
- `ranked_view.current_record_id` equals visible `MOVIE::ID`
- every row has the seven required row keys
- exactly one row is selected when the selected id is valid

### B. Loading State

Click `Load Web Viewer` without pushing context.

Confirm:

- page `41` loads in `wv_main`
- `Loading ranked records…` is visible
- the viewer debug HUD reports a registered renderer
- no ranked row is invented before context arrives

### C. Populated And Selected State

Click `Push Context`.

Confirm:

- 33 supplied rows render
- the visible rank and rating match the context values
- the genre and movie count match the context
- the viewer summary includes the native current-record position
- only the FileMaker-marked row has `is-selected`

### D. Native Row-Selection Round Trip

Click Web Viewer row `#4`, `AX: Amber Void (2018)`.

Confirm the action envelope contains:

```text
type = ranked.select_movie
__wv_action.page = 41
__wv_action.source = wv.renderer.ranked.list
payload.movie_id = MOVIE-51D0E623-D55B-4D32-9191-B20C58243640
```

Confirm FileMaker then shows:

- `MOVIE::title_year_display = AX: Amber Void (2018)`
- `MOVIE::ID = MOVIE-51D0E623-D55B-4D32-9191-B20C58243640`
- native record `17 of 33`
- `FOCUS::g_wv_action_type = ranked.select_movie`
- incremented action count
- status ending in `record 17 of 33`
- rebuilt context with the same `current_record_id`
- row `#4` returned with `selected: true`
- viewer summary `native record 17 of 33`

The rank `4` and native position `17` should both remain visible. Their disagreement is useful evidence that the stable id, not a row number, joins the two surfaces.

### E. Invalid Ranked Id

Run `WV__Demo_Handle_Action` manually with:

```json
{
  "__wv_action": {
    "version": 1,
    "source": "wv.renderer.ranked.list",
    "page": 41
  },
  "type": "ranked.select_movie",
  "payload": {
    "movie_id": "MOVIE-NOT-IN-CURRENT-CONTEXT"
  }
}
```

Confirm:

- the handler returns `invalid_ranked_selection`
- action count does not increment
- native current record does not change
- status says the id is not valid in current FileMaker context

### F. Wrong Page Or Source

Repeat the valid action with either:

- page other than `41`
- source other than `wv.renderer.ranked.list`

Confirm the handler rejects the request before native navigation.

### G. Empty State

Push a manual test contract containing:

```json
{
  "ranked_view": {
    "count": 0,
    "filter": {
      "genre_id": "GENRE-DEMO-NO-MATCHES",
      "label": "No Matches"
    },
    "rows": [],
    "selected_movie_id": "",
    "empty_message": "No ranked movies match No Matches."
  },
  "actions": {
    "status": "Manual empty-state fixture"
  }
}
```

Confirm the dashed empty panel appears and no row remains selected. Restore a builder-generated context immediately afterward.

This fixture tests renderer state. It is not a claim that a production genre has no ranked movies.

### H. Smarter Run Path

With the ranked page already loaded, click `Run`.

Confirm:

- builder runs first
- ensure-loaded result is valid JSON
- status exposes `status`, `message`, and `did_reload`
- unchanged context may take the push/skip path without unconditional reload
- explicit buttons still work afterward

### I. Regression Actions

The inherited handler still accepts:

- `demo.inspect_context`
- `demo.mark_movie`

Confirm their envelope validation and action-count behavior remain intact. They do not navigate or mutate native movie records.

## Native Screenshot Capture List

The completed native screenshots are stored in:

`filemaker-web-viewer-series/article three/screenshots/`

| File | Evidence |
| --- | --- |
| `01-ranked-loading-native.png` | module `41` loaded before context push |
| `02-ranked-empty-native.png` | deliberate manual empty fixture |
| `03-ranked-selected-native.png` | selected row plus native current-record evidence |
| `04-ranked-final-native.png` | completed ranked interface and diagnostics |
| `05-builder-native.png` | native found-set and context builder steps |
| `06-handler-native.png` | ranked action navigation and acknowledgement path |
| `07-module-inventory-native.png` | cumulative ten-module inventory and renderer record |

All captures come from the native target `.fmp12` file. A browser harness may support renderer development, but it is not final FileMaker evidence.

## Final Export And Reconciliation

After the native verification sequence:

1. Save and close Script Workspace.
2. Export a fresh XML DDR from the target only.
3. Export `Summary.xml`.
4. Export all ten `LIBRARY_CODE` records.
5. Reconcile script counts and headers.
6. Reconcile module names, indexes, dependencies, payload metadata, and code.
7. Reconcile article payload keys and example values.
8. Reconcile screenshots to the native target.

Completed reconciliation:

- `WV__Demo_Build_Context` is 59 steps.
- `WV__Demo_Handle_Action` is 71 steps.
- `WV__Demo_Run_All` is 16 steps.
- handler `Calls` includes Build, Load, and Push.
- handler history contains the 22hr42, 21hr22, 19hr34, and original 19 Jul entries in newest-first order.
- builder history preserves all inherited entries.
- final `WV Framework - Demo` layout is based on `MOVIE` and contains object `wv_main`.
- final module inventory is `20–25`, `41–42`, and `62–63`.
- exported module `41` matches `wv.page.ranked.list.html`.
- exported module `42` matches `wv.renderer.ranked.list.js`.
- final context contains stable ids, explicit rank/order, display-ready values, native found-set evidence, and FileMaker-owned selected state.
- the successful selected run navigates to native record `17 of 33` and acknowledges row `#4` by stable id.

The target is now source-backed by:

- `filemaker-web-viewer-series/article three/source/2026-08-01-final-target/Flicks_WebViewer_Framework_03_RankedViews_fmp12.xml`
- `filemaker-web-viewer-series/article three/source/2026-08-01-final-target/Summary.xml`
- `filemaker-web-viewer-series/article three/source/2026-08-01-final-target/LIBRARY_CODE.tab`

The native file remains the source of truth. The instructions explain how it was built; they do not get to overrule it because a paragraph was easier to edit.
