# Revision Prompt

Revise the initial module `44` proposal using this observed evidence.

Observed browser-harness failure:

- Drag began in the first histogram bin and crossed several visible bars.
- Outbound action was `hybrid.set_rating_band`, but the bounds covered only the starting bin: `1496.31`–`1496.535625`.
- Keyboard range selection worked.
- Source inspection shows pointer capture is set on the starting `rect`, while range growth depends on `pointerenter` firing on sibling rectangles.

Required correction:

1. Track pointer drag at the chart level.
2. Convert the current pointer x-coordinate to a clamped bin index using the SVG viewBox/chart bounds.
3. Keep the starting bin as transient state; update the preview from chart-level pointer movement.
4. Commit one narrow `hybrid.set_rating_band` action on pointer release.
5. Preserve FileMaker ownership; do not mark the preview authoritative or synthesize acknowledgement.
6. Reject null, undefined, and empty-string numeric values before calling `Number(...)`.
7. Make acknowledged band/bin overlap consistent at shared edges.
8. Do not change the input contract, action names, module indexes, dependency closure, or stop lines.

Return the reviewed module source plus a compact diff explanation. Do not modify FileMaker scripts.

