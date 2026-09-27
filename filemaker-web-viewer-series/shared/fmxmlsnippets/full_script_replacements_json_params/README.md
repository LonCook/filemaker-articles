# Full Script Replacement Snippets
Use these instead of the earlier tiny caller/callee patch snippets. For each listed script: open the script in FileMaker, select all existing steps, paste the matching snippet, then run the smoke tests.
These replacements convert script parameters from the old `#()` / `ParamAssign` custom-function stack to native FileMaker JSON. Existing required-parameter `Exit Loop If [ $_error ]` guards are retained inside the full scripts.
## 01. `WV__Demo_Build_Context`
File: `01__WV__Demo_Build_Context__FULL_JSON_PARAMS.fmxmlsnippet.xml`
Changes:
- Perform Script parameter -> JSON for . webviewer . context . build ( -index ; -movie_id ; -genre_id ) : json

## 02. `WV__Demo_Load_Viewer`
File: `02__WV__Demo_Load_Viewer__FULL_JSON_PARAMS.fmxmlsnippet.xml`
Changes:
- Perform Script parameter -> JSON for . webviewer . load ( index ; -object_name )

## 03. `WV__Demo_Push_Context`
File: `03__WV__Demo_Push_Context__FULL_JSON_PARAMS.fmxmlsnippet.xml`
Changes:
- Perform Script parameter -> JSON for . webviewer . push context ( -object_name ; -context_json )

## 04. `. webviewer . load ( index ; -object_name )`
File: `04__webviewer___load___index____object_name__FULL_JSON_PARAMS.fmxmlsnippet.xml`
Changes:
- ParamAssign block -> native JSON parameter block
- Perform Script parameter -> JSON for . webviewer . render ( index ) : text

## 05. `. webviewer . render ( index ) : text`
File: `05__webviewer___render___index_____text__FULL_JSON_PARAMS.fmxmlsnippet.xml`
Changes:
- ParamAssign block -> native JSON parameter block
- Perform Script parameter -> JSON for library_json . ensure cache ( -force_rebuild ) : json

## 06. `. webviewer . push context ( -object_name ; -context_json )`
File: `06__webviewer___push_context____object_name____context_json__FULL_JSON_PARAMS.fmxmlsnippet.xml`
Changes:
- ParamAssign block -> native JSON parameter block

## 07. `. webviewer . ensure loaded . batch ( viewers_json ; -base_context_json ; -force_reload )`
File: `07__webviewer___ensure_loaded___batch___viewers_json____base_context_json____force_reload__FULL_JSON_PARAMS.fmxmlsnippet.xml`
Changes:
- ParamAssign block -> native JSON parameter block
- Perform Script parameter -> JSON for . webviewer . context . build ( -index ; -movie_id ; -genre_id ) : json
- Perform Script parameter -> JSON for . webviewer . ensure loaded ( index ; -object_name ; -context_json ; -movie_id ; -genre_id ; ... ) :

## 08. `. webviewer . ensure loaded ( index ; -object_name ; -context_json ; -movie_id ; -genre_id ; ... ) :`
File: `08__webviewer___ensure_loaded___index____object_name____context_json____movie_id____genre_id__FULL_JSON_PARAMS.fmxmlsnippet.xml`
Changes:
- ParamAssign block -> native JSON parameter block
- Perform Script parameter -> JSON for . webviewer . context . build ( -index ; -movie_id ; -genre_id ) : json
- Perform Script parameter -> JSON for . webviewer . load ( index ; -object_name )
- Perform Script parameter -> JSON for . webviewer . push context ( -object_name ; -context_json )

## 09. `. webviewer . context . build ( -index ; -movie_id ; -genre_id ) : json`
File: `09__webviewer___context___build____index____movie_id____genre_id_____json__FULL_JSON_PARAMS.fmxmlsnippet.xml`
Changes:
- ParamAssign block -> native JSON parameter block

## 10. `library_json . ensure cache ( -force_rebuild ) : json`
File: `10__library_json___ensure_cache____force_rebuild_____json__FULL_JSON_PARAMS.fmxmlsnippet.xml`
Changes:
- Exit Script result -> JSON object
- ParamAssign block -> native JSON parameter block
- Perform Script parameter -> JSON for library_json . build cache( version ) : json

## 11. `library_json . build cache( version ) : json`
File: `11__library_json___build_cache__version_____json__FULL_JSON_PARAMS.fmxmlsnippet.xml`
Changes:
- ParamAssign block -> native JSON parameter block

