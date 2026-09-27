# Operator-Approved Redesign: Rating Landscape

Approved from the visual mockup on 15 Aug 2026.

## Why the first closure was rejected

The first Article 4 closure placed a rating histogram beside a native FileMaker list. It proved a possible shared-state path, but it was still substantially the Article 3 ranked-view demo with a second surface. The operator rejected it as an insufficient payoff for the promised richer visualization.

The original human brief, initial prompt, reviewed output, and failure evidence remain unchanged as the authentic record of that attempt. This redesign supersedes the visual target; it does not rewrite that history.

## Approved visual target

The Article 4 Web Viewer becomes a coordinated rating-analysis workspace containing three linked views:

1. **Rating landscape**
   - Plot every FileMaker-shaped movie row by release year and global rating.
   - Highlight the FileMaker-owned selected movie.
   - Show the acknowledged rating band across the chart.
   - Selecting a point sends `hybrid.select_movie` with its stable movie id.

2. **Rating distribution**
   - Retain the accessible histogram and contiguous rating-band interaction.
   - The acknowledged band, rather than local preview state, controls the settled visual treatment.
   - Band changes continue through `hybrid.set_rating_band` and `hybrid.clear_rating_band`.

3. **Nearby in rank**
   - Derive a compact comparison neighborhood from the same FileMaker-shaped rows.
   - Center the FileMaker-owned selected movie and show adjacent ranked movies.
   - Selecting a neighbor sends the same narrow stable-id action as a landscape point.

The native FileMaker list remains visible as the authoritative record surface. Selection is cross-highlighted in the landscape, distribution, neighborhood, and native row only after FileMaker acknowledges the state.

## Verified data boundary

No new schema is required. The current Article 4 context already provides each ranked row's:

- `movie_id`
- `display_title`
- `year`
- `rating`
- `rank`
- `selected`

The current context also provides FileMaker-owned `selected_movie_id`, `native_found_count`, and `rating_band` state.

## Retained contracts

- Module `43`: `wv.page.hybrid.rating.html`
- Module `44`: `wv.renderer.hybrid.rating.js`
- JavaScript bridge: inherited module `25`, `WV.sendAction`
- Actions: `hybrid.select_movie`, `hybrid.set_rating_band`, and `hybrid.clear_rating_band`
- FileMaker remains authoritative for selection, found set, rating band, validation, and acknowledgement.

## Explicit exclusions

The redesign does not import the production reducer, direct `FileMaker.PerformScript` calls, synthetic fallback rows, camera state, or cache/deployment machinery. It earns the larger visual payoff from the real Article 4 row contract rather than copying the broader production application.

## Acceptance additions

- The Web Viewer visibly performs analysis the native list does not: year/rating pattern, distribution, and selected-rank neighborhood.
- One acknowledged FileMaker selection is visibly consistent in all four surfaces.
- A rating band filters the native found set and settles consistently in the landscape, distribution, neighborhood, and native list.
- The three Web Viewer views remain usable at the saved native Web Viewer dimensions.
- Pointer and keyboard interaction are available for every actionable Web Viewer view.

## Visual reference

`../screenshots/10-hybrid-rating-landscape-mockup.png`

This image is a design target, not native FileMaker acceptance evidence.
