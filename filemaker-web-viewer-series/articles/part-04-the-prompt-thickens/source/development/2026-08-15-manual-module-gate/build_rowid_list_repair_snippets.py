#!/usr/bin/env python3
"""Build and statically validate the Article 4 ROWID/Go-to-List script replacements."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import xml.etree.ElementTree as ET


ARTICLE_FOUR = Path(__file__).resolve().parents[2]
SNIPPET_DIR = ARTICLE_FOUR / "fmxmlsnippets"

BUILD_SOURCE = SNIPPET_DIR / "WV__Demo_Build_Context_Hybrid.fmxmlsnippet"
APPLY_SOURCE = SNIPPET_DIR / "WV__Demo_Apply_Hybrid_Context.fmxmlsnippet"
HANDLER_SOURCE = SNIPPET_DIR / "WV__Demo_Handle_Action_Hybrid.fmxmlsnippet"
NATIVE_ROW_SOURCE = SNIPPET_DIR / "WV__Demo_Select_Native_Row.fmxmlsnippet"

BUILD_OUTPUT = SNIPPET_DIR / "WV__Demo_Build_Context_ROWID_List.fmxmlsnippet"
APPLY_OUTPUT = SNIPPET_DIR / "WV__Demo_Apply_Hybrid_Context_ROWID_List.fmxmlsnippet"

EXPECTED_SOURCE_HASHES = {
    BUILD_SOURCE: "48478d4176f4ae37b54c7aea0dded98e64b3b3b089d1ad2673c5182318265d70",
    APPLY_SOURCE: "60185b33bf33a4164e6a768e43357647e963f91562e93e88de2b2b828b814fb4",
    HANDLER_SOURCE: "8f327dd439cab154983f6437777d1144295d695de9273261f89934bc710e6ba5",
    NATIVE_ROW_SOURCE: "ee8257f9d2c11cf9516ca0f0c1d40af7ef80ee747bb36846145114af75ad572c",
}

NEW_BUILD_HISTORY = (
    " Modified:\t16 Aug 2026, 19hr24PT — Lon Cook — lon@portagebay.com : "
    "replace multi-request ID finds with one private ROWID-backed Go to List of Records operation."
)
NEW_APPLY_HISTORY = (
    " Modified:\t16 Aug 2026, 19hr24PT — Lon Cook — lon@portagebay.com : "
    "apply rating-band found sets with one private ROWID-backed Go to List of Records operation."
)

PRIVATE_ROWS_CALC = r'''Let ( [
  row_sep = Char ( 30 ) ;
  field_sep = Char ( 29 ) ;
  row_list = Substitute ( $_rows_text ; row_sep ; ¶ ) ;
  n = Case ( IsEmpty ( $_rows_text ) ; 0 ; ValueCount ( row_list ) )
] ;
  While (
    [
      i = 1 ; j = 0 ; rows = "[]" ; values = "" ;
      movie_id = "" ; rating = "" ; record_id = "" ; include = 0
    ] ;
    i <= n ;
    [
      values = Substitute ( GetValue ( row_list ; i ) ; field_sep ; ¶ ) ;
      movie_id = GetAsText ( GetValue ( values ; 1 ) ) ;
      rating = GetAsNumber ( GetValue ( values ; 4 ) ) ;
      record_id = GetAsText ( GetValue ( values ; 6 ) ) ;
      include = not IsEmpty ( record_id ) ;
      rows = Case (
        include ;
        JSONSetElement ( rows
          ; [ "[" & j & "].movie_id" ; movie_id ; JSONString ]
          ; [ "[" & j & "].rating" ; rating ; JSONNumber ]
          ; [ "[" & j & "].record_id" ; record_id ; JSONString ]
        ) ;
        rows
      ) ;
      j = j + include ;
      i = i + 1
    ] ;
    rows
  )
)'''

PRIVATE_MAP_CALC = r'''JSONSetElement ( "{}"
  ; [ "genre_id" ; $_genre_id ; JSONString ]
  ; [ "rows" ; $_private_rows ; JSONArray ]
)'''

RECORD_IDS_CALC = r'''Let ( [
  rows = JSONGetElement ( $$wv_hybrid_movie_rowid_map ; "rows" ) ;
  n = ValueCount ( JSONListKeys ( rows ; "" ) )
] ;
  While (
    [ i = 0 ; ids = "" ; rating = "" ; record_id = "" ; include = 0 ] ;
    i < n ;
    [
      rating = GetAsNumber ( JSONGetElement ( rows ; "[" & i & "].rating" ) ) ;
      record_id = GetAsText ( JSONGetElement ( rows ; "[" & i & "].record_id" ) ) ;
      include = not $_band_active or ( rating >= $_rating_lo and rating <= $_rating_hi ) ;
      ids = Case ( include and not IsEmpty ( record_id ) ; List ( ids ; record_id ) ; ids ) ;
      i = i + 1
    ] ;
    ids
  )
)'''

CONTEXT_INVALID_CALC = r'''IsEmpty ( $_context_json ) or JSONFormatElements ( $_context_json ) = "?" or
GetAsNumber ( JSONGetElement ( $_context_json ; "__wv.page" ) ) <> 43 or
EvaluationError ( JSONGetElementType ( $_context_json ; "ranked_view.rows" ) ) <> 0 or
JSONGetElementType ( $_context_json ; "ranked_view.rows" ) <> JSONArray or
IsEmpty ( $$wv_hybrid_movie_rowid_map ) or
EvaluationError ( JSONGetElementType ( $$wv_hybrid_movie_rowid_map ; "rows" ) ) <> 0 or
JSONGetElementType ( $$wv_hybrid_movie_rowid_map ; "rows" ) <> JSONArray or
GetAsText ( JSONGetElement ( $$wv_hybrid_movie_rowid_map ; "genre_id" ) ) <>
  GetAsText ( GetField ( "FOCUS::g_wv_demo_genre_id" ) ) or
ValueCount ( JSONListKeys ( $$wv_hybrid_movie_rowid_map ; "rows" ) ) <>
  ValueCount ( JSONListKeys ( $_context_json ; "ranked_view.rows" ) )'''


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def parse(path: Path) -> ET.Element:
    root = ET.parse(path).getroot()
    if root.tag != "fmxmlsnippet" or root.get("type") != "FMObjectList":
        raise AssertionError(f"Unexpected FMXML root in {path.name}")
    if any(child.tag != "Step" for child in root):
        raise AssertionError(f"Non-Step child in {path.name}")
    return root


def calculation(step: ET.Element) -> ET.Element | None:
    return step.find(".//Calculation")


def variable_name(step: ET.Element) -> str:
    return step.findtext("Name", default="")


def find_variable(root: ET.Element, name: str) -> tuple[int, ET.Element]:
    for index, step in enumerate(root):
        if step.get("name") == "Set Variable" and variable_name(step) == name:
            return index, step
    raise AssertionError(f"Variable step not found: {name}")


def find_first_step(root: ET.Element, name: str, start: int = 0) -> int:
    for index in range(start, len(root)):
        if root[index].get("name") == name:
            return index
    raise AssertionError(f"Step not found: {name}")


def matching_end_if(root: ET.Element, if_index: int) -> int:
    depth = 0
    for index in range(if_index, len(root)):
        step_id = root[index].get("id")
        if step_id == "68":
            depth += 1
        elif step_id == "70":
            depth -= 1
            if depth == 0:
                return index
    raise AssertionError(f"End If not found for step {if_index}")


def comment(text: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "89", "name": "# (comment)"})
    ET.SubElement(step, "Text").text = text
    return step


def set_variable(name: str, calc_text: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "141", "name": "Set Variable"})
    value = ET.SubElement(step, "Value")
    ET.SubElement(value, "Calculation").text = calc_text
    repetition = ET.SubElement(step, "Repetition")
    ET.SubElement(repetition, "Calculation").text = "1"
    ET.SubElement(step, "Name").text = name
    return step


def freeze_window() -> ET.Element:
    return ET.Element("Step", {"enable": "True", "id": "79", "name": "Freeze Window"})


def go_to_list_of_records(calc_text: str) -> ET.Element:
    step = ET.Element(
        "Step", {"enable": "True", "id": "228", "name": "Go to List of Records"}
    )
    ET.SubElement(step, "Calculation").text = calc_text
    ET.SubElement(step, "LayoutDestination", {"value": "CurrentLayout"})
    return step


def comments(root: ET.Element) -> list[str]:
    return [step.findtext("Text", default="") for step in root if step.get("name") == "# (comment)"]


def history(root: ET.Element) -> list[str]:
    return [text for text in comments(root) if text.startswith(" Modified:\t")]


def set_calc(step: ET.Element, calc_text: str) -> None:
    calc = calculation(step)
    if calc is None:
        raise AssertionError("Step has no calculation")
    calc.text = calc_text


def build_build_replacement(source: ET.Element) -> ET.Element:
    root = deepcopy(source)
    old_history = history(source)
    root.insert(5, comment(NEW_BUILD_HISTORY))

    _, rows_step = find_variable(root, "$_rows_text")
    rows_calc = rows_step.find("Value/Calculation")
    assert rows_calc is not None and rows_calc.text is not None
    old_sql_fragment = '"r.\\"global_rating\\", r.\\"global_rank_order\\" " &'
    new_sql_fragment = '"r.\\"global_rating\\", r.\\"global_rank_order\\", m.ROWID " &'
    if rows_calc.text.count(old_sql_fragment) != 1:
        raise AssertionError("Expected one five-column SQL fragment")
    rows_calc.text = rows_calc.text.replace(old_sql_fragment, new_sql_fragment)

    replace_start, _ = find_variable(root, "$_native_ids")
    replace_end, _ = find_variable(root, "$_find_error")

    layout_if_index = find_first_step(root, "If", replace_start)
    layout_end_index = matching_end_if(root, layout_if_index)
    layout_guard = [deepcopy(step) for step in root[layout_if_index : layout_end_index + 1]]

    replacement = [
        set_variable("$_private_rows", PRIVATE_ROWS_CALC),
        set_variable("$$wv_hybrid_movie_rowid_map", PRIVATE_MAP_CALC),
        set_variable("$_record_ids", RECORD_IDS_CALC),
        set_variable(
            "$_record_ids_for_step",
            'Case ( IsEmpty ( $_record_ids ) ; "[]" ; $_record_ids )',
        ),
        *layout_guard,
        freeze_window(),
        go_to_list_of_records("$_record_ids_for_step"),
        set_variable("$_list_error", "Get ( LastError )"),
    ]
    root[replace_start : replace_end + 1] = replacement

    _, status_step = find_variable(root, "$_status")
    status_calc = status_step.find("Value/Calculation")
    assert status_calc is not None and status_calc.text is not None
    status_calc.text += r''' &
  Case (
    $_list_error = 0 ; "" ;
    $_list_error = 401 ; " | empty native found set" ;
    " | Go to List error " & $_list_error
  )'''

    if history(root) != [NEW_BUILD_HISTORY, *old_history]:
        raise AssertionError("Build history was not preserved verbatim")
    return root


def build_apply_replacement(source: ET.Element) -> ET.Element:
    root = deepcopy(source)
    old_history = history(source)

    notes = root[5]
    if notes.get("name") != "# (comment)" or not notes.findtext("Text", "").startswith(" Notes:\t"):
        raise AssertionError("Apply Notes header moved")
    notes.find("Text").text = (
        " Notes:\t\tSelection retains one calculated record jump. Band changes restore the "
        "native found set with one private ROWID-backed Go to List of Records operation."
    )
    root.insert(6, comment(NEW_APPLY_HISTORY))

    _, context_invalid_step = find_variable(root, "$_context_invalid")
    set_calc(context_invalid_step, CONTEXT_INVALID_CALC)

    band_if_index = next(
        index
        for index, step in enumerate(root)
        if step.get("id") == "68"
        and (calculation(step).text if calculation(step) is not None else "").strip()
        == "$_set_band_action or $_clear_band_action"
    )
    band_end_index = matching_end_if(root, band_if_index)
    replacement = [
        set_variable("$_record_ids", RECORD_IDS_CALC),
        set_variable(
            "$_record_ids_for_step",
            'Case ( IsEmpty ( $_record_ids ) ; "[]" ; $_record_ids )',
        ),
        freeze_window(),
        go_to_list_of_records("$_record_ids_for_step"),
        set_variable("$_list_error", "Get ( LastError )"),
    ]
    root[band_if_index + 1 : band_end_index] = replacement

    if history(root) != [NEW_APPLY_HISTORY, *old_history]:
        raise AssertionError("Apply history was not preserved verbatim")
    return root


def control_flow_is_balanced(root: ET.Element) -> bool:
    if_depth = 0
    loop_depth = 0
    for step in root:
        step_id = step.get("id")
        if step_id == "68":
            if_depth += 1
        elif step_id == "70":
            if_depth -= 1
        elif step_id == "71":
            loop_depth += 1
        elif step_id == "73":
            loop_depth -= 1
        if if_depth < 0 or loop_depth < 0:
            return False
    return if_depth == 0 and loop_depth == 0


def validate_output(
    root: ET.Element,
    source: ET.Element,
    expected_new_history: str,
    expected_steps: int,
) -> None:
    assert root.tag == "fmxmlsnippet" and root.get("type") == "FMObjectList"
    assert len(root) == expected_steps
    assert all(step.tag == "Step" for step in root)
    assert history(root) == [expected_new_history, *history(source)]
    assert control_flow_is_balanced(root)

    forbidden_names = {"Enter Find Mode", "New Record/Request", "Perform Find"}
    assert not any(step.get("name") in forbidden_names for step in root)
    assert not any(variable_name(step) in {"$_native_ids", "$_request_index", "$_find_error"} for step in root)

    go_list_steps = [step for step in root if step.get("name") == "Go to List of Records"]
    assert len(go_list_steps) == 1
    go_list = go_list_steps[0]
    assert go_list.get("id") == "228" and go_list.get("enable") == "True"
    assert [child.tag for child in go_list] == ["Calculation", "LayoutDestination"]
    assert go_list.findtext("Calculation") == "$_record_ids_for_step"
    assert go_list.find("LayoutDestination").get("value") == "CurrentLayout"
    assert go_list.find("Layout") is None
    assert go_list.find("WindowReference") is None

    text = ET.tostring(root, encoding="unicode")
    assert "$$wv_hybrid_movie_rowid_map" in text
    assert "record_id" in text
    assert "not $_band_active" in text
    assert '"[]"' in text

    public_context_calcs = []
    for step in root:
        calc = calculation(step)
        if calc is not None and calc.text and "ranked_view" in calc.text:
            public_context_calcs.append(calc.text)
    assert public_context_calcs
    for calc_text in public_context_calcs:
        if "$$wv_hybrid_movie_rowid_map" not in calc_text:
            assert "ROWID" not in calc_text
            assert '"record_id"' not in calc_text


def write(root: ET.Element, path: Path) -> None:
    ET.indent(root, space="  ")
    xml = ET.tostring(root, encoding="unicode", short_empty_elements=True)
    path.write_text(xml + "\n", encoding="utf-8")


def main() -> None:
    for path, expected in EXPECTED_SOURCE_HASHES.items():
        actual = digest(path)
        if actual != expected:
            raise AssertionError(f"Source drift: {path.name}: {actual}")

    build_source = parse(BUILD_SOURCE)
    apply_source = parse(APPLY_SOURCE)
    assert len(build_source) == 69
    assert len(apply_source) == 66

    build_root = build_build_replacement(build_source)
    apply_root = build_apply_replacement(apply_source)

    validate_output(build_root, build_source, NEW_BUILD_HISTORY, 62)
    validate_output(apply_root, apply_source, NEW_APPLY_HISTORY, 56)

    build_rows_calc = find_variable(build_root, "$_rows_text")[1].findtext("Value/Calculation", "")
    assert "m.ROWID" in build_rows_calc
    assert 'ORDER BY r.\\"global_rank_order\\" ASC' in build_rows_calc
    assert find_variable(build_root, "$_rows_json")[1].findtext("Value/Calculation", "").count(
        "GetValue ( values ; 6 )"
    ) == 0

    apply_invalid = find_variable(apply_root, "$_context_invalid")[1].findtext("Value/Calculation", "")
    assert 'GetField ( "FOCUS::g_wv_demo_genre_id" )' in apply_invalid
    assert "ranked_view.rows" in apply_invalid

    write(build_root, BUILD_OUTPUT)
    write(apply_root, APPLY_OUTPUT)

    # Generated outputs must not mutate either neighboring Article 4 script.
    assert digest(HANDLER_SOURCE) == EXPECTED_SOURCE_HASHES[HANDLER_SOURCE]
    assert digest(NATIVE_ROW_SOURCE) == EXPECTED_SOURCE_HASHES[NATIVE_ROW_SOURCE]

    print(f"Wrote {BUILD_OUTPUT.name}: {len(build_root)} steps, sha256={digest(BUILD_OUTPUT)}")
    print(f"Wrote {APPLY_OUTPUT.name}: {len(apply_root)} steps, sha256={digest(APPLY_OUTPUT)}")
    print("Static validation passed: step-only FMObjectList roots, preserved histories, balanced control flow,")
    print("no find/request steps, one current-layout Go to List of Records step per script, ROWID private.")


if __name__ == "__main__":
    main()
