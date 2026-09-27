# Redesign Browser-Harness Evidence

Tested: 15 Aug 2026

Target: `11-redesign-output/wv.renderer.hybrid.rating.js`

## Static checks

- JavaScript syntax passed `node --check`.
- Renderer contains no direct `FileMaker.PerformScript` call.
- Renderer contains no generated fallback rows or random data.
- Page module retains `LIB[20]`, `LIB[25]`, and `LIB[44]` dependencies.
- Action source remains `wv.renderer.hybrid.rating`.
- Action vocabulary remains limited to `hybrid.select_movie`, `hybrid.set_rating_band`, and `hybrid.clear_rating_band`.

## Populated render

- 33 rating-landscape points rendered.
- 14 histogram bins rendered.
- 5 selected-rank neighborhood controls rendered.
- One selected landscape point and one selected neighborhood item reflected the acknowledged FileMaker-owned id.
- No renderer console errors were reported in the direct harness.

## Action-envelope checks

Landscape point selection emitted:

```json
{
  "type": "hybrid.select_movie",
  "payload": { "movie_id": "MOVIE-01" },
  "options": { "source": "wv.renderer.hybrid.rating" }
}
```

Neighborhood selection emitted the same action shape with the selected neighbor's stable id.

Keyboard range selection emitted:

```json
{
  "type": "hybrid.set_rating_band",
  "payload": {
    "rating_lo": 6.1,
    "rating_hi": 6.434285714285714
  },
  "options": { "source": "wv.renderer.hybrid.rating" }
}
```

Clear-band selection emitted:

```json
{
  "type": "hybrid.clear_rating_band",
  "payload": {},
  "options": { "source": "wv.renderer.hybrid.rating" }
}
```

## Acknowledged and empty states

- Acknowledged band context produced one landscape band zone and eight overlapping highlighted histogram bins in the representative harness payload.
- The clear-band control was enabled only for acknowledged active-band context.
- Empty context removed all landscape points, histogram bins, and neighborhood controls and displayed the supplied empty-state message.

## Saved native Web Viewer dimensions

The responsive harness was evaluated at a 730 × 470 iframe, matching the current saved Web Viewer closely enough to test the relevant breakpoint:

- two-column analytical grid remained active;
- all five neighborhood controls fit inside the right column;
- 33 points, 14 bins, and 5 neighbors remained present;
- the dashboard shell height fit the viewer content height without stacking the three views below the visible area.

The sections above this point are browser evidence only. They do not by themselves prove FileMaker module persistence, library rebuild, native Web Viewer loading, bridge acknowledgement, native found-set changes, or the saved FileMaker layout.

## Native FileMaker color and bridge verification — 15 Aug 2026

- Live module 44 retained both prior history entries and added the amber/gold correction as the newest entry.
- The live module field contained the revised amber/gold band-zone, committed-bin, and drag-preview styles; coral selected-movie focus styles remained unchanged.
- The FileMaker module library was rebuilt, module 43 was reloaded, and the active acknowledged band rendered amber/gold in both the histogram and rating landscape.
- Activating `Clear rating band` in the native Web Viewer emitted `hybrid.clear_rating_band`, advanced the action count to 8, cleared the rating bounds, and restored the native found set to 33 records.
- Dragging the native histogram again emitted `hybrid.set_rating_band`, advanced the action count to 9, reapplied bounds 1497.78268186018–1498.85361858048, and reduced the native found set to 21 records.
- Native screenshot: `../screenshots/11-rating-band-amber-gold-native.png`.

## Native FileMaker resident-viewer performance verification — 16 Aug 2026

The interaction-time reload path was removed from the live Article 4 scripts. `WV__Demo_Handle_Action` and `WV__Demo_Select_Native_Row` contain no call to `WV__Demo_Load_Viewer` and no interaction pause. Redundant navigation to the already-active hybrid layout is guarded. The shared `. webviewer . load ( index ; -object_name )` script now retains each rendered data URL in `$$wv_url_map`, and the saved `wv_main` layout object resolves its address from that map.

Web Viewer-originated hybrid actions use one deferred pass through `WV__Demo_Apply_Hybrid_Context`, located in the root `Article 4` script folder. A 0.10-second host-idle handoff lets the Web Viewer-originated script return, then the continuation settles authoritative FileMaker state, yields 0.05 seconds for rendering, and pushes acknowledgement context to the resident viewer. If a newer intent arrives during that continuation, the ending action-count guard re-arms the pass so the newest intent is not stranded.

Native acceptance runs in `Flicks_WebViewer_Framework_04_HybridInterface.fmp12` produced:

- Rating-landscape dot: action count 25→26, current record 4→10, focus AC→BT, and `Context pushed to wv_main | result: ok`.
- Real pointer drag across histogram bins: action count 26→27, action type `hybrid.set_rating_band`, bounds 1498.13966076695–1499.03210803387, native found set 16→18, and final push `ok`.
- Native FileMaker list row: action count 27→28, current record 10→5, focus BT→AC, and final push `ok`.
- Repeated rating-landscape dot under a 36-frame screenshot burst: action count 28→29, current record 5→10, final push `ok`, and the rendered dashboard remained present in every captured frame. No blank Web Viewer frame appeared.

