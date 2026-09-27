# Review Notes: Initial Renderer Proposal

Reviewed: 12 Aug 2026

## Accepted

- New page/renderer boundary at modules `43` and `44`; no production router or 3D dependency.
- Renderer consumes only `ranked_view.rows` and returned FileMaker state.
- Empty data remains empty; no deterministic production-looking fallback records are invented.
- Movie ids remain stable action values; display titles are not used as identity.
- All accepted outbound calls use `WV.sendAction` with source `wv.renderer.hybrid.rating`.
- Selected movie and rating band are re-read from context on every render.
- SVG marks, live status, keyboard focus, and action labels provide a reasonable accessibility baseline.
- Browser harness proved the expected `hybrid.select_movie` and keyboard `hybrid.set_rating_band` envelopes.

## Rejected or revised

1. **Pointer band range stopped at the first bin.** The initial code captured the pointer on the starting `rect` and depended on sibling `pointerenter` handlers to advance `dragEnd`. In the browser harness, dragging from the first through the fourth visible bar emitted only the first bin: `1496.31`–`1496.535625`.
2. **Null numeric values normalized to zero.** `Number(null)` and `Number("")` are `0`; the helper must reject null/empty inputs before numeric conversion so an incomplete returned band cannot appear numerically valid.
3. **Band overlap used inclusive shared edges.** A returned upper edge could visually select the immediately adjacent bin. The corrected comparison treats bin intervals consistently and includes the final maximum explicitly.
4. **Page header provenance.** The initial module history labels the code as an AI proposal. The accepted module will retain that provenance but add the human review/revision entry above it, newest first.

## Contract checks

- Direct `FileMaker.PerformScript` in proposed renderer: none.
- Invented FileMaker scripts, fields, or APIs: none.
- Scope growth into movers, surfaces, reducers, cache, or deployment: none.
- Browser-owned authoritative selection/filter state: none; transient pointer and keyboard previews only.

The proposal is useful but not accepted unchanged. Pointer tracking and numeric normalization require revision before native integration.

