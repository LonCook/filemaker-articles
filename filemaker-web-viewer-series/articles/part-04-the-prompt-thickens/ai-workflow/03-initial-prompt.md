# Initial Prompt: Propose The Hybrid Rating Modules

## 1. Job

Extend the existing FileMaker/Web Viewer framework with an accessible rating distribution that works alongside the native FileMaker record surface.

The two surfaces must behave as views of the same FileMaker-owned movie scope, selected movie, and rating band. JavaScript presents the visualization and reports user intent. FileMaker validates that intent, changes authoritative state, and returns acknowledgement context.

Propose only the new page and renderer modules in this pass. Do not modify FileMaker scripts yet.

## 2. Current Source And Contracts

Inspect these project files before proposing code:

- `01-human-brief.md` — human-owned purpose, behavior, accessibility requirements, and boundaries.
- `02-context-manifest.md` — exact current exports, accepted modules, FileMaker scripts, representative JSON, dependencies, and deliberate exclusions.
- Every source file named by the manifest. Current source outranks inference or memory.

Preserve the existing architecture:

- FileMaker supplies `ranked_view.rows`, `ranked_view.selected_movie_id`, `ranked_view.native_found_count`, and `ranked_view.rating_band`.
- Each row uses its stable `movie_id` and supplied display, rating, rank, and selected values.
- JavaScript sends intent only through inherited module `25`, `WV.sendAction`.
- Allowed actions are `hybrid.select_movie`, `hybrid.set_rating_band`, and `hybrid.clear_rating_band`.
- JavaScript may retain hover, drag, animation, and in-flight preview state.
- JavaScript may not retain authoritative selected-movie, rating-band, found-set, or acknowledgement state. Returned FileMaker context wins on every render.
- An empty `ranked_view.rows` array is an empty state. Do not invent fallback movies or production-looking data.

Follow the module conventions visible in the supplied source:

- New module `43`: `wv.page.hybrid.rating.html`.
- New module `44`: `wv.renderer.hybrid.rating.js`.
- Preserve the established module-header format.
- Declare exact dependencies and exports.
- Add the modules to the existing assembly model; do not invent another loader or bridge.

Do not import production module `66`, movers, layered surfaces, camera behavior, production reducers, synthetic defaults, or cache/deployment machinery.

## 3. Acceptance Criteria And Stop Line

The proposal must satisfy these acceptance criteria:

1. Render an accessible SVG rating histogram derived honestly from the supplied rows.
2. Show the movie identified by FileMaker as selected with a visible focus marker.
3. Support one contiguous rating-band selection through pointer and keyboard interaction.
4. Send movie selection and rating-band intent only through `WV.sendAction` using the three allowed actions.
5. Wait for returned FileMaker context before treating selection or band state as accepted.
6. Render loading, empty, error, selected, and filtered states legibly.
7. Reject absent numeric values rather than coercing them into synthetic zeroes.
8. Include no direct `FileMaker.PerformScript` call and no browser-owned authoritative state.
9. Preserve exact module dependencies, exports, action names, and stable movie identifiers.
10. Provide complete source that can be reviewed in the browser harness before FileMaker integration.

Stop after returning the two proposed modules. Do not create or modify FileMaker scripts, schema, relationships, layouts, or deployment machinery. The proposal will be reviewed before integration.

## 4. Requested Change And Delivery

Return:

1. The complete source for module `43`, `wv.page.hybrid.rating.html`.
2. The complete source for module `44`, `wv.renderer.hybrid.rating.js`.
3. A compact dependency and export summary for each module.
4. A compact explanation of how the proposal preserves FileMaker ownership and uses `WV.sendAction`.

Do not return partial patches. Do not broaden the requested change.
