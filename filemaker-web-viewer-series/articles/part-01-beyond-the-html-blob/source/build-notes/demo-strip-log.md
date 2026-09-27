# Article 1 Demo Strip Log

## Files

Source:

`/Users/loncook/Documents/Databases:Invoices/Flicks clone.fmp12`

Working demo:

`/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_01_Context.fmp12`

Pre-strip backup:

`/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_01_Context.prestrip-2026-07-06.fmp12`

Spec:

`/Users/loncook/Documents/Codex/Bayesian Gliko/docs/web_viewer_article_01_demo_spec.md`

Current article contract:

`/Users/loncook/Documents/Codex/Blog Posts/filemaker-web-viewer-series/article-contracts.md`

## Current State From Fresh DDR

Fresh DDR/export uploaded 2026-07-07:

- `filemaker-web-viewer-series/article one/Flicks_WebViewer_Framework_01_Context_fmp12.xml`
- `filemaker-web-viewer-series/article one/LIBRARY.tab`
- `filemaker-web-viewer-series/article one/Summary.xml`

`Summary.xml` reports:

- `8` base tables
- `11` table occurrences
- `4` layouts
- `13` scripts
- `8` value lists
- `0` custom functions

Current Article 1 demo path is explicit:

- `WV__Demo_Build_Context`
- `WV__Demo_Load_Viewer`
- `WV__Demo_Push_Context`

`WV__Demo_Run_All` is teaching glue that runs those three scripts in order. `WV__Demo_Rebuild_Library` is a module-layout utility button, not part of the main demo layout flow.

Retained `. webviewer . ensure loaded ...` scripts are framework carry-forward code only; they are not part of the Article 1 visible walkthrough.

## Completed Outside FileMaker

- Created the working demo copy from `Flicks clone.fmp12`.
- Created a pre-strip backup of the working demo file.
- Updated the Article 1 demo spec so the source is `Flicks clone.fmp12`, not the older `Flicks.fmp12`.
- Re-cloned the working demo on 2026-07-06 after layout deletion did not complete correctly. The failed stripped copy was preserved as `Flicks_WebViewer_Framework_01_Context.broken-layout-delete-2026-07-06T20-06-26-0700.fmp12`, and `Flicks_WebViewer_Framework_01_Context.fmp12` was restored from `Flicks clone.fmp12`.

## Tooling Boundary

The `.fmp12` file is a FileMaker binary. From the shell, we can safely clone and back it up; we cannot safely delete schema, layouts, script steps, relationships, or records inside the file without FileMaker Pro. FileMaker Pro 22 is installed and AppleScript can open files/run scripts, but the AppleScript dictionary does not provide a clean schema-editing API for this strip-down work.

So: binary edits happen in FileMaker Pro. The terminal gets to be useful; it does not get to pretend it is FileMaker.

## FileMaker Strip Sequence

Work only in:

`Flicks_WebViewer_Framework_01_Context.fmp12`

### 1. Open The Working Demo

- Confirm the window/file name is `Flicks_WebViewer_Framework_01_Context`.
- Do not open or edit `Flicks clone.fmp12`.
- Confirm the pre-strip backup exists before changing schema.

### 2. Update Visible Identity

Set visible solution/header text to:

- solution name: `Flicks Web Viewer Framework`
- release/version label: `Context Demo`

Update the `SOLUTION` record if present:

- `SOLUTION::name`
- `SOLUTION::release_notes`
- any retained visible version/release fields

### 3. Create Stable Framework Layout Names

Earlier notes said to use the ranked-list Web Viewer surface as the demonstrator. That has been superseded. Article 1 now uses a thin framework context demonstrator on `WV Framework - Demo`; the ranked-list view is reserved for later articles.

Current retained layouts:

- `WV Framework - Demo`
- `WV Framework - Modules`
- `WV Framework - Sample Data`
- `SOLUTION` (hidden utility layout)

Do not use article-numbered internal layout names; the next demo file should inherit these names without looking stale.

### 4. Strip Interface Chrome From Those Layouts

Remove from the three framework layouts:

- navigation menus
- side drawers and drawer handles
- popover launchers
- app-wide tab bars
- admin/debug controls unrelated to the Web Viewer framework
- production filter/sort/mode controls
- full-app breadcrumbs
- splash/startup panels
- dashboard cards unrelated to context delivery
- hidden buttons inherited from the full app unless retained scripts require them

### 5. Build The Framework Script Path

Current retained visible demo scripts:

