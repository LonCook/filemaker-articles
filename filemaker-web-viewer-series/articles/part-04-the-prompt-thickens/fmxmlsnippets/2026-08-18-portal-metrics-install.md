# Article 4 Portal Metrics — Manual Install

The hybrid layout is based on the one-record `SOLUTION__all` host. Therefore FileMaker's native `{{FoundCount}}` and `{{RecordNumber}}` symbols correctly remain `1` and `1`; they cannot describe the related portal.

## Complete script replacements

Replace complete script bodies in this order:

1. `WV__Demo_Build_Context`
   - Paste `WV__Demo_Build_Context_Portal_Metrics.fmxmlsnippet`.
2. `WV__Demo_Apply_Hybrid_Context`
   - Paste `WV__Demo_Apply_Hybrid_Context_Portal_Metrics.fmxmlsnippet`.

The scripts expose their already-calculated portal metrics as private FileMaker globals:

- `$$wv_hybrid_portal_count`
- `$$wv_hybrid_selected_position`

No find, found-set, current-record, viewer-load, or timer step is added.

## Layout objects

On `WV Framework - Hybrid` in Layout Mode:

1. Delete only these four objects:
   - `found_count`
   - `{{FoundCount}}`
   - `record_number`
   - `{{RecordNumber}}`
2. With no object selected, paste `WV_Framework_Hybrid_Portal_Metrics.fmxmlsnippet`.

The replacements retain the same bounds and display:

- `portal_count` → `<<$$wv_hybrid_portal_count>>`
- `selected_row` → `<<$$wv_hybrid_selected_position>>`

## Native verification

1. Click `Run` with Sci-Fi and a cleared rating band. Expect approximately `33` and a selected row position greater than zero.
2. Select a different portal row or chart dot. `selected_row` must change when the selected rank position changes.
3. Apply a rating band. `portal_count` must match the visible related rows and `selected_row` must be the selected row's position within that filtered portal.
4. Clear the band. Expect the complete genre-scoped count to return.
