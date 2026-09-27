# Article 4 native List View repair — manual installation

Authority checked: `../Flicks_WebViewer_Framework_04_HybridInterface.xml` and the fresh DDR generated 16 Aug 2026 at 17:57 PT.

The target is the existing `WV Framework - Hybrid` layout (layout 150), based on `MOVIE`, in List View. Its `wv_main` Web Viewer is in the Top Navigation part and its address is the record-independent calculation `JSONGetElement ( $$wv_url_map ; "wv_main" )`.

## Critical paste rule

For each script below, select all existing steps and **delete them first**. Confirm the script is empty, then paste the corresponding `FMObjectList` snippet. Pasting while the old steps remain selected has previously appended another complete script body; the fresh export shows 115 steps in `WV__Demo_Build_Context` and 409 steps in `WV__Demo_Handle_Action` for that reason.

## Installation order

1. Replace all steps in `WV__Demo_Build_Context` with `WV__Demo_Build_Context_Hybrid.fmxmlsnippet`.
2. Replace all steps in `WV__Demo_Apply_Hybrid_Context` with `WV__Demo_Apply_Hybrid_Context.fmxmlsnippet`.
3. Replace all steps in `WV__Demo_Handle_Action` with `WV__Demo_Handle_Action_Hybrid.fmxmlsnippet`.
4. Replace all steps in `WV__Demo_Select_Native_Row` with `WV__Demo_Select_Native_Row.fmxmlsnippet`.
5. Replace the `code` field on LIBRARY_CODE module 25 (`wv.platform.actions.js`) with `../source/2026-08-15-manual-module-gate/wv.platform.actions.js`.
6. Rebuild the library cache once, load the viewer once, then push context once.

Do not replace the Web Viewer loader. The fresh export confirms that `. webviewer . load ( index ; -object_name )` already persists the rendered URL in `$$wv_url_map`, and layout 150 already reads that stable URL.

## Expected interaction paths

- Web Viewer dot: one `WV__Demo_Handle_Action` call, one calculated native-record jump, one in-memory context patch, one context push.
- Native row: current `MOVIE` row becomes authoritative, one in-memory context patch, one context push.
- Rating band: one frozen exact-ID native find, at most one calculated native-record jump, one in-memory context patch, one context push.
- No interaction path calls `WV__Demo_Load_Viewer`, pauses, an OnTimer script, an `fmp://` callback, a portal, or the deleted stable layout.

## Static verification completed

- All four files are pasteable `<fmxmlsnippet type="FMObjectList">` step lists with no `<Script>` wrapper.
- If/Else/End If and Loop/End Loop structures are balanced.
- No snippet references `WV Framework - Hybrid Stable`, `portal.native_movies`, `WV__Demo_Load_Viewer`, Pause/Resume Script, Install OnTimer Script, or Open URL.
- Module 25 passes `node --check` and no longer waits for `WV_FM_PUSH` to unlock action dispatch.

