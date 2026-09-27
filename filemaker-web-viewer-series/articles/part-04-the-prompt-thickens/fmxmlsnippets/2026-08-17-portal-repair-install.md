# Article 4 Portal Repair — Manual Install

These snippets replace the MOVIE List View interaction surface with a relationship-backed portal. They do not edit the FileMaker file directly.

## Completed phase

The 2026-08-17 23:46 DDR was reconciled. It verifies:

- `SOLUTION::g_wv_hybrid_movie_ids` is global text, field id `23`.
- `SOLUTION__all::g_wv_hybrid_movie_ids = MOVIE_GLOBAL_RATING::id_movie`.
- The related `MOVIE_GLOBAL_RATING` side is sorted by `global_rank_order` ascending.
- `MOVIE_GLOBAL_RATING → hybrid.MOVIE → hybrid.TITLE~display` has the required ID and display-title predicates.

## Script replacement order

In the existing `Article 4` script folder, replace the complete steps inside these existing scripts in this exact order:

1. `WV__Demo_Build_Context`
   - Paste `WV__Demo_Build_Context_Portal_v2.fmxmlsnippet`.
   - Version 2 restores the FileMaker `\"` escapes around quoted SQL identifiers. The original portal snippet is superseded.
2. `WV__Demo_Apply_Hybrid_Context`
   - Paste `WV__Demo_Apply_Hybrid_Context_Portal.fmxmlsnippet`.
3. `WV__Demo_Handle_Action`
   - Paste `WV__Demo_Handle_Action_Portal.fmxmlsnippet`.
4. `WV__Demo_Select_Native_Row`
   - Paste `WV__Demo_Select_Native_Row_Portal.fmxmlsnippet`.
5. `WV__Demo_Run_All`
   - Paste `WV__Demo_Run_All_Portal_v2.fmxmlsnippet`.
   - This removes the inherited hardcoded module `41` argument. Run now uses the module index established by `WV__Demo_Build_Context` (`43` for the Article 4 rating landscape).
   - Version 2 also force-loads the selected module when the explicit Run command is used, preventing stale loaded-state globals from leaving a blank viewer. Interaction scripts remain push-only.

Each file contains only script steps inside `<fmxmlsnippet type="FMObjectList">`. Do not paste a snippet while the insertion point is inside another step or control block. Select the complete existing script body first, then paste its complete replacement.

## Layout conversion

On `WV Framework - Hybrid`:

1. Open Layout Setup and change **Show records from** to `SOLUTION__all`.
2. Set the layout's default view to **Form View**.
3. Keep the existing Top Navigation part and all of its objects, including `wv_main` and the Diagnostics popover.
4. Delete only the four obsolete native List View row objects at approximately `y = 523–548`:
   - `{{RecordNumber}}`
   - `MOVIE::title_year_display`
   - `MOVIE::ID`
   - `button.native_row_select`
5. Increase the Body part to at least `358 pt` high so its bottom is at or below `y = 878`.
6. With the Body part active and no object selected, paste `WV_Framework_Hybrid_Portal_Objects.fmxmlsnippet`.

The pasted group contains column headings and `portal.hybrid_movies`. The portal has ten visible rows, uses the relationship's `global_rank_order` sort, and calls the existing script `WV__Demo_Select_Native_Row` with `MOVIE_GLOBAL_RATING::id_movie`.

The full-row button uses this conditional-format calculation:

```text
GetAsText ( MOVIE_GLOBAL_RATING::id_movie ) =
GetAsText ( FOCUS::g_wv_demo_movie_id )
```

Its selected state is amber/gold and the stable movie ID remains the public selection identifier.

## Native validation sequence

After leaving Layout Mode:

1. Click `Run` once to build the initial relationship list, load the viewer, and push context.
2. Select a rating band that retains the selected movie.
   - Portal membership changes.
   - Selection remains unchanged.
   - The Web Viewer does not show its loading state or reset its runtime.
3. Select a rating band that excludes the selected movie.
   - Portal membership changes.
   - FileMaker selects and highlights the first ranked portal row.
   - The acknowledged context selects the same movie in the chart.
4. Clear the band.
   - The complete genre-scoped portal list returns in global-rank order.
5. Click an eligible chart dot.
   - The corresponding portal row becomes amber/gold without FileMaker record navigation.
6. Click a portal row.
   - The chart acknowledges the same stable movie ID without reloading.
7. Repeat rapid range and row/dot selections while watching Script Debugger.
   - No hybrid interaction should execute `Enter Find Mode`, `Perform Find`, `Go to List of Records`, `Go to Record/Request/Page`, or `Install OnTimer Script`.

Completion remains pending until this sequence is observed in the native FileMaker interface.
