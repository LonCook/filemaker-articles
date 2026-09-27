#!/usr/bin/env python3
"""Build and validate the Article 4 portal repair from the current FileMaker XML."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET


HERE = Path(__file__).resolve().parent
ARTICLE_FOUR = HERE.parents[1]
DDR = ARTICLE_FOUR / "Flicks_WebViewer_Framework_04_HybridInterface_fmp12.xml"
OUTPUT = ARTICLE_FOUR / "fmxmlsnippets"
HELPERS_PATH = HERE / "build_hybrid_script_snippets.py"

spec = importlib.util.spec_from_file_location("hybrid_helpers", HELPERS_PATH)
helpers = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(helpers)

comment = helpers.comment
set_variable = helpers.set_variable
set_field_by_name = helpers.set_field_by_name
set_field = helpers.set_field
if_step = helpers.if_step
else_step = helpers.else_step
end_if = helpers.end_if
exit_script = helpers.exit_script
perform_script = helpers.perform_script
go_to_layout = helpers.go_to_layout

STAMP = "17 Aug 2026, 23hr53PT — Lon Cook — lon@portagebay.com"
RUN_STAMP = "18 Aug 2026, 00hr24PT — Lon Cook — lon@portagebay.com"
SQL_STAMP = "18 Aug 2026, 00hr37PT — Lon Cook — lon@portagebay.com"
RUN_FORCE_STAMP = "18 Aug 2026, 20hr13PT — Lon Cook — lon@portagebay.com"


def current_script_steps(root: ET.Element, name: str) -> list[ET.Element]:
    matches = []
    for script in root.iter("Script"):
        if script.get("name") != name:
            continue
        step_list = script.find("StepList")
        if step_list is not None and len(step_list):
            matches.append(step_list)
    if len(matches) != 1:
        raise ValueError(f"Expected one concrete script {name}, found {len(matches)}")
    return [deepcopy(step) for step in matches[0]]


def header_and_history(
    current: list[ET.Element],
    fixed_lines: list[str],
    modification: str,
    stamp: str = STAMP,
) -> tuple[list[ET.Element], list[str]]:
    old_header = []
    for step in current:
        if step.get("name") != "# (comment)":
            break
        old_header.append(step)
    old_history = [
        step.findtext("Text") or ""
        for step in old_header
        if (step.findtext("Text") or "").lstrip().startswith("Modified:")
    ]
    new_header = [comment(line) for line in fixed_lines]
    new_header.append(comment(f" Modified:\t{stamp} : {modification}"))
    new_header.extend(deepcopy(step) for step in old_header if (step.findtext("Text") or "").lstrip().startswith("Modified:"))
    if old_header and not (old_header[-1].findtext("Text") or "").strip():
        new_header.append(comment(""))
    return new_header, old_history


def set_error_capture_on() -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "86", "name": "Set Error Capture"})
    ET.SubElement(step, "Set", {"state": "True"})
    return step


def write_script(name: str, steps: list[ET.Element]) -> Path:
    root = ET.Element("fmxmlsnippet", {"type": "FMObjectList"})
    # DDR-only display text can become stale when structured step operands are
    # changed. The proven Article 4 paste shape omits these generated nodes.
    for step in steps:
        for parent in step.iter():
            for child in list(parent):
                if child.tag in {"StepText", "DisplayCalculation", "DisableStepCollapsed", "CurrentScript"}:
                    parent.remove(child)
    root.extend(steps)
    ET.indent(root, space="  ")
    path = OUTPUT / name
    path.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")
    return path


def build_context(ddr: ET.Element) -> tuple[list[ET.Element], list[str]]:
    current = current_script_steps(ddr, "WV__Demo_Build_Context")
    header, history = header_and_history(
        current,
        [
            " Purpose:\tBuild the hybrid rating context, portal relationship list, and acknowledged FileMaker-owned selection/band state.",
            " In:\t\t\tFOCUS::g_wv_demo_movie_id, FOCUS::g_wv_demo_genre_id, FOCUS::g_wv_rating_lo, FOCUS::g_wv_rating_hi",
            " Out:\t\tFOCUS::g_wv_module_index, FOCUS::g_wv_context_json, FOCUS::g_wv_status, SOLUTION__all::g_wv_hybrid_movie_ids; exits with raw context JSON.",
            " Anchor:\t\tSOLUTION__all on WV Framework - Hybrid. The portal is related through the private ordered movie-ID list.",
            " Calls:\t\tNone. FileMaker shapes the complete chart contract and the active portal scope without changing found sets or current records.",
        ],
        "replace native List View navigation with an ordered relationship-backed portal while keeping FileMaker-owned selection and filter state.",
    )
    header.insert(5, comment(
        f" Modified:\t{SQL_STAMP} : restore FileMaker-escaped SQL identifier quotes so the genre label and ranked rows evaluate correctly."
    ))
    sql = '''Let ( [
  base =
    "SELECT m.\\\"ID\\\", m.\\\"title_year_display\\\", m.\\\"year\\\", " &
    "r.\\\"global_rating\\\", r.\\\"global_rank_order\\\" " &
    "FROM \\\"MOVIE\\\" m " &
    "INNER JOIN \\\"MOVIE_GLOBAL_RATING\\\" r ON r.\\\"id_movie\\\" = m.\\\"ID\\\" " ;
  ordered = "ORDER BY r.\\\"global_rank_order\\\" ASC, m.\\\"title_year_display\\\" ASC"
] ;
  Case (
    IsEmpty ( $_genre_id ) ;
      ExecuteSQL ( base & ordered ; Char ( 29 ) ; Char ( 30 ) ) ;
    ExecuteSQL (
      base &
      "INNER JOIN \\\"MOVIE_GENRE\\\" mg ON mg.\\\"id_movie\\\" = m.\\\"ID\\\" " &
      "WHERE mg.\\\"id_genre\\\" = ? " & ordered ;
      Char ( 29 ) ; Char ( 30 ) ; $_genre_id
    )
  )
)'''
    rows_json = '''Let ( [
  row_sep = Char ( 30 ) ;
  field_sep = Char ( 29 ) ;
  row_list = Substitute ( $_rows_text ; row_sep ; ¶ ) ;
  row_count = Case ( IsEmpty ( $_rows_text ) ; 0 ; ValueCount ( row_list ) )
] ;
  While (
    [
      i = 0 ; n = row_count ; row = "" ; values = "" ;
      movie_id = "" ; display_title = "" ; year = "" ;
      rating = "" ; native_rank = "" ; rank = "" ; json = "[]"
    ] ;
    i < n ;
    [
      row = GetValue ( row_list ; i + 1 ) ;
      values = Substitute ( row ; field_sep ; ¶ ) ;
      movie_id = GetAsText ( GetValue ( values ; 1 ) ) ;
      display_title = GetAsText ( GetValue ( values ; 2 ) ) ;
      year = GetAsNumber ( GetValue ( values ; 3 ) ) ;
      rating = GetAsNumber ( GetValue ( values ; 4 ) ) ;
      native_rank = GetAsNumber ( GetValue ( values ; 5 ) ) ;
      rank = Case ( native_rank > 0 ; native_rank ; i + 1 ) ;
      json = JSONSetElement ( json
        ; [ "[" & i & "].movie_id" ; movie_id ; JSONString ]
        ; [ "[" & i & "].display_title" ; Case ( IsEmpty ( display_title ) ; movie_id ; display_title ) ; JSONString ]
        ; [ "[" & i & "].year" ; year ; JSONNumber ]
        ; [ "[" & i & "].rating" ; rating ; JSONNumber ]
        ; [ "[" & i & "].rank" ; rank ; JSONNumber ]
        ; [ "[" & i & "].order" ; i + 1 ; JSONNumber ]
      ) ;
      i = i + 1
    ] ;
    json
  )
)'''
    portal_ids = '''Let ( [
  n = ValueCount ( JSONListKeys ( $_rows_json ; "" ) )
] ;
  While (
    [ i = 0 ; ids = "" ; movie_id = "" ; rating = "" ; include = 0 ] ;
    i < n ;
    [
      movie_id = GetAsText ( JSONGetElement ( $_rows_json ; "[" & i & "].movie_id" ) ) ;
      rating = GetAsNumber ( JSONGetElement ( $_rows_json ; "[" & i & "].rating" ) ) ;
      include = not $_band_active or ( rating >= $_rating_lo and rating <= $_rating_hi ) ;
      ids = Case ( include and not IsEmpty ( movie_id ) ; List ( ids ; movie_id ) ; ids ) ;
      i = i + 1
    ] ;
    ids
  )
)'''
    mark_selected = '''Let ( [ n = ValueCount ( JSONListKeys ( $_rows_json ; "" ) ) ] ;
  While (
    [ i = 0 ; json = $_rows_json ] ;
    i < n ;
    [
      json = JSONSetElement ( json
        ; "[" & i & "].selected"
        ; not IsEmpty ( $_movie_id ) and
          GetAsText ( JSONGetElement ( json ; "[" & i & "].movie_id" ) ) = $_movie_id
        ; JSONBoolean
      ) ;
      i = i + 1
    ] ;
    json
  )
)'''
    context = '''JSONSetElement ( "{}"
  ; [ "__wv.page" ; $_index ; JSONNumber ]
  ; [ "__wv.page_name" ; "hybrid_rating" ; JSONString ]
  ; [ "__wv.source" ; "hybrid_rating_demo" ; JSONString ]
  ; [ "__wv.contract_version" ; 1 ; JSONNumber ]
  ; [ "__wv.ts" ; GetAsText ( Get ( CurrentHostTimestamp ) ) ; JSONString ]
  ; [ "ranked_view.filter.genre_id" ; $_genre_id ; JSONString ]
  ; [ "ranked_view.filter.label" ; $_filter_label ; JSONString ]
  ; [ "ranked_view.rating_band.active" ; $_band_active ; JSONBoolean ]
  ; [ "ranked_view.rating_band.rating_lo" ; Case ( $_band_active ; $_rating_lo ; "" ) ; Case ( $_band_active ; JSONNumber ; JSONNull ) ]
  ; [ "ranked_view.rating_band.rating_hi" ; Case ( $_band_active ; $_rating_hi ; "" ) ; Case ( $_band_active ; JSONNumber ; JSONNull ) ]
  ; [ "ranked_view.rating_band.label" ; $_band_label ; JSONString ]
  ; [ "ranked_view.selected_movie_id" ; $_movie_id ; JSONString ]
  ; [ "ranked_view.count" ; $_row_count ; JSONNumber ]
  ; [ "ranked_view.native_found_count" ; $_portal_count ; JSONNumber ]
  ; [ "ranked_view.current_record_number" ; $_selected_position ; JSONNumber ]
  ; [ "ranked_view.current_record_id" ; $_movie_id ; JSONString ]
  ; [ "ranked_view.empty_message" ; Case (
      IsEmpty ( $_genre_id ) ; "No ranked movies are available." ;
      "No ranked movies match " & $_filter_label & "."
    ) ; JSONString ]
  ; [ "ranked_view.rows" ; $_rows_json ; JSONArray ]
  ; [ "actions.count" ; GetAsNumber ( GetField ( "FOCUS::g_wv_action_count" ) ) ; JSONNumber ]
  ; [ "actions.last_type" ; GetAsText ( GetField ( "FOCUS::g_wv_action_type" ) ) ; JSONString ]
  ; [ "actions.status" ; Case (
      IsEmpty ( GetField ( "FOCUS::g_wv_action_status" ) ) ;
      "Waiting for a selection" ;
      GetAsText ( GetField ( "FOCUS::g_wv_action_status" ) )
    ) ; JSONString ]
)'''
    error_context = '''JSONSetElement ( "{}"
  ; [ "__wv.page" ; $_index ; JSONNumber ]
  ; [ "__wv.page_name" ; "hybrid_rating" ; JSONString ]
  ; [ "__wv.source" ; "hybrid_rating_demo" ; JSONString ]
  ; [ "__wv.contract_version" ; 1 ; JSONNumber ]
  ; [ "ranked_view.filter.genre_id" ; $_genre_id ; JSONString ]
  ; [ "ranked_view.filter.label" ; $_filter_label ; JSONString ]
  ; [ "ranked_view.rating_band.active" ; $_band_active ; JSONBoolean ]
  ; [ "ranked_view.rating_band.rating_lo" ; Case ( $_band_active ; $_rating_lo ; "" ) ; Case ( $_band_active ; JSONNumber ; JSONNull ) ]
  ; [ "ranked_view.rating_band.rating_hi" ; Case ( $_band_active ; $_rating_hi ; "" ) ; Case ( $_band_active ; JSONNumber ; JSONNull ) ]
  ; [ "ranked_view.rating_band.label" ; $_band_label ; JSONString ]
  ; [ "ranked_view.selected_movie_id" ; "" ; JSONString ]
  ; [ "ranked_view.count" ; 0 ; JSONNumber ]
  ; [ "ranked_view.native_found_count" ; 0 ; JSONNumber ]
  ; [ "ranked_view.current_record_number" ; 0 ; JSONNumber ]
  ; [ "ranked_view.current_record_id" ; "" ; JSONString ]
  ; [ "ranked_view.empty_message" ; "The ranked query failed. Inspect FOCUS::g_wv_status." ; JSONString ]
  ; [ "ranked_view.rows" ; "[]" ; JSONArray ]
  ; [ "error" ; $_rows_text ; JSONString ]
)'''
    steps = header + [
        set_error_capture_on(),
        set_variable("$_index", "43"),
        set_field_by_name("FOCUS::g_wv_module_index", "$_index"),
        if_step('Get ( LayoutName ) <> "WV Framework - Hybrid"'),
        go_to_layout("150", "WV Framework - Hybrid"),
        end_if(),
        set_variable("$_movie_id", 'GetAsText ( GetField ( "FOCUS::g_wv_demo_movie_id" ) )'),
        set_variable("$_genre_id", 'GetAsText ( GetField ( "FOCUS::g_wv_demo_genre_id" ) )'),
        set_variable("$_rating_lo_raw", 'GetAsText ( GetField ( "FOCUS::g_wv_rating_lo" ) )'),
        set_variable("$_rating_hi_raw", 'GetAsText ( GetField ( "FOCUS::g_wv_rating_hi" ) )'),
        set_variable("$_band_active", 'not IsEmpty ( $_rating_lo_raw ) and not IsEmpty ( $_rating_hi_raw ) and\nGetAsNumber ( $_rating_lo_raw ) <= GetAsNumber ( $_rating_hi_raw )'),
        set_variable("$_rating_lo", 'Case ( $_band_active ; GetAsNumber ( $_rating_lo_raw ) ; "" )'),
        set_variable("$_rating_hi", 'Case ( $_band_active ; GetAsNumber ( $_rating_hi_raw ) ; "" )'),
        set_variable("$_band_label", 'Case ( $_band_active ; "Ratings " & $_rating_lo & "–" & $_rating_hi ; "All ratings" )'),
        set_variable("$_filter_label", '''Case (
  IsEmpty ( $_genre_id ) ; "All Genres" ;
  Let ( [
    label = ExecuteSQL (
      "SELECT \\\"name\\\" FROM \\\"GENRE\\\" WHERE \\\"ID\\\" = ?" ;
      "" ; "" ; $_genre_id
    )
  ] ;
    Case ( Left ( label ; 1 ) = "?" or IsEmpty ( label ) ; $_genre_id ; label )
  )
)'''),
        set_variable("$_rows_text", sql),
        if_step('Left ( $_rows_text ; 1 ) = "?"'),
        set_field("SOLUTION__all", "23", "g_wv_hybrid_movie_ids", '""'),
        set_field_by_name("FOCUS::g_wv_demo_movie_id", '""'),
        set_variable("$_context_json", error_context),
        set_field_by_name("FOCUS::g_wv_context_json", "JSONFormatElements ( $_context_json )"),
        set_field_by_name("FOCUS::g_wv_status", '"Ranked context failed: " & $_rows_text'),
        exit_script("$_context_json"),
        end_if(),
        set_variable("$_rows_json", rows_json),
        set_variable("$_portal_movie_ids", portal_ids),
        set_variable("$_selected_valid", 'not IsEmpty ( $_movie_id ) and not IsEmpty ( FilterValues ( $_portal_movie_ids ; $_movie_id ) )'),
        set_variable("$_movie_id", 'Case ( IsEmpty ( $_portal_movie_ids ) ; "" ; $_selected_valid ; $_movie_id ; GetValue ( $_portal_movie_ids ; 1 ) )'),
        set_field("SOLUTION__all", "23", "g_wv_hybrid_movie_ids", "$_portal_movie_ids"),
        set_field_by_name("FOCUS::g_wv_demo_movie_id", "$_movie_id"),
        set_variable("$_rows_json", mark_selected),
        set_variable("$_row_count", 'ValueCount ( JSONListKeys ( $_rows_json ; "" ) )'),
        set_variable("$_portal_count", 'Case ( IsEmpty ( $_portal_movie_ids ) ; 0 ; ValueCount ( $_portal_movie_ids ) )'),
        set_variable("$_selected_position", 'Case ( IsEmpty ( $_movie_id ) ; 0 ;\nWhile (\n  [ i = 1 ; n = $_portal_count ; found = 0 ] ;\n  i <= n and not found ;\n  [ found = GetAsText ( GetValue ( $_portal_movie_ids ; i ) ) = $_movie_id ; i = i + 1 ] ;\n  Case ( found ; i - 1 ; 0 )\n) )'),
        set_variable("$_context_json", context),
        set_field_by_name("FOCUS::g_wv_context_json", "JSONFormatElements ( $_context_json )"),
        set_field_by_name("FOCUS::g_wv_status", '"Hybrid portal context built: " & $_row_count & " movies | " & $_band_label &\n  " | " & $_portal_count & " portal rows" &\n  If ( not IsEmpty ( $_movie_id ) ; " | selected row " & $_selected_position ; " | no portal selection" )'),
        set_variable("$$wv_hybrid_movie_rowid_map", '""'),
        set_variable("$$wv_hybrid_context_retry_count", '""'),
        exit_script("$_context_json"),
    ]
    return steps, history


def build_apply(ddr: ET.Element) -> tuple[list[ET.Element], list[str]]:
    current = current_script_steps(ddr, "WV__Demo_Apply_Hybrid_Context")
    header, history = header_and_history(
        current,
        [
            " Purpose:\tApply Article 4 portal selection/rating-band state and patch the resident hybrid context without rebuilding its SQL payload.",
            " In:\t\t\tFOCUS hybrid selection, rating band, action state, and existing page-43 context JSON.",
            " Out:\t\tFOCUS::g_wv_context_json and SOLUTION__all::g_wv_hybrid_movie_ids patched from authoritative FileMaker state; exits with raw context JSON.",
            " Anchor:\t\tSOLUTION__all on WV Framework - Hybrid.",
            " Calls:\t\tWV__Demo_Build_Context only when no valid page-43 context exists.",
            " Notes:\t\tNo find, found-set change, current-record navigation, viewer reload, or timer retry occurs on the interaction path.",
        ],
        "replace found-set and record navigation with one ordered portal match-list update and remove viewer-recovery timer retries.",
    )
    portal_ids = '''While (
  [ i = 0 ; ids = "" ; movie_id = "" ; rating = "" ; include = 0 ] ;
  i < $_row_count ;
  [
    movie_id = GetAsText ( JSONGetElement ( $_rows_json ; "[" & i & "].movie_id" ) ) ;
    rating = GetAsNumber ( JSONGetElement ( $_rows_json ; "[" & i & "].rating" ) ) ;
    include = not $_band_active or ( rating >= $_rating_lo and rating <= $_rating_hi ) ;
    ids = Case ( include and not IsEmpty ( movie_id ) ; List ( ids ; movie_id ) ; ids ) ;
    i = i + 1
  ] ;
  ids
)'''
    steps = header + [
        set_error_capture_on(),
        set_variable("$_type", 'GetAsText ( GetField ( "FOCUS::g_wv_action_type" ) )'),
        set_variable("$_context_json", 'GetAsText ( GetField ( "FOCUS::g_wv_context_json" ) )'),
        set_variable("$_context_invalid", '''IsEmpty ( $_context_json ) or JSONFormatElements ( $_context_json ) = "?" or
GetAsNumber ( JSONGetElement ( $_context_json ; "__wv.page" ) ) <> 43 or
EvaluationError ( JSONGetElementType ( $_context_json ; "ranked_view.rows" ) ) <> 0 or
JSONGetElementType ( $_context_json ; "ranked_view.rows" ) <> JSONArray or
GetAsText ( JSONGetElement ( $_context_json ; "ranked_view.filter.genre_id" ) ) <>
  GetAsText ( GetField ( "FOCUS::g_wv_demo_genre_id" ) )'''),
        if_step("$_context_invalid"),
        perform_script("480", "WV__Demo_Build_Context"),
        exit_script("GetAsText ( Get ( ScriptResult ) )"),
        end_if(),
        set_variable("$_rating_lo_raw", 'GetAsText ( GetField ( "FOCUS::g_wv_rating_lo" ) )'),
        set_variable("$_rating_hi_raw", 'GetAsText ( GetField ( "FOCUS::g_wv_rating_hi" ) )'),
        set_variable("$_band_active", 'not IsEmpty ( $_rating_lo_raw ) and not IsEmpty ( $_rating_hi_raw ) and\nGetAsNumber ( $_rating_lo_raw ) <= GetAsNumber ( $_rating_hi_raw )'),
        set_variable("$_rating_lo", 'Case ( $_band_active ; GetAsNumber ( $_rating_lo_raw ) ; "" )'),
        set_variable("$_rating_hi", 'Case ( $_band_active ; GetAsNumber ( $_rating_hi_raw ) ; "" )'),
        set_variable("$_band_label", 'Case ( $_band_active ; "Ratings " & $_rating_lo & "–" & $_rating_hi ; "All ratings" )'),
        set_variable("$_rows_json", 'JSONGetElement ( $_context_json ; "ranked_view.rows" )'),
        set_variable("$_row_count", 'ValueCount ( JSONListKeys ( $_rows_json ; "" ) )'),
        set_variable("$_portal_movie_ids", portal_ids),
        set_variable("$_selected_movie_id", 'GetAsText ( GetField ( "FOCUS::g_wv_demo_movie_id" ) )'),
        set_variable("$_selected_valid", 'not IsEmpty ( $_selected_movie_id ) and not IsEmpty ( FilterValues ( $_portal_movie_ids ; $_selected_movie_id ) )'),
        set_variable("$_selected_movie_id", 'Case ( IsEmpty ( $_portal_movie_ids ) ; "" ; $_selected_valid ; $_selected_movie_id ; GetValue ( $_portal_movie_ids ; 1 ) )'),
        set_field("SOLUTION__all", "23", "g_wv_hybrid_movie_ids", "$_portal_movie_ids"),
        set_field_by_name("FOCUS::g_wv_demo_movie_id", "$_selected_movie_id"),
        set_variable("$_rows_json", '''While (
  [ i = 0 ; json = $_rows_json ] ;
  i < $_row_count ;
  [
    row_id = GetAsText ( JSONGetElement ( json ; "[" & i & "].movie_id" ) ) ;
    json = JSONSetElement ( json
      ; [ "[" & i & "].selected" ; row_id = $_selected_movie_id ; JSONBoolean ]
    ) ;
    i = i + 1
  ] ;
  json
)'''),
        set_variable("$_portal_count", 'Case ( IsEmpty ( $_portal_movie_ids ) ; 0 ; ValueCount ( $_portal_movie_ids ) )'),
        set_variable("$_selected_position", 'Case ( IsEmpty ( $_selected_movie_id ) ; 0 ;\nWhile (\n  [ i = 1 ; n = $_portal_count ; found = 0 ] ;\n  i <= n and not found ;\n  [ found = GetAsText ( GetValue ( $_portal_movie_ids ; i ) ) = $_selected_movie_id ; i = i + 1 ] ;\n  Case ( found ; i - 1 ; 0 )\n) )'),
        set_variable("$_context_json", '''JSONSetElement ( $_context_json
  ; [ "__wv.ts" ; GetAsText ( Get ( CurrentHostTimestamp ) ) ; JSONString ]
  ; [ "ranked_view.rating_band.active" ; $_band_active ; JSONBoolean ]
  ; [ "ranked_view.rating_band.rating_lo" ; Case ( $_band_active ; $_rating_lo ; "" ) ; Case ( $_band_active ; JSONNumber ; JSONNull ) ]
  ; [ "ranked_view.rating_band.rating_hi" ; Case ( $_band_active ; $_rating_hi ; "" ) ; Case ( $_band_active ; JSONNumber ; JSONNull ) ]
  ; [ "ranked_view.rating_band.label" ; $_band_label ; JSONString ]
  ; [ "ranked_view.selected_movie_id" ; $_selected_movie_id ; JSONString ]
  ; [ "ranked_view.native_found_count" ; $_portal_count ; JSONNumber ]
  ; [ "ranked_view.current_record_number" ; $_selected_position ; JSONNumber ]
  ; [ "ranked_view.current_record_id" ; $_selected_movie_id ; JSONString ]
  ; [ "ranked_view.rows" ; $_rows_json ; JSONArray ]
  ; [ "actions.count" ; GetAsNumber ( GetField ( "FOCUS::g_wv_action_count" ) ) ; JSONNumber ]
  ; [ "actions.last_type" ; $_type ; JSONString ]
  ; [ "actions.status" ; GetAsText ( GetField ( "FOCUS::g_wv_action_status" ) ) ; JSONString ]
)'''),
        set_field_by_name("FOCUS::g_wv_context_json", "JSONFormatElements ( $_context_json )"),
        set_field_by_name("FOCUS::g_wv_status", '"Hybrid portal context patched: " & $_portal_count & " rows | " & $_band_label &\n  If ( not IsEmpty ( $_selected_movie_id ) ; " | selected row " & $_selected_position ; " | no portal selection" )'),
        set_variable("$$wv_hybrid_context_retry_count", '""'),
        exit_script("$_context_json"),
    ]
    return steps, history


def variable_name(step: ET.Element) -> str:
    return step.findtext("Name") or ""


def calc_node(step: ET.Element) -> ET.Element | None:
    return step.find(".//Calculation")


def matching_end_if(steps: list[ET.Element], start: int) -> int:
    depth = 0
    for i in range(start, len(steps)):
        if steps[i].get("name") == "If":
            depth += 1
        elif steps[i].get("name") == "End If":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("Unbalanced If")


def build_handler(ddr: ET.Element) -> tuple[list[ET.Element], list[str]]:
    current = current_script_steps(ddr, "WV__Demo_Handle_Action")
    header, history = header_and_history(
        current,
        [
            " Purpose:\tReceive and validate inherited or hybrid action envelopes, apply FileMaker-owned state, and push acknowledgement context.",
            " In:\t\t\tGet ( ScriptParameter ) as raw JSON.",
            " Out:\t\tJSON status object.",
            " Anchor:\t\tSOLUTION__all on WV Framework - Hybrid for hybrid actions; inherited actions retain their original target layout.",
            " Calls:\t\tWV__Demo_Apply_Hybrid_Context, WV__Demo_Build_Context, WV__Demo_Push_Context.",
        ],
        "route hybrid actions through portal globals only, with no found-set/current-record navigation or viewer-recovery timer.",
    )
    body = [deepcopy(s) for s in current if s.get("name") != "# (comment)"]
    target = next(s for s in body if variable_name(s) == "$_target_record")
    target.find("Name").text = "$_hybrid_selection_available"
    calc_node(target).text = '''Case ( not $_hybrid_select_action ; True ;
Let ( [
  context_json = GetAsText ( GetField ( "FOCUS::g_wv_context_json" ) ) ;
  rows = JSONGetElement ( context_json ; "ranked_view.rows" ) ;
  n = ValueCount ( JSONListKeys ( rows ; "" ) )
] ;
  While (
    [ i = 0 ; found = 0 ] ;
    i < n and not found ;
    [
      found = GetAsText ( JSONGetElement ( rows ; "[" & i & "].movie_id" ) ) = $_payload_movie_id ;
      i = i + 1
    ] ;
    found
  )
) )'''
    invalid = next(s for s in body if variable_name(s) == "$_invalid_hybrid_selection")
    calc_node(invalid).text = '''Case ( not $_hybrid_select_action ; False ;
Let ( [
  payload_type_error = EvaluationError ( JSONGetElementType ( $_raw ; "payload.movie_id" ) )
] ;
  payload_type_error <> 0 or
  JSONGetElementType ( $_raw ; "payload.movie_id" ) <> JSONString or
  IsEmpty ( $_payload_movie_id ) or
  not $_hybrid_selection_available
) )'''
    for step in body:
        if step.get("name") == "Set Field By Name":
            result = step.find("Result/Calculation")
            if result is not None and result.text == '"Rejected hybrid selection: the movie id is not available in the current FileMaker found set."':
                result.text = '"Rejected hybrid selection: the movie id is not available in the authoritative hybrid context."'
    select_if = next(i for i,s in enumerate(body) if s.get("name") == "If" and (calc_node(s).text or "").strip() == "$_hybrid_select_action")
    select_end = matching_end_if(body, select_if)
    body[select_if:select_end + 1] = [
        if_step("$_hybrid_select_action"),
        set_field_by_name("FOCUS::g_wv_demo_movie_id", "$_payload_movie_id"),
        end_if(),
    ]
    status = next(s for s in body if variable_name(s) == "$_status")
    calc_node(status).text = '''Case (
  $_ranked_action ; "Selected native movie " & GetAsText ( MOVIE::ID ) ;
  $_hybrid_select_action ; "Selected hybrid movie " & $_payload_movie_id & " in native portal" ;
  $_hybrid_set_band_action ; "Applied portal rating band " & $_payload_rating_lo & "–" & $_payload_rating_hi ;
  $_hybrid_clear_band_action ; "Cleared portal rating band" ;
  "Handled " & $_type
)'''
    timer_if = next(i for i,s in enumerate(body) if s.get("name") == "If" and calc_node(s) is not None and (calc_node(s).text or "").strip() == "$_hybrid_set_band_action or $_hybrid_clear_band_action")
    timer_end = matching_end_if(body, timer_if)
    del body[timer_if:timer_end + 1]
    return header + body, history


def build_select(ddr: ET.Element) -> tuple[list[ET.Element], list[str]]:
    current = current_script_steps(ddr, "WV__Demo_Select_Native_Row")
    header, history = header_and_history(
        current,
        [
            " Purpose:\tAcknowledge a clicked native portal row as FileMaker-owned hybrid selection and refresh both surfaces.",
            " In:\t\t\tGet ( ScriptParameter ) as stable MOVIE::ID; falls back to the current MOVIE_GLOBAL_RATING portal row.",
            " Out:\t\tJSON status object.",
            " Anchor:\t\tSOLUTION__all on WV Framework - Hybrid; button context is MOVIE_GLOBAL_RATING.",
            " Calls:\t\tWV__Demo_Apply_Hybrid_Context, WV__Demo_Push_Context.",
        ],
        "repurpose native-row selection for the relationship-backed portal without changing the layout current record.",
    )
    steps = header + [
        set_error_capture_on(),
        set_variable("$_movie_id", '''Let ( [ p = GetAsText ( Get ( ScriptParameter ) ) ] ;
  Case ( not IsEmpty ( p ) ; p ; GetAsText ( MOVIE_GLOBAL_RATING::id_movie ) )
)'''),
        set_variable("$_portal_movie_ids", 'GetAsText ( SOLUTION__all::g_wv_hybrid_movie_ids )'),
        set_variable("$_movie_valid", 'not IsEmpty ( $_movie_id ) and not IsEmpty ( FilterValues ( $_portal_movie_ids ; $_movie_id ) )'),
        if_step("not $_movie_valid"),
        exit_script('JSONSetElement ( "{}"\n  ; [ "ok" ; 0 ; JSONBoolean ]\n  ; [ "error" ; "no_portal_movie" ; JSONString ]\n  ; [ "movie_id" ; $_movie_id ; JSONString ]\n)'),
        end_if(),
        set_variable("$_count", 'GetAsNumber ( GetField ( "FOCUS::g_wv_action_count" ) ) + 1'),
        set_variable("$_status", '"Selected native portal movie " & $_movie_id'),
        set_field_by_name("FOCUS::g_wv_demo_movie_id", "$_movie_id"),
        set_field_by_name("FOCUS::g_wv_action_json", '''JSONFormatElements ( JSONSetElement ( "{}"
  ; [ "__wv_action.version" ; 1 ; JSONNumber ]
  ; [ "__wv_action.source" ; "filemaker.native.hybrid_portal" ; JSONString ]
  ; [ "__wv_action.page" ; 43 ; JSONNumber ]
  ; [ "type" ; "hybrid.select_movie" ; JSONString ]
  ; [ "payload.movie_id" ; $_movie_id ; JSONString ]
) )'''),
        set_field_by_name("FOCUS::g_wv_action_type", '"hybrid.select_movie"'),
        set_field_by_name("FOCUS::g_wv_action_count", "$_count"),
        set_field_by_name("FOCUS::g_wv_action_status", "$_status"),
        perform_script("502", "WV__Demo_Apply_Hybrid_Context"),
        perform_script("482", "WV__Demo_Push_Context"),
        set_variable("$_push_result", "GetAsText ( Get ( ScriptResult ) )"),
        exit_script('JSONSetElement ( "{}"\n  ; [ "ok" ; 1 ; JSONBoolean ]\n  ; [ "type" ; "hybrid.select_movie" ; JSONString ]\n  ; [ "selected_movie_id" ; $_movie_id ; JSONString ]\n  ; [ "push_result" ; $_push_result ; JSONString ]\n)'),
    ]
    return steps, history


def build_run(ddr: ET.Element) -> tuple[list[ET.Element], list[str]]:
    current = current_script_steps(ddr, "WV__Demo_Run_All")
    header, history = header_and_history(
        current,
        [
            " Purpose:\tBuild the current demo context, then ensure the builder-selected Web Viewer module is loaded with that context.",
            " In:\t\t\tThe current demo builder inputs; WV__Demo_Build_Context owns FOCUS::g_wv_module_index.",
            " Out:\t\tFOCUS::g_wv_context_json, FOCUS::g_wv_status; exits with the ensure-loaded result.",
            " Calls:\t\tWV__Demo_Build_Context; . webviewer . ensure loaded ( index ; -object_name ; -context_json ; -movie_id ; -genre_id ; ... )",
        ],
        "remove the inherited hardcoded module-41 loader index and honor the current builder's authoritative module index.",
        RUN_STAMP,
    )
    header.insert(4, comment(
        f" Modified:\t{RUN_FORCE_STAMP} : make the explicit Run command force-load the selected module before pushing context so stale loaded-state cannot leave the viewer blank."
    ))
    body = [deepcopy(s) for s in current if s.get("name") != "# (comment)"]
    build_index = next(
        i for i, step in enumerate(body)
        if step.get("name") == "Perform Script"
        and step.find("Script") is not None
        and step.find("Script").get("name") == "WV__Demo_Build_Context"
    )
    body.insert(
        build_index + 1,
        set_variable(
            "$_index",
            'Let ( [ raw = GetField ( "FOCUS::g_wv_module_index" ) ] ;\n  Case ( IsEmpty ( raw ) ; 43 ; GetAsNumber ( raw ) )\n)',
        ),
    )
    ensure = next(
        step for step in body
        if step.get("name") == "Perform Script"
        and step.find("Script") is not None
        and (step.find("Script").get("name") or "").startswith(". webviewer . ensure loaded")
    )
    calc = ensure.find("Calculation")
    assert calc is not None and calc.text is not None
    if calc.text.count('; [ "index" ; 41 ; JSONNumber ]') != 1:
        raise ValueError("Run All no longer contains the reviewed hardcoded module-41 index")
    calc.text = calc.text.replace(
        '; [ "index" ; 41 ; JSONNumber ]',
        '; [ "index" ; $_index ; JSONNumber ]',
        1,
    )
    if calc.text.count('; [ "force_reload" ; 0 ; JSONNumber ]') != 1:
        raise ValueError("Run All no longer contains the reviewed non-forced load argument")
    calc.text = calc.text.replace(
        '; [ "force_reload" ; 0 ; JSONNumber ]',
        '; [ "force_reload" ; 1 ; JSONNumber ]',
        1,
    )
    status = next(step for step in body if variable_name(step) == "$_status")
    calc_node(status).text = '"Run module " & $_index & ": " & JSONGetElement ( $_ensure_result ; "status" ) &\n  " — " & JSONGetElement ( $_ensure_result ; "message" ) &\n  " — did_reload=" & JSONGetElement ( $_ensure_result ; "did_reload" )'
    return header + body, history


def set_bounds(obj: ET.Element, top: float, left: float, bottom: float, right: float) -> None:
    bounds = obj.find("Bounds")
    assert bounds is not None
    for key, value in (("top",top),("left",left),("bottom",bottom),("right",right)):
        bounds.set(key, f"{value:.7f}")


def set_text(obj: ET.Element, text: str) -> None:
    for node in obj.findall(".//CharacterStyleVector/Style/Data") + obj.findall(".//ParagraphStyleVector/Style/Data"):
        node.text = text


def make_field(template: ET.Element, key: int, bounds: tuple[float,float,float,float], table: str, field_id: str, name: str) -> ET.Element:
    obj = deepcopy(template)
    obj.set("key",str(key)); obj.set("LabelKey","0")
    set_bounds(obj,*bounds)
    fo=obj.find("FieldObj"); assert fo is not None
    fo.set("inputMode","0"); fo.set("quickFind","0")
    fo.find("Name").text=f"{table}::{name}"
    d=fo.find("DDRInfo/Field"); assert d is not None
    d.attrib.update({"table":table,"id":field_id,"name":name,"repetition":"1","maxRepetition":"1"})
    return obj


def make_label(template: ET.Element, key: int, bounds: tuple[float,float,float,float], text: str) -> ET.Element:
    obj=deepcopy(template); obj.set("key",str(key)); obj.set("LabelKey","0")
    set_bounds(obj,*bounds); set_text(obj,text)
    return obj


def build_portal(ddr: ET.Element) -> Path:
    modules = next(l for l in ddr.iter("Layout") if l.get("id")=="115")
    portal_template = next(o for o in modules.findall("Object") if o.get("type")=="Portal")
    portal = deepcopy(portal_template)
    portal.attrib.update({"key":"601","LabelKey":"0","name":"portal.hybrid_movies","flags":"-2147483648","rotation":"0"})
    set_bounds(portal,550,12,878,1273)
    po=portal.find("PortalObj"); assert po is not None
    po.attrib.update({"portalFlags":"277","numOfRows":"10","initialRow":"1"})
    po.find("TableAliasKey").text="MOVIE_GLOBAL_RATING"
    for child in list(po):
        if child.tag=="Object": po.remove(child)
    fl=po.find("FieldList"); assert fl is not None
    fl.clear()
    for table,fid,name in (
        ("MOVIE_GLOBAL_RATING","21","global_rank_order"),
        ("MOVIE_GLOBAL_RATING","16","global_rating"),
        ("MOVIE_GLOBAL_RATING","15","id_movie"),
        ("hybrid.MOVIE","24","year"),
        ("hybrid.TITLE~display","13","title"),
    ):
        ET.SubElement(fl,"Field",{"table":table,"id":fid,"name":name})
    styles=po.find("Styles"); assert styles is not None
    styles.clear(); css=ET.SubElement(styles,"LocalCSS")
    css.text='''self:normal .self
{
  background-color: #151515;
  border-bottom-color: #2B2B2B;
  border-bottom-style: solid;
  border-bottom-width: 1px;
}'''
    field_template=next(o for o in portal_template.findall("PortalObj/Object") if o.get("type")=="Field")
    label_template=next(o for o in next(l for l in ddr.iter("Layout") if l.get("id")=="150").findall("Object") if o.get("type")=="Text")
    fields=[
        make_field(field_template,602,(551,24,582,76),"MOVIE_GLOBAL_RATING","21","global_rank_order"),
        make_field(field_template,603,(551,86,582,646),"hybrid.TITLE~display","13","title"),
        make_field(field_template,604,(551,656,582,736),"hybrid.MOVIE","24","year"),
        make_field(field_template,605,(551,786,582,906),"MOVIE_GLOBAL_RATING","16","global_rating"),
        make_field(field_template,606,(551,936,582,1258),"MOVIE_GLOBAL_RATING","15","id_movie"),
    ]
    for f in fields: po.append(f)
    button_template=next(o for o in portal_template.findall("PortalObj/Object") if o.get("type")=="Button")
    button=deepcopy(button_template)
    button.attrib.update({"key":"607","LabelKey":"0","name":"button.hybrid_portal_row","flags":"65536","rotation":"0"})
    set_bounds(button,551,13,582,1272); set_text(button,"")
    for cf in list(button.findall("ConditionalFormatting")): button.remove(cf)
    cf=ET.Element("ConditionalFormatting")
    item=ET.SubElement(cf,"Item",{"id":"0","flags":"5"})
    condition=ET.SubElement(item,"Condition",{"op":"0"})
    calc=ET.SubElement(condition,"Calculation")
    calc.text='GetAsText ( MOVIE_GLOBAL_RATING::id_movie ) = GetAsText ( FOCUS::g_wv_demo_movie_id )'
    ET.SubElement(condition,"RangeBegin"); ET.SubElement(condition,"RangeEnd")
    fmt=ET.SubElement(item,"Format"); st=ET.SubElement(fmt,"Styles"); lc=ET.SubElement(st,"LocalCSS")
    lc.text='''self:normal .self
{
  background-color: rgba(78%,63%,8%,0.38);
  border-left-color: #D5AA18;
  border-left-style: solid;
  border-left-width: 4px;
}'''
    button.insert(0,cf)
    text_obj=button.find("TextObj"); assert text_obj is not None
    bst=text_obj.find("Styles"); assert bst is not None
    bst.clear(); lc=ET.SubElement(bst,"LocalCSS")
    lc.text='''self:normal .self
{
  background-color: rgba(0%,0%,0%,0);
  border-style: none;
}
self:hover .self
{
  background-color: rgba(78%,63%,8%,0.14);
  border-style: none;
}
self:pressed .self
{
  background-color: rgba(78%,63%,8%,0.24);
  border-style: none;
}'''
    bo=button.find("ButtonObj"); assert bo is not None
    bo.clear(); bo.attrib.update({"buttonFlags":"0","iconSize":"12","displayType":"0"})
    step=ET.SubElement(bo,"Step",{"enable":"True","id":"1","name":"Perform Script"})
    c=ET.SubElement(step,"Calculation"); c.text='GetAsText ( MOVIE_GLOBAL_RATING::id_movie )'
    ET.SubElement(step,"Script",{"id":"501","name":"WV__Demo_Select_Native_Row"})
    po.append(button)
    hybrid=next(l for l in ddr.iter("Layout") if l.get("id")=="150")
    text_template=next(o for o in hybrid.findall("Object") if o.get("type")=="Text")
    labels=[
        make_label(text_template,608,(524,24,546,76),"RANK"),
        make_label(text_template,609,(524,86,546,646),"TITLE"),
        make_label(text_template,610,(524,656,546,736),"YEAR"),
        make_label(text_template,611,(524,786,546,906),"RATING"),
        make_label(text_template,612,(524,936,546,1258),"STABLE MOVIE ID"),
    ]
    snippet=ET.Element("fmxmlsnippet",{"type":"LayoutObjectList"})
    layout=ET.SubElement(snippet,"Layout",{
        "enclosingRectTop":"524.0000000","enclosingRectLeft":"12.0000000",
        "enclosingRectBottom":"878.0000000","enclosingRectRight":"1273.0000000",
    })
    layout.extend(labels); layout.append(portal)
    ET.indent(snippet,space="  ")
    path=OUTPUT/"WV_Framework_Hybrid_Portal_Objects.fmxmlsnippet"
    path.write_text(ET.tostring(snippet,encoding="unicode")+"\n",encoding="utf-8")
    return path


def validate_script(path: Path, old_history: list[str], forbidden: set[str]) -> None:
    root=ET.parse(path).getroot()
    assert root.tag=="fmxmlsnippet" and root.get("type")=="FMObjectList"
    assert all(child.tag=="Step" for child in root)
    assert not root.findall(".//Script/StepList")
    history=[s.findtext("Text") or "" for s in root if s.get("name")=="# (comment)" and (s.findtext("Text") or "").lstrip().startswith("Modified:")]
    assert len(history) > len(old_history)
    assert history[-len(old_history):]==old_history
    names={s.get("name") for s in root}
    assert not (names & forbidden), (path,names & forbidden)
    depth=0
    for s in root:
        if s.get("name")=="If": depth+=1
        elif s.get("name")=="End If": depth-=1
        assert depth>=0
    assert depth==0
    text=path.read_text(encoding="utf-8")
    assert "≠" not in text


def main() -> None:
    ddr=ET.parse(DDR).getroot()
    builds=[
        ("WV__Demo_Build_Context_Portal.fmxmlsnippet",build_context,{"Enter Find Mode","Perform Find","New Record/Request","Go to List of Records","Go to Record/Request/Page"}),
        ("WV__Demo_Apply_Hybrid_Context_Portal.fmxmlsnippet",build_apply,{"Enter Find Mode","Perform Find","New Record/Request","Go to List of Records","Go to Record/Request/Page","Install OnTimer Script"}),
        ("WV__Demo_Handle_Action_Portal.fmxmlsnippet",build_handler,set()),
        ("WV__Demo_Select_Native_Row_Portal.fmxmlsnippet",build_select,{"Enter Find Mode","Perform Find","New Record/Request","Go to List of Records","Go to Record/Request/Page","Install OnTimer Script"}),
        ("WV__Demo_Run_All_Portal.fmxmlsnippet",build_run,set()),
    ]
    paths=[]
    for filename,builder,forbidden in builds:
        steps,history=builder(ddr)
        path=write_script(filename,steps)
        validate_script(path,history,forbidden)
        paths.append(path)
    build_v2 = OUTPUT / "WV__Demo_Build_Context_Portal_v2.fmxmlsnippet"
    build_v2.write_text(paths[0].read_text(encoding="utf-8"), encoding="utf-8")
    build_text = build_v2.read_text(encoding="utf-8")
    assert 'm.\\"ID\\"' in build_text
    assert 'FROM \\"MOVIE\\" m' in build_text
    assert 'SELECT \\"name\\" FROM \\"GENRE\\"' in build_text
    run_v2 = OUTPUT / "WV__Demo_Run_All_Portal_v2.fmxmlsnippet"
    run_v2.write_text(paths[4].read_text(encoding="utf-8"), encoding="utf-8")
    run_v2_text = run_v2.read_text(encoding="utf-8")
    assert '"force_reload" ; 1 ; JSONNumber' in run_v2_text
    assert '"force_reload" ; 0 ; JSONNumber' not in run_v2_text
    handler=ET.parse(paths[2]).getroot()
    hybrid_block=False
    for step in handler:
        calc=calc_node(step)
        text="" if calc is None else (calc.text or "")
        if "$_hybrid_select_action" in text or "$_hybrid_set_band_action" in text or "$_hybrid_clear_band_action" in text:
            if step.get("name") in {"Go to Record/Request/Page","Go to List of Records","Enter Find Mode","Perform Find","Install OnTimer Script"}:
                hybrid_block=True
    assert not hybrid_block
    run_root = ET.parse(paths[4]).getroot()
    run_text = paths[4].read_text(encoding="utf-8")
    assert '"index" ; 41' not in run_text
    assert '"index" ; $_index ; JSONNumber' in run_text
    assert any(step.findtext("Name") == "$_index" for step in run_root)
    portal=build_portal(ddr)
    proot=ET.parse(portal).getroot()
    assert proot.get("type")=="LayoutObjectList"
    pobj=proot.find('.//Object[@name="portal.hybrid_movies"]')
    assert pobj is not None and pobj.find("PortalObj/TableAliasKey").text=="MOVIE_GLOBAL_RATING"
    assert pobj.find('.//Script[@id="501"]') is not None
    ptext=portal.read_text(encoding="utf-8")
    for token in ("SOLUTION__all", "MOVIE_GLOBAL_RATING", "hybrid.MOVIE", "hybrid.TITLE~display"):
        if token=="SOLUTION__all":
            continue
        assert token in ptext
    assert "≠" not in ptext
    for path in paths+[build_v2,run_v2,portal]: print(path)
    print("Static validation passed: current histories preserved; step-only script snippets; no hybrid find/list/current-record/timer operations; verified portal IDs and row action.")


if __name__=="__main__":
    main()
