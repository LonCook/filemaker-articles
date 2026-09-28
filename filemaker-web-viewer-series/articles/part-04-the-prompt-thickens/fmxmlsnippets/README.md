# Article 4 FileMaker Snippets

This folder preserves the hybrid-interface installation and repair artifacts produced during Article 4 development. FileMaker uses the same FMXML clipboard mechanism for different kinds of objects, so the paste target matters.

## Clipboard Handling

Codex placed the generated snippets directly onto the clipboard in FileMaker’s expected object format during the Article 4 build. That workflow did not require a separate plug-in or conversion utility.

The files stored in this directory are ordinary XML text. If that text is copied later from Git, a browser, or an editor, it must first be converted to FileMaker’s internal clipboard format before pasting:

- The [MBS `Clipboard.SetFileMakerData` function](https://www.mbsplugins.eu/ClipboardSetFileMakerData.shtml) or [MBS automatic clipboard converter](https://www.monkeybreadsoftware.com/filemaker/SyntaxColoring/43-ClipboardConverter.shtml) can perform that conversion.
- A dedicated [FM Clipboard Tool](https://filemakerhacks.com/2026/05/31/fm-clipboard-tool-and-fmxml/) is another option.

These are optional installation aids. Neither is a runtime dependency of the demo.

## Current Portal Installation Path

Follow these instructions in order:

1. [`2026-08-17-portal-repair-install.md`](2026-08-17-portal-repair-install.md) converts the hybrid layout to the `SOLUTION__all` portal architecture and installs the primary portal scripts and objects.
2. [`../source/build-notes/2026-08-18-portal-metrics-v2-install.md`](../source/build-notes/2026-08-18-portal-metrics-v2-install.md) installs the corrected portal metrics and targeted object refreshes.

## Current Script-Step Snippets

These files use `<fmxmlsnippet type="FMObjectList">`. Paste each one into the named FileMaker script after selecting its complete existing script body. They are script steps, not whole `<Script>` objects and not layout objects.

| FileMaker script | Pasteable snippet | Purpose |
| --- | --- | --- |
| `WV__Demo_Build_Context` | [`WV__Demo_Build_Context_Portal_Metrics_v2.fmxmlsnippet`](WV__Demo_Build_Context_Portal_Metrics_v2.fmxmlsnippet) | Builds the portal-backed context and private portal metrics. |
| `WV__Demo_Apply_Hybrid_Context` | [`WV__Demo_Apply_Hybrid_Context_Portal_Metrics_v2.fmxmlsnippet`](WV__Demo_Apply_Hybrid_Context_Portal_Metrics_v2.fmxmlsnippet) | Applies acknowledged portal state and refreshes only the two metric objects. |
| `WV__Demo_Handle_Action` | [`WV__Demo_Handle_Action_Portal.fmxmlsnippet`](WV__Demo_Handle_Action_Portal.fmxmlsnippet) | Validates and handles the three `hybrid.*` actions. |
| `WV__Demo_Select_Native_Row` | [`WV__Demo_Select_Native_Row_Portal.fmxmlsnippet`](WV__Demo_Select_Native_Row_Portal.fmxmlsnippet) | Converts a portal-row click into FileMaker-owned selection and acknowledgement. |
| `WV__Demo_Run_All` | [`WV__Demo_Run_All_Portal_v2.fmxmlsnippet`](WV__Demo_Run_All_Portal_v2.fmxmlsnippet) | Builds context, loads module `43` when Run is explicit, and pushes context. |
| `. webviewer . load ( index ; -object_name )` | [`WebViewer_Load_Persistent_URL.fmxmlsnippet`](WebViewer_Load_Persistent_URL.fmxmlsnippet) | Persists the rendered viewer URL for reuse without interaction-time reloads. |

## Current Layout-Object Snippets

These files use `<fmxmlsnippet type="LayoutObjectList">`. Paste them in Layout Mode with the correct layout part active and no existing object selected. Do not paste them into Script Workspace.

| Pasteable snippet | Layout content |
| --- | --- |
| [`WV_Framework_Hybrid_Portal_Objects.fmxmlsnippet`](WV_Framework_Hybrid_Portal_Objects.fmxmlsnippet) | Portal, column headings, row fields, full-row selection button, and selected-row conditional formatting. |
| [`WV_Framework_Hybrid_Portal_Metrics_v2.fmxmlsnippet`](WV_Framework_Hybrid_Portal_Metrics_v2.fmxmlsnippet) | `portal_count` and `selected_row` merge-calculation objects named for targeted refresh. |

## Web Viewer Address Calculation

[`wv_main_persistent_address.calc.txt`](wv_main_persistent_address.calc.txt) contains the `wv_main` address calculation. It is calculation text for the Web Viewer setup dialog; it is neither a script-step snippet nor a layout-object snippet.

## Historical Repair Artifacts

[`2026-08-16-native-list-repair-install.md`](2026-08-16-native-list-repair-install.md), [`2026-08-18-portal-metrics-install.md`](2026-08-18-portal-metrics-install.md), and files whose names contain `ROWID_List`, unversioned portal metrics, or earlier portal variants record the route to the accepted portal implementation. They remain available as development evidence; they are not the current installation sequence.

All snippets depend on the [shared framework snippets](../../../shared/fmxmlsnippets/README.md). Static XML validation proves only the clipboard structure. Acceptance still requires installation and observation in the native FileMaker demo.
