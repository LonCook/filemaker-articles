# Context Manifest

Captured: 12 Aug 2026

## Full source supplied

- `source/2026-08-12-prebuild-article-03/Flicks_WebViewer_Framework_03_RankedViews_fmp12.xml` — fresh native DDR from `Flicks_WebViewer_Framework_03_RankedViews.fmp12`; created 12 Aug 2026 at 12:13:36 PM.
- `source/2026-08-12-prebuild-article-03/Summary.xml` — fresh native summary; 8 base tables, 11 table occurrences, 4 layouts, 14 scripts.
- `source/2026-08-12-prebuild-article-03/LIBRARY_CODE.tab` — fresh 10-record module export.
- `source/2026-08-12-prebuild-production/Flicks clone_fmp12.xml` — fresh native DDR from the read-only production reference; created 12 Aug 2026 at 12:18:11 PM.
- `source/2026-08-12-prebuild-production/Summary.xml` — fresh native summary; 26 base tables, 100 table occurrences, 44 layouts, 182 scripts.
- `source/2026-08-12-prebuild-production/LIBRARY_CODE.tab` — fresh 17-record module export.
- `../article three/source/wv.page.ranked.list.html` and `wv.renderer.ranked.list.js` — exact accepted Article 3 modules.
- `../article three/fmxmlsnippets/WV__Demo_Build_Context_Ranked.fmxmlsnippet.xml` — exact cumulative context builder.
- `../article three/fmxmlsnippets/WV__Demo_Handle_Action_Ranked.fmxmlsnippet.xml` — exact cumulative action handler.

## Source excerpts supplied

- Production layout `UI__Ranked_List`, Web Viewer object `wv_viz`, and its native focus-row button paths.
- Production modules `66`, `67`, and `68` from the fresh library export.
- Production scripts `UI__Ranked_FocusRow_Set`, `WV__Rating_Dashboard_Action ( action_json )`, `RANK__RatingDashboardState_ApplyAction ( action_json )`, and the rating-dashboard context/refresh path from the fresh DDR.
- Representative Article 3 `ranked_view` JSON copied from the successful native Sci-Fi run preserved in `article-03-let-the-record-show.md`.

## Production closure findings

- `67 -> 20, 66, 68`; module `20` expands platform modules `21`–`24`.
- Module `68` calls `window.FileMaker.PerformScript` directly, retains optimistic focus/band state, and supplies deterministic fallback values.
- Module `68` also carries movers and layered surface behavior; module `66` alone is a large standalone 3D helper.
- Production state depends on the broader rating-dashboard reducer, row-scope globals, native focus script, context builder, and refresh scripts.

## Deliberate adaptations

- Retain the source-backed P1 rating-distribution idea, selected focus, and band interaction.
- Replace direct bridge behavior with cumulative module `25`, `WV.sendAction`.
- Replace production action names with three walkthrough-specific `hybrid.*` actions.
- Drive bins directly from the Article 3 ranked rows so no synthetic fallback or production reducer is required.
- Omit movers, layered surfaces, camera behavior, neighbors, production state globals, and general action routing.

## Abridged article material

Any excerpt in the article will be labeled as abridged and reconciled to the final target exports. Full implementation remains in the final source export and FMXML snippets.