- `WV__Demo_Build_Context`
- `WV__Demo_Load_Viewer`
- `WV__Demo_Push_Context`
- `WV__Demo_Run_All`
- `WV__Demo_Rebuild_Library`

Current retained framework scripts:

- `. webviewer . load ( index ; -object_name )`
- `. webviewer . push context ( -object_name ; -context_json )`
- `. webviewer . render ( index ) : text`
- `. webviewer . context . build ( -index ; -movie_id ; -genre_id ) : json`
- `. webviewer . ensure loaded . batch ( viewers_json ; -base_context_json ; -force_reload )`
- `. webviewer . ensure loaded ( index ; -object_name ; -context_json ; -movie_id ; -genre_id ; ... ) :`
- `library_json . ensure cache ( -force_rebuild ) : json`
- `library_json . build cache( version ) : json`

The article should point readers to the explicit `Build Context -> Load Viewer -> Push Context` flow first. Do not lead with `ensure loaded`; that is a later optimization pattern.

### 6. Rename And Prune Module Records

Fresh Article 1 DDR/import evidence lives in:

- `filemaker-web-viewer-series/article one/Flicks_WebViewer_Framework_01_Context_fmp12.xml`
- `filemaker-web-viewer-series/article one/LIBRARY.tab`

The fresh DDR reports `LIBRARY_CODE` has `7` records. Article 1 root is index `62`; its intended expansion-token closure remains:

- `62 -> 20, 63`
- `20 -> 21, 22, 23, 24`

Retained module records:

| Index | Rename to | Status |
| --- | --- | --- |
| `20` | `wv.base.shell.html` | Base shell. Current `name` is `wv.platform.base.html`; exported payload name is already `wv.base.shell.html`. |
| `21` | `wv.platform.base.css` | Required by shell `20`. |
| `22` | `wv.platform.runtime.js` | Required by shell `20`. |
| `23` | `wv.platform.context.js` | Required by shell `20`; exported payload name is currently `wv.platform.fmbridge.js`, so verify which visible name you want readers to see. |
| `24` | `wv.platform.boot.js` | Required by shell `20`. |
| `62` | `wv.page.framework.context.html` | Article 1 page root. Current `name` is `wv.page.viz.pairwise.html`; exported payload name is already `wv.page.framework.context.html`. |
| `63` | `wv.renderer.framework.context.js` | Article 1 renderer paired with page `62`; current exported names still say pairwise, so rename for the teaching file. |

The older records below were candidates for deletion during stripping and should not be treated as current Article 1 dependencies:

- `40`
- `41`
- `42`
- `60`
- `61`
- `64`
- `65`
- `66`
- `67`
- `68`

Leftover production script references to clear before deleting those records:

- `UI__Pair_Next` references index `64`.
- `viz . progress . wv refresh : json` defaults to index `64` and documents renderer `65`.
- `viz . dashboard . wv refresh : json` defaults to index `41`.
- `viz . rating dashboard . wv refresh : json` defaults to page `67`.
- `UI__Ranked_Filter_Apply`, `UI__Ranked_FocusRow_Set`, `WV__Rating_Dashboard_Action ( action_json )`, and `run script . script result` call page `67`.

Fresh DDR check after trimming extra scripts:

- `Summary.xml` reports `13` scripts.
- Retained script definitions are the five `WV__Demo_*` scripts, the Web Viewer load/render/push/context/ensure helpers, and the two library JSON cache helpers.
- Error/email/AppleScript script definitions are gone.
- Custom functions are gone; `Summary.xml` reports `0`.
- No stale old page-index default comment remains in the fresh DDR.

### 7. Align The Web Viewer Object

Use object name:

- `wv_main`

Make sure `WV__Demo_Load_Viewer`, `WV__Demo_Push_Context`, and `. webviewer . push context` target the same object name.

Set the demo module input/default to:

- `FOCUS::g_wv_module_index` = `62`

Fresh DDR evidence: `WV__Demo_Load_Viewer` defaults the module index to `62` and targets `wv_main`. Do not use dependency/helper module indexes such as `21` as the demo page index.

### 8. Retain Only Needed Value Lists

DDR value lists to keep for Article 1:

- `boolean`
  - Keep for retained yes/no fields such as module enabled flags.
- `library_code_languages`
  - Keep for `LIBRARY_CODE::language` on the module layout.
- `movie_all`
  - Keep if the demo movie picker stores `MOVIE::ID`.
  - Primary: `MOVIE::ID`; secondary: `movie.TITLE~display::title`.