None of these four interactions appended a `Viewer loaded` event. The dashboard also remained accessible and rendered after a separate five-second persistence hold.

- Settled native proof: `native-performance-proof-2026-08-16.png`.
- No-flash frame contact sheet: `native-dot-no-flash-contact-2026-08-16.png`.

## Native FileMaker low-latency acceptance — 16 Aug 2026 (superseded)

The rating-band found-set rebuild now derives the exact stable-id list with `ExecuteSQL`, freezes the active window, shows all 100 `MOVIE` records, and omits nonmatching local records in one pass. The normal nonempty-band path creates no find requests. Selection-only acknowledgements skip that found-set rebuild entirely.

Native acceptance in the reopened `Flicks_WebViewer_Framework_04_HybridInterface.fmp12` produced:

- Direct build for bounds 1498.13966076695–1499.03210803387 completed in approximately 0.06 seconds and produced the exact 18-record native found set.
- A real histogram drag displayed the amber/gold band and `applying` state at the 100 ms capture. The authoritative context was settled, the `applying` marker was cleared, the found count remained exactly 18, and the resident viewer remained rendered by the approximately 350 ms capture.
- A rating-landscape dot displayed `Updating FileMaker: BT: Polar Gate (2018) · Rank 17` at the 100 ms capture. FileMaker selected BT, kept the 18-record found set, pushed context successfully, and cleared the pending state by the approximately 300 ms capture.
- Two dot intents issued 150 ms apart advanced the action count 9→11. The continuation re-arm guard acknowledged the newest BT intent by the approximately 350 ms capture; no queued action remained.
- No tested range or dot interaction reloaded the Web Viewer or produced a blank frame.

Native timing captures for this pass are retained as `/tmp/range010-100ms.png`, `/tmp/range010-350ms.png`, `/tmp/dot010-100ms.png`, `/tmp/dot010-300ms.png`, `/tmp/rapid010-100ms.png`, and `/tmp/rapid010-350ms.png` for the current workstation session.

## Superseding native low-latency acceptance — 16 Aug 2026

The preceding timer-based acceptance did not reproduce the operator's later observation of delays ranging from several seconds to minutes. It is retained as historical evidence, but its architecture and latency claim are superseded by this section.

Further native diagnosis established two independent costs:

- the handler rebuilt the entire hybrid context, including SQL and repeated JSON-array work, for every interaction;
- the timer continuation could take approximately 16 seconds to fire in the observed FileMaker session, so it was not a reliable low-latency acknowledgement path.

An `fmp://` callback experiment changed native state in approximately five seconds but did not consistently push acknowledgement context back into the Web Viewer. That path was abandoned.

The accepted live architecture now:

- defers the established `FileMaker.PerformScript` bridge by one browser task inside `WV.sendAction`, allowing the originating pointer event stack to return;
- validates and applies intent in `WV__Demo_Handle_Action`;
- derives rating-band membership from the already-resident 33-row context and performs an exact stable-id multi-request find instead of scanning the native table record by record;
- locates the target in the native found set with `GetNthRecord` and performs one calculated record navigation instead of walking through records and repeatedly invalidating the Web Viewer surface;
- patches selection, band, found-count, record-number, action acknowledgement, and affected `row.selected` values in the resident context JSON instead of rebuilding the whole context;
- calls `WV__Demo_Push_Context` directly after native state settles, without reloading the Web Viewer.

Native acceptance in the reopened `Flicks_WebViewer_Framework_04_HybridInterface.fmp12` produced:

- A neighbor/title selection emitted exactly one `hybrid.select_movie` action, advanced the action count 28→29, selected `B: Star Forge (2019) · Rank 27` as native record 1 of 23, and was fully settled in the first 100 ms capture. The resident dashboard remained rendered throughout the 100, 300, 700, and 1,500 ms captures.
- A real pointer drag across the rating histogram emitted exactly one `hybrid.set_rating_band` action, advanced the action count 29→30, applied bounds 1497.60419240679–1498.85361858048, retained the 23-record native found set and the acknowledged `B: Star Forge` selection, and was fully settled in the first 100 ms capture.
- Captures at approximately 300 ms, 700 ms, and 2,000 ms remained unchanged and rendered. No tested interaction appended a viewer-load event or showed a reload flash.

The live FileMaker file remains the authority for the installed scripts and module record. Canonical generated script source is `../../fmxmlsnippets/WV__Demo_Handle_Action_Hybrid.fmxmlsnippet`; the canonical module-25 source corresponding to the installed record is retained as `../source/2026-08-15-manual-module-gate/wv.platform.actions.js`.

## Superseding stable-host and bridge-drain acceptance — 16 Aug 2026

The preceding acceptance still depended on a `MOVIE`-anchored layout and therefore did not survive the operator's recording evidence: changing the current record or found set reconstructed the Web Viewer, raced context pushes, and produced delays from seconds to minutes. That resident-viewer invariant is superseded by the native evidence below.

The repaired live architecture now:

