# Human Brief: Hybrid Ranked Interface

Prepared before requesting renderer code: 12 Aug 2026

## Payoff

Build one hybrid interface in `Flicks_WebViewer_Framework_04_HybridInterface.fmp12`: a native FileMaker movie list and an interactive rating distribution must behave as two views of the same FileMaker-owned records, selection, and rating band.

The chart is an analytical control the native list does not readily provide. It is not a second application.

## Native FileMaker behavior

- The native list shows the authoritative found set of ranked `MOVIE` records.
- Selecting a native row makes that record current, writes its stable `MOVIE::ID` to the demo selection state, rebuilds context, and pushes the acknowledged state to the Web Viewer.
- A rating band changes the authoritative native found set. Clearing the band restores the genre-ranked collection.
- Native fields expose selected movie id, band bounds, found count, current record number, last action, action status, incoming context, and outgoing action JSON.

## Visualization behavior

- Render a real rating distribution from FileMaker-shaped rows.
- Draw a visible focus marker for the movie FileMaker marks selected.
- Let the user choose a contiguous rating band by dragging or keyboard-adjusting over histogram bins.
- Report movie selection and band intent through `WV.sendAction`; wait for returned context before treating either as authoritative.
- Render loading, empty, populated, selected, filtered, and error states.

## Allowed changes

After source inspection, the accepted change may touch:

- new page module `43`, `wv.page.hybrid.rating.html`
- new renderer module `44`, `wv.renderer.hybrid.rating.js`
- `WV__Demo_Build_Context`
- `WV__Demo_Handle_Action`
- a narrowly scoped native-row selection script
- a thin hybrid list layout and demo global fields required for rating-band state

Inherited module `25`, `wv.platform.actions.js`, remains the only JavaScript-to-FileMaker bridge.

## Input contract

The renderer receives the established Article 3 context plus:

```jsonc
{
  "__wv": {
    "contract_version": 1,
    "page": 43,
    "page_name": "hybrid_rating"
  },
  "ranked_view": {
    "rows": [
      {
        "movie_id": "stable FileMaker id",
        "display_title": "display-ready title",
        "rating": 1499.12,
        "rank": 4,
        "selected": true
      }
    ],
    "selected_movie_id": "stable FileMaker id",
    "native_found_count": 33,
    "rating_band": {
      "active": false,
      "rating_lo": null,
      "rating_hi": null,
      "label": "All ratings"
    }
  }
}
```

## Allowed actions

- `hybrid.select_movie` with `payload.movie_id`
- `hybrid.set_rating_band` with numeric `payload.rating_lo` and `payload.rating_hi`
- `hybrid.clear_rating_band` with an empty object payload

Every action uses `WV.sendAction(type, payload, { source: "wv.renderer.hybrid.rating" })`.

## Ownership and validation

- JavaScript may retain hover, drag, animation, and in-flight presentation state.
- JavaScript may not retain authoritative selected movie, rating band, native found set, or acknowledgement state.
- FileMaker validates envelope version, source, type, ids, numeric bounds, bound order, and membership in the current ranked collection.
- FileMaker performs native selection or found-set work, rebuilds context, and returns acknowledgement context.

## Accessibility

- The histogram has an accessible name and concise instructions.
- Each bin is keyboard focusable and exposes its range and count.
- Selected band and focus are not communicated by color alone.
- Status changes use a polite live region.
- Pointer dragging has keyboard-equivalent band controls.

## Acceptance tests

1. Native row selection updates FileMaker selection and the chart focus marker.
2. Chart movie selection sends a stable id through `WV.sendAction`; FileMaker validates, navigates, and returns selected context.
3. Chart band selection sends numeric bounds through `WV.sendAction`; FileMaker applies the authoritative found-set change and both surfaces display the returned band.
4. Clearing the chart band restores the FileMaker-owned ranked collection.
5. Reloading or navigating cannot leave browser-owned selection or band state contradicting FileMaker.
6. Empty, loading, error, selected, and filtered states remain legible.
7. Accepted renderer contains no direct `FileMaker.PerformScript` call and no synthetic production-looking fallback data.

## Test environments

- Browser harness: renderer geometry, pointer/keyboard events, empty/error states, and outbound envelope capture.
- Native FileMaker target: list, found set, bridge, validation, navigation, acknowledgement, and final screenshots.

## Stop lines

Do not import the production dashboard router, reducer, movers, layered 3D surfaces, camera state, synthetic defaults, direct FileMaker bridge calls, or cache/version/deployment machinery reserved for the next pass.

