# Native Test Evidence

## Pre-integration renderer loop — 12 Aug 2026

Environment: browser harness, explicitly not native FileMaker proof.

- Populated context rendered 12 real-shaped rows into 16 derived bins.
- Focus marker resolved to stable id `MOVIE-4`.
- Clicking `AL: Twilight Cargo (2015)` emitted `hybrid.select_movie` with `movie_id: MOVIE-1`.
- Keyboard band selection emitted `hybrid.set_rating_band` with numeric lower/upper bounds.
- Pointer drag across several bars emitted only the starting bin (`1496.31`–`1496.535625`).
- Diagnosed layer: renderer pointer tracking, before the FileMaker bridge.

## Native integration evidence

Pending integration into `Flicks_WebViewer_Framework_04_HybridInterface.fmp12`. Final entries must include incoming context, outgoing action, FileMaker found set/current record, acknowledgement state, and screenshot filenames. This placeholder is explicit; browser evidence is not being promoted to native proof.