- hosts the hybrid interface on the one-record `SOLUTION__all` table occurrence in `WV Framework - Hybrid Stable`;
- presents `MOVIE` records through a native portal rather than making the Web Viewer's host record follow selection or filtering;
- builds the 33-row authoritative context without interaction-time layout changes, finds, record navigation, show/omit operations, or current-record changes;
- keeps one Web Viewer action in flight, coalesces a 100 ms pointer-event burst to the latest intent, and treats receipt of authoritative `WV_FM_PUSH` context as the acknowledgement;
- retains the native lock through the short handler-unwind window so a queued intent cannot re-enter FileMaker while the prior handler is returning;
- rebuilds and pushes authoritative context before every handler exit, including malformed, unsupported, invalid-selection, invalid-band, and other rejection exits.

Native interface monitoring at 500 ms intervals established:

- The stable host remained record 1 of 1 while context contained 33 movies; selection and rating-band work did not navigate the host layout or its found set.
- An accepted rating-landscape dot showed `Updating FileMaker` in the first captured frame and was acknowledged and redrawn by the next frame. No loading frame or viewer flash occurred.
- A real histogram drag changed the acknowledged upper bound to `1498.6751291271`; it was already settled before the first 500 ms capture after pointer-up.
- A deliberately rejected dot outside the active rating band showed the request state in the first frame and returned to `Dashboard ready` by the next frame. This specifically proves that rejection now releases the bridge.
- A six-click, 30 ms-spaced dot burst settled before the first captured frame, retained only the latest intent, and left no queued or waiting state.
- A histogram drag issued immediately after that burst advanced the native action count 60→61, applied bounds `1497.60419240679–1498.49663967372`, showed `applying` in frame 0, and was settled in frame 1. This proves the burst released the bridge for the next action.
- Across all final captures, the dashboard remained rendered. No `Loading rating landscape…` frame, Web Viewer reload flash, FileMaker record navigation, or beachball was observed.

Canonical installed-source counterparts are:

- `../../fmxmlsnippets/WV__Demo_Build_Context_Hybrid.fmxmlsnippet`
- `../../fmxmlsnippets/WV__Demo_Handle_Action_Hybrid.fmxmlsnippet`
- `../source/2026-08-15-manual-module-gate/wv.platform.actions.js`

The live `.fmp12` file remains the authority for the installed scripts, module 25, stable layout, and portal.

## Final portal-layout and metric reconciliation — 19 Aug 2026

The preceding stable-host section proves the architectural direction, but its layout name and several implementation details were subsequently replaced. This section is authoritative for the final article and build instructions.

Fresh exports:

- `../Flicks_WebViewer_Framework_04_HybridInterface_fmp12.xml` — DDR generated 19 Aug 2026 at 00:18:23.
- `../Flicks_WebViewer_Framework_04_HybridInterface.xml` — FileMaker Pro 26.0.2 Save as XML generated 19 Aug 2026 at 00:18:41.
- `../Summary.xml` — generated 19 Aug 2026 at 00:18:22.

The exports verify:

- Layout `WV Framework - Hybrid` (`id 150`) is 1,300 points wide and based on `SOLUTION__all`.
- The resident Web Viewer remains named `wv_main`.
- The native record surface is `portal.hybrid_movies`, an eight-visible-row portal based on `MOVIE_GLOBAL_RATING`.
- The portal displays rank, title, genres, year, global rating, and stable movie id. The `GENRES` column uses the related `hybrid.movie.movie_genre.GENRE::name` values added by the operator.
- Portal membership comes from the ordered stable-id list in `SOLUTION__all::g_wv_hybrid_movie_ids`.
- The full-row button `button.hybrid_portal_row` and the row objects use `FOCUS::g_wv_demo_movie_id` for the amber/gold acknowledged selection treatment.
- `WV__Demo_Select_Native_Row` validates the clicked `MOVIE_GLOBAL_RATING::id_movie` against the current portal id list, writes the FileMaker-owned selection, applies the hybrid context patch, and pushes context without changing the host record.
- `WV__Demo_Handle_Action` handles `hybrid.select_movie`, `hybrid.set_rating_band`, and `hybrid.clear_rating_band` through globals and the portal match list. Its hybrid path contains no found-set or current-record navigation.
- `WV__Demo_Apply_Hybrid_Context` derives filtered portal membership from the already-resident page-43 row context, preserves the selected movie when it remains present, otherwise selects the first matching row, patches the context, and pushes the acknowledgement path without a find, layout change, timer, or Web Viewer reload.
- `portal_count` and `selected_row` are no longer FileMaker layout symbols tied to the one-record host. They display `$$wv_hybrid_portal_count` and `$$wv_hybrid_selected_position` through named merge-calculation objects `metric.portal_count` and `metric.selected_row`.
- Both context scripts use `Refresh Object` only for those two named metrics. They do not call `Refresh Window` and do not target `wv_main`.

This static reconciliation proves the installed object and script structure. Final publication screenshots must still show the current portal layout after a clean Run, a portal-row selection, a Web Viewer dot selection, and a rating-band change. Static exports do not replace those native interaction captures.
