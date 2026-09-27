# Article 4 portal metrics v2 install

This patch corrects the metric objects to FileMaker's native merge-calculation form and refreshes only those two objects after the private metric globals change.

## Replace in this order

1. On `WV Framework - Hybrid`, delete the four current `portal_count` / `selected_row` text objects and paste `WV_Framework_Hybrid_Portal_Metrics_v2.fmxmlsnippet`.
2. Replace the complete body of `WV__Demo_Build_Context` with `WV__Demo_Build_Context_Portal_Metrics_v2.fmxmlsnippet`.
3. Replace the complete body of `WV__Demo_Apply_Hybrid_Context` with `WV__Demo_Apply_Hybrid_Context_Portal_Metrics_v2.fmxmlsnippet`.

The two value objects are named `metric.portal_count` and `metric.selected_row`. The scripts use `Refresh Object` for exactly those names. They do not refresh the window or the `wv_main` Web Viewer.

## Native validation

1. Click `Run` and confirm `portal_count` shows the number of portal rows and `selected_row` shows the selected portal position.
2. Click a different portal row and confirm `selected_row` changes without a manual window refresh.
3. Select a rating range and confirm both values change immediately as appropriate.
4. Confirm the Web Viewer remains loaded throughout.

Static XML validation has passed. Native FileMaker acceptance remains pending until these checks are observed in the target file.
