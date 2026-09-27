# Acceptance Results

Status: this document records the rejected first closure and its then-current acceptance state. The later rating-landscape and portal architecture supersede its List View implementation claims. Final architecture evidence is recorded in `12-redesign-test-evidence.md` and the 19 Aug 2026 DDR/XML reconciliation.

## Satisfied evidence

- Fresh pre-build DDR, Summary, and library exports captured from the completed Article 3 demo and read-only production reference on 12 Aug 2026.
- Minimal closure decision recorded from fresh source.
- Human brief, context manifest, initial prompt, untouched initial output, review, observed renderer failure, constrained revision prompt, and reviewed revision preserved authentically.
- Browser harness proves populated/empty rendering, stable-id selection intent, keyboard band intent, and corrected multi-bin pointer band intent.
- Reviewed renderer contains no direct `FileMaker.PerformScript`, production reducer, synthetic fallback rows, movers, or layered surfaces.
- Modules `43` and `44` were manually committed to the native Article 4 target on 15 Aug 2026.
- The immediate 12-record native library export matches both reviewed module files byte-for-byte after FileMaker field decoding:
  - `43` — `wv.page.hybrid.rating.html`, enabled, private, `text/html`, payload name matched, 1,056 bytes.
  - `44` — `wv.renderer.hybrid.rating.js`, enabled, private, `application/javascript`, payload name matched, 15,194 bytes.
- Native module-inventory screenshot and the dated reconciliation export are preserved under `article four/screenshots/` and `article four/source/2026-08-15-manual-module-gate/`.
- The native `WV__Demo_Rebuild_Library` wrapper was executed under Script Debugger on 15 Aug 2026. Immediately before exit, `JSONFormatElements ( $_result )` returned `cache_empty = false`, `cache_error = 0`, `commit_error = 0`, `loaded_map_cleared = true`, and `ok = true`.
- Module `43` was then passed only through the paused loader's local `$_index` variable. The existing `. webviewer . load ( index ; -object_name )` chain assembled it into `wv_main`; FileMaker displayed the framework debug HUD in the native Web Viewer. No field, script, layout, or privilege setting was changed for this test.
- Native rebuild and module-load evidence is preserved as screenshots `02-library-rebuild-native.png`, `03-module43-native-load.png`, and `04-module43-native-webviewer.png`.
- Native Manage Database inspection on 15 Aug 2026 verifies `FOCUS::g_wv_rating_lo` and `FOCUS::g_wv_rating_hi` as Number fields with global storage. Evidence is preserved as `05-rating-band-fields-native.png`.
- The native `WV Framework - Hybrid` layout is saved as a 1,300-point-wide List View in `MOVIE` context with Top Navigation, Body, and Footer parts.
- One verified `LayoutObjectList` FMXML snippet supplied the 34-object layout set. Its saved bindings include:
  - named Web Viewer object `wv_main`;
  - rating globals `FOCUS::g_wv_rating_lo` and `FOCUS::g_wv_rating_hi`, current native field ids `122` and `123`;
  - inherited context, action, movie, genre, module, and status fields;
  - inherited buttons bound to `WV__Demo_Build_Context`, `WV__Demo_Load_Viewer`, `WV__Demo_Push_Context`, and `WV__Demo_Run_All`;
  - the native repeating movie row, with no invented row-selection script binding.
- The operator corrected the context/action caption and field spacing in native Layout mode. That exact geometry was round-tripped from FileMaker and retained in the canonical generator and final pasted object set.
- A first native Browse check exposed three literal `{{FoundCount}}` / `{{RecordNumber}}` strings. Verified DDR examples showed that FileMaker's internal symbol representation requires `TextObj flags="8"` plus an empty `FieldList`; the generator was narrowed to that correction and the object set was replaced once.
- The final native Browse check evaluates the top found count as `33`, the current record number as `17`, and the visible body-row record numbers as `11` through `17`. It also preserves the corrected spacing and saved 1,300-point layout width. Evidence is preserved as `08-hybrid-layout-browse-native.png`.

## Unsatisfied acceptance items

- The operator-approved rating-landscape redesign is browser-tested but has not yet replaced modules `43` and `44` in the native target.
- The native FileMaker list surface exists, but row selection is not yet wired and the authoritative rating-band found-set path has not been built.
- Native-list-to-chart selection, chart-to-native selection, and chart-band-to-native-found-set acknowledgement remain unproved.
- Final native interaction screenshots and final target DDR/Summary/library exports do not exist.
- Article and exact build instructions remain intentionally undrafted because final source reconciliation is a prerequisite.

## Native integration stop-loss

Direct macOS UI automation created a malformed blank module record: FileMaker moved focus between editable fields differently than the accessibility coordinates implied, leaving `name = 43`, `index = 64`, and no code. No reviewed source was committed to that record. The malformed record was deleted immediately; the module count returned from 11 to the inherited 10.

The dated pre-edit backup remains:

`/Users/loncook/Documents/Databases:Invoices/Flicks_WebViewer_Framework_04_HybridInterface.prebuild-2026-08-12.fmp12`

## Exact next action

Reconcile the current exact `WV__Demo_Build_Context` and `WV__Demo_Handle_Action` source, then prepare the smallest Article 4 script packet that loads page module `43`, validates stable-id selection and rating-band intent, applies FileMaker-owned state, and returns acknowledgement context to both surfaces. Add a narrow native row-selection script only after its required record and state path is source-verified.

Stop-loss: if the current native script source differs from the latest native XML export, or a required field, table occurrence, helper, script id, found-set operation, or action contract cannot be verified, do not generate or paste the script packet; preserve the discrepancy for reconciliation.

## Superseding architecture note — 19 Aug 2026

The items above describe the state of the first implementation attempt; they are not the finished Article 4 architecture.

The final `WV Framework - Hybrid` layout is 1,300 points wide and based on the one-record `SOLUTION__all` table occurrence. It keeps `wv_main` on that stable host and presents ranked movies through the named `portal.hybrid_movies` portal, based on `MOVIE_GLOBAL_RATING` and sorted by the ordered stable-id relationship list in `SOLUTION__all::g_wv_hybrid_movie_ids`.

The final interaction path does not establish or navigate a `MOVIE` found set. FileMaker owns:

- the ordered portal membership list;
- `FOCUS::g_wv_demo_movie_id` as the acknowledged selected movie;
- `FOCUS::g_wv_rating_lo` and `FOCUS::g_wv_rating_hi` as the acknowledged rating band;
- the context and action JSON;
- portal count and selected-row position.

The portal row button calls `WV__Demo_Select_Native_Row` with `MOVIE_GLOBAL_RATING::id_movie`. Web Viewer dot and band actions continue through `WV.sendAction` and `WV__Demo_Handle_Action`. Both paths call `WV__Demo_Apply_Hybrid_Context`, which changes the relationship match list and selected globals, patches the resident page-43 context, refreshes only `metric.portal_count` and `metric.selected_row`, and pushes acknowledgement context without refreshing the window or reloading `wv_main`.

The original List View, ROWID, `Go to List of Records`, timer, and viewer-recovery experiments remain useful failure evidence. They are not build instructions and must not be described as the accepted result.