- `movieYear_active`
  - Keep only if the demo picker stores `MOVIE::id_active` or you want the existing title/year display without building a new value list.
  - Primary: `MOVIE::id_active`; secondary: `MOVIE::title_year_display`.
- `genre_ids`
  - Keep only if the demo keeps a genre input that stores `GENRE::ID`.
  - Primary: `GENRE::ID`; secondary: `GENRE::name`.
- `genre_active`
  - Keep only if the demo keeps active-genre filtering and stores `GENRE::id_active`.
- `payload_mime`
  - Keep only if the module layout exposes payload/container fields.
- `rating`
  - Keep only if the sample-data layout exposes `MOVIE::rating`.

DDR value lists to strip for Article 1 unless FileMaker reports a dependency:

- `sort_options`
- `ranked_mode`
- `genre_names`
- `genre_byMovie`
- `admin_action`
- `snapshot_reason`
- `VirtualValueList01_1column`
- `VirtualValueList01_2column`
- `field_type`
- `entry_method`
- `asc_desc`
- `text_number`
- separator lists: `-`, `--`, `---`

For the demo movie selector, prefer `movie_all` if the field stores the stable `MOVIE::ID`. Use `movieYear_active` only if the existing scripts expect `id_active`. Stable IDs are the lesson; title/year is just the reader-friendly label, not the payload identity.

### 9. Strip Schema After Dependencies Are Clear

Fresh DDR retained base tables:

- `LIBRARY_CODE`
- `SOLUTION`
- `FOCUS`
- `MOVIE`
- `TITLE`
- `MOVIE_GLOBAL_RATING`
- `GENRE`
- `MOVIE_GENRE`

Strip production-only tables only after layouts, scripts, and table occurrences no longer depend on them.

### 10. Prune Records Only In Retained Tables

After schema is stable:

- keep approximately 8 to 15 `MOVIE` records
- keep one display `TITLE` per retained movie
- keep one `MOVIE_GLOBAL_RATING` per retained movie
- keep only framework module records in `LIBRARY_CODE`
- keep one `SOLUTION` record
- keep minimum `FOCUS` state needed by the scripts

Do not prune records from tables you removed. There is no prize for sweeping a room after demolishing it.

### 11. Custom Function Removal And Script Migration

Fresh DDR on 2026-07-07 at 11:07:38 confirms:

- `CustomFunctions count="0"`
- `<CustomFunctionCatalog/>`
- no external or internal `CustomFunctionRef` dependencies

The Article 1 demo now ships with no custom functions. The required migration work before deletion was:

- replace `#( name ; value )` and `ParamAssign` script parameters with native FileMaker JSON
- use `JSONSetElement` in caller scripts
- use `JSONGetElement`, `JSONGetElementType`, and `EvaluationError` guards in callee scripts
- keep required-parameter behavior by setting `$_invalid_params`, `$_error_message`, and `$_error`, then retaining `Exit Loop If [ $_error ]`
- avoid `?` leakage from `JSONGetElement` by checking `EvaluationError` before casting or comparing
- replace `IDCreate` / `FieldTableOccurrence` auto-enter calculations with native hardcoded ID prefixes plus `Get ( UUID )`
- replace `LIBRARY_CODE::index` SQL helper logic with the `LIBRARY_CODE__all` Cartesian relationship and `Max ( LIBRARY_CODE__all::index ) + 1`
- replace library cache desired-version lookup with `GetAsText ( Max ( LIBRARY_CODE__all::modified ) )`

For later article demo files, do not copy production scripts back in with their old custom-function dependencies intact. Any migrated script must be normalized to native JSON parameter passing and native FileMaker calculations first; otherwise we will slowly rebuild the custom-function junk drawer we just emptied. Which would be artisanal, perhaps, but still a junk drawer.

### 12. Verify

Run:

- `WV__Demo_Build_Context`
- `WV__Demo_Load_Viewer`
- `WV__Demo_Push_Context`

Or run:

- `WV__Demo_Run_All`

After editing module records, first run:

- `WV__Demo_Rebuild_Library`

Confirm:

- `wv_main` loads the framework context page
- `. webviewer . push context ( -object_name ; -context_json )` returns or displays `ok`
- the viewer changes from waiting state to rendered state
- `FOCUS::g_wv_context_json` shows `__wv.page = 62`
- no Article 2 callback/reducer behavior is present
- screenshots can be captured from the native `.fmp12`

## Current Status

Demo file is in working Article 1 shape per the 2026-07-07 fresh DDR. Remaining article work is drafting, screenshot capture, and final wording against the current contract.
