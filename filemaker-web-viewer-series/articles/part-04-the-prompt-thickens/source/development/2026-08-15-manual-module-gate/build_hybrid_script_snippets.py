#!/usr/bin/env python3
"""Build Article 4 FileMaker script-step FMXML from the exact Article 3 sources."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET


ARTICLE_FOUR = Path(__file__).resolve().parents[2]
ARTICLE_THREE = ARTICLE_FOUR.parent / "article three"
SOURCE_DIR = ARTICLE_THREE / "fmxmlsnippets"
OUTPUT_DIR = ARTICLE_FOUR / "fmxmlsnippets"

BUILDER_SOURCE = SOURCE_DIR / "WV__Demo_Build_Context_Ranked.fmxmlsnippet.xml"
HANDLER_SOURCE = SOURCE_DIR / "WV__Demo_Handle_Action_Ranked.fmxmlsnippet.xml"
SHARED_LOADER_SOURCE = (
    ARTICLE_FOUR.parent
    / "fmxmlsnippets"
    / "full_script_replacements_json_params"
    / "04__webviewer___load___index____object_name__FULL_JSON_PARAMS.fmxmlsnippet.xml"
)


def parse_step(xml: str) -> ET.Element:
    return ET.fromstring(xml)


def calculation(step: ET.Element) -> ET.Element | None:
    return step.find(".//Calculation")


def variable_name(step: ET.Element) -> str:
    node = step.find("Name")
    return "" if node is None or node.text is None else node.text


def find_variable(root: ET.Element, name: str) -> tuple[int, ET.Element]:
    for index, step in enumerate(root):
        if variable_name(step) == name:
            return index, step
    raise ValueError(f"Variable step not found: {name}")


def find_if(root: ET.Element, expression: str) -> int:
    for index, step in enumerate(root):
        if step.get("id") != "68":
            continue
        calc = calculation(step)
        if calc is not None and (calc.text or "").strip() == expression:
            return index
    raise ValueError(f"If step not found: {expression}")


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
    raise ValueError(f"End If not found for step {if_index}")


def set_variable(name: str, calc_text: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "141", "name": "Set Variable"})
    value = ET.SubElement(step, "Value")
    calc = ET.SubElement(value, "Calculation")
    calc.text = calc_text
    repetition = ET.SubElement(step, "Repetition")
    rep_calc = ET.SubElement(repetition, "Calculation")
    rep_calc.text = "1"
    name_node = ET.SubElement(step, "Name")
    name_node.text = name
    return step


def comment(text: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "89", "name": "# (comment)"})
    node = ET.SubElement(step, "Text")
    node.text = text
    return step


def if_step(calc_text: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "68", "name": "If"})
    ET.SubElement(step, "Restore", {"state": "False"})
    calc = ET.SubElement(step, "Calculation")
    calc.text = calc_text
    return step


def else_step() -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "69", "name": "Else"})
    ET.SubElement(step, "Restore", {"state": "False"})
    return step


def end_if() -> ET.Element:
    return ET.Element("Step", {"enable": "True", "id": "70", "name": "End If"})


def set_field_by_name(target: str, result: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "147", "name": "Set Field By Name"})
    result_node = ET.SubElement(step, "Result")
    result_calc = ET.SubElement(result_node, "Calculation")
    result_calc.text = result
    target_node = ET.SubElement(step, "TargetName")
    target_calc = ET.SubElement(target_node, "Calculation")
    target_calc.text = f'"{target}"'
    return step


def set_field(table: str, field_id: str, name: str, calc_text: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "76", "name": "Set Field"})
    calc = ET.SubElement(step, "Calculation")
    calc.text = calc_text
    ET.SubElement(step, "Field", {"table": table, "id": field_id, "name": name})
    return step


def exit_script(calc_text: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "103", "name": "Exit Script"})
    calc = ET.SubElement(step, "Calculation")
    calc.text = calc_text
    return step


def go_to_layout(layout_id: str, name: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "6", "name": "Go to Layout"})
    ET.SubElement(step, "LayoutDestination", {"value": "SelectedLayout"})
    ET.SubElement(step, "Layout", {"id": layout_id, "name": name})
    return step


def go_first() -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "16", "name": "Go to Record/Request/Page"})
    ET.SubElement(step, "NoInteract", {"state": "False"})
    ET.SubElement(step, "RowPageLocation", {"value": "First"})
    return step


def go_next() -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "16", "name": "Go to Record/Request/Page"})
    ET.SubElement(step, "NoInteract", {"state": "False"})
    ET.SubElement(step, "Exit", {"state": "False"})
    ET.SubElement(step, "RowPageLocation", {"value": "Next"})
    return step


def go_to_record_by_calculation(calc_text: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "16", "name": "Go to Record/Request/Page"})
    ET.SubElement(step, "NoInteract", {"state": "True"})
    ET.SubElement(step, "RowPageLocation", {"value": "ByCalculation"})
    calc = ET.SubElement(step, "Calculation")
    calc.text = calc_text
    return step


def go_to_object(object_name: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "145", "name": "Go to Object"})
    object_node = ET.SubElement(step, "ObjectName")
    object_calc = ET.SubElement(object_node, "Calculation")
    object_calc.text = f'"{object_name}"'
    repetition = ET.SubElement(step, "Repetition")
    rep_calc = ET.SubElement(repetition, "Calculation")
    rep_calc.text = "1"
    return step


def go_to_portal_row(location: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "99", "name": "Go to Portal Row"})
    ET.SubElement(step, "NoInteract", {"state": "False"})
    ET.SubElement(step, "SelectAll", {"state": "False"})
    ET.SubElement(step, "Exit", {"state": "False"})
    ET.SubElement(step, "RowPageLocation", {"value": location})
    return step


def perform_javascript(object_name: str, function_name: str, parameter: str = '""') -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "175", "name": "Perform JavaScript in Web Viewer"})
    name_node = ET.SubElement(step, "Name")
    name_calc = ET.SubElement(name_node, "Calculation")
    name_calc.text = object_name
    function_node = ET.SubElement(step, "FunctionRef")
    function_calc = ET.SubElement(function_node, "Calculation")
    function_calc.text = function_name
    parameter_node = ET.SubElement(step, "Parameter")
    parameter_calc = ET.SubElement(parameter_node, "Calculation")
    parameter_calc.text = parameter
    return step


def loop_step() -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "71", "name": "Loop"})
    ET.SubElement(step, "FlushType", {"value": "Always"})
    return step


def exit_loop_if(calc_text: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "72", "name": "Exit Loop If"})
    calc = ET.SubElement(step, "Calculation")
    calc.text = calc_text
    return step


def end_loop() -> ET.Element:
    return ET.Element("Step", {"enable": "True", "id": "73", "name": "End Loop"})


def perform_script(script_id: str, name: str, parameter: str = '""') -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "1", "name": "Perform Script"})
    calc = ET.SubElement(step, "Calculation")
    calc.text = parameter
    ET.SubElement(step, "Script", {"id": script_id, "name": name})
    return step


def open_url(calc_text: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "111", "name": "Open URL"})
    ET.SubElement(step, "NoInteract", {"state": "True"})
    ET.SubElement(step, "Option", {"state": "False"})
    calc = ET.SubElement(step, "Calculation")
    calc.text = calc_text
    return step


def install_on_timer(script_id: str = "", name: str = "", interval: str = "") -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "148", "name": "Install OnTimer Script"})
    if interval:
        interval_node = ET.SubElement(step, "Interval")
        calc = ET.SubElement(interval_node, "Calculation")
        calc.text = interval
    if script_id and name:
        ET.SubElement(step, "Script", {"id": script_id, "name": name})
    return step


def pause(seconds: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "62", "name": "Pause/Resume Script"})
    ET.SubElement(step, "PauseTime", {"value": "ForDuration"})
    calc = ET.SubElement(step, "Calculation")
    calc.text = seconds
    return step


def enter_find_mode() -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "22", "name": "Enter Find Mode"})
    ET.SubElement(step, "Pause", {"state": "False"})
    ET.SubElement(step, "Restore", {"state": "False"})
    return step


def perform_find() -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "28", "name": "Perform Find"})
    ET.SubElement(step, "Restore", {"state": "False"})
    return step


def new_record_request() -> ET.Element:
    return ET.Element("Step", {"enable": "True", "id": "7", "name": "New Record/Request"})


def constrain_found_set() -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "126", "name": "Constrain Found Set"})
    ET.SubElement(step, "Option", {"state": "False"})
    ET.SubElement(step, "Restore", {"state": "False"})
    return step


def show_all_records() -> ET.Element:
    return ET.Element("Step", {"enable": "True", "id": "23", "name": "Show All Records"})


def sort_records(table: str, field_id: str, name: str, direction: str = "Ascending") -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "39", "name": "Sort Records"})
    ET.SubElement(step, "NoInteract", {"state": "True"})
    ET.SubElement(step, "Restore", {"state": "True"})
    sort_list = ET.SubElement(step, "SortList", {"Maintain": "True", "value": "True"})
    sort = ET.SubElement(sort_list, "Sort", {"type": direction})
    primary = ET.SubElement(sort, "PrimaryField")
    ET.SubElement(primary, "Field", {"table": table, "id": field_id, "name": name})
    return step


def freeze_window() -> ET.Element:
    return ET.Element("Step", {"enable": "True", "id": "79", "name": "Freeze Window"})


def omit_record() -> ET.Element:
    return ET.Element("Step", {"enable": "True", "id": "25", "name": "Omit Record"})


def remove_interaction_reload(root: ET.Element) -> None:
    steps = list(root)
    matches = [
        index for index, step in enumerate(steps)
        if step.get("name") == "Perform Script"
        and step.find("Script") is not None
        and step.find("Script").get("name") == "WV__Demo_Load_Viewer"
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one interaction-time viewer load, found {len(matches)}")
    load_index = matches[0]
    if load_index < 1 or load_index + 1 >= len(steps):
        raise ValueError("interaction-time viewer load is missing its surrounding pauses")
    before = steps[load_index - 1]
    after = steps[load_index + 1]
    if (
        before.get("name") != "Pause/Resume Script"
        or calculation(before) is None
        or calculation(before).text != ".5"
        or after.get("name") != "Pause/Resume Script"
        or calculation(after) is None
        or calculation(after).text != "1"
    ):
        raise ValueError("interaction-time viewer load sequence does not match the reviewed source")
    root.remove(before)
    root.remove(steps[load_index])
    root.remove(after)


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"Expected one occurrence, found {count}: {old[:80]!r}")
    return text.replace(old, new, 1)


def build_context() -> ET.Element:
    root = ET.parse(BUILDER_SOURCE).getroot()

    header = [
        " Purpose:\tBuild the hybrid rating context, native found set, and acknowledged FileMaker-owned selection/band state.",
        " In:\t\t\tFOCUS::g_wv_demo_movie_id, FOCUS::g_wv_demo_genre_id, FOCUS::g_wv_rating_lo, FOCUS::g_wv_rating_hi",
        " Out:\t\tFOCUS::g_wv_module_index, FOCUS::g_wv_context_json, FOCUS::g_wv_status; exits with raw context JSON.",
        " Anchor:\t\tMOVIE_GLOBAL_RATING on WV Framework - Hybrid. Native rows come from the rating found set and expose related MOVIE display fields.",
        " Calls:\t\tNone. FileMaker establishes the native rating-band found set and shapes the rendering contract.",
    ]
    for step, text in zip(root[:5], header):
        step.find("Text").text = text
    root.insert(5, comment(" Modified:\t15 Aug 2026, 19hr31PT — Lon Cook — lon@portagebay.com : add the Article 4 hybrid rating context and FileMaker-owned rating-band found set."))
    root.insert(5, comment(" Modified:\t15 Aug 2026, 23hr41PT — Lon Cook — lon@portagebay.com : preserve the loaded Web Viewer by avoiding redundant navigation to the current hybrid layout."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 01hr42PT — Lon Cook — lon@portagebay.com : replace per-movie find requests with one related-field find and skip unchanged selection finds."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 02hr18PT — Lon Cook — lon@portagebay.com : preserve related-record find semantics by establishing the genre set before constraining it to the rating band."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 02hr24PT — Lon Cook — lon@portagebay.com : replace unsupported unrelated-field criteria with one frozen local pass over the verified MOVIE id set."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 15hr38PT — Lon Cook — lon@portagebay.com : move hybrid context to a stable SOLUTION__all host and remove every interaction-time find and record-navigation step."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 17hr36PT — Lon Cook — lon@portagebay.com : restore the MOVIE-based native List View and replace record walking with one calculated record navigation."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 19hr08PT — Lon Cook — lon@portagebay.com : anchor the native List View on MOVIE_GLOBAL_RATING, find one stored rating range, and remove current-record selection navigation."))

    _, index_step = find_variable(root, "$_index")
    calculation(index_step).text = "43"

    layout_steps = [
        (position, step) for position, step in enumerate(root)
        if step.get("name") == "Go to Layout"
        and step.find("Layout") is not None
        and step.find("Layout").get("name") == "WV Framework - Demo"
    ]
    if len(layout_steps) != 1:
        raise ValueError(f"expected one hybrid-layout navigation step, found {len(layout_steps)}")
    layout_index, layout_step = layout_steps[0]
    layout_step.find("Layout").set("id", "150")
    layout_step.find("Layout").set("name", "WV Framework - Hybrid")
    root.insert(layout_index, if_step('Get ( LayoutName ) <> "WV Framework - Hybrid"'))
    root.insert(layout_index + 2, end_if())

    genre_index, _ = find_variable(root, "$_genre_id")
    band_steps = [
        set_variable("$_rating_lo_raw", 'GetAsText ( GetField ( "FOCUS::g_wv_rating_lo" ) )'),
        set_variable("$_rating_hi_raw", 'GetAsText ( GetField ( "FOCUS::g_wv_rating_hi" ) )'),
        set_variable("$_band_active", "not IsEmpty ( $_rating_lo_raw ) and not IsEmpty ( $_rating_hi_raw ) and\nGetAsNumber ( $_rating_lo_raw ) <= GetAsNumber ( $_rating_hi_raw )"),
        set_variable("$_rating_lo", 'Case ( $_band_active ; GetAsNumber ( $_rating_lo_raw ) ; "" )'),
        set_variable("$_rating_hi", 'Case ( $_band_active ; GetAsNumber ( $_rating_hi_raw ) ; "" )'),
        set_variable("$_band_label", 'Case ( $_band_active ; "Ratings " & $_rating_lo & "–" & $_rating_hi ; "All ratings" )'),
    ]
    for offset, step in enumerate(band_steps, 1):
        root.insert(genre_index + offset, step)

    for step in root:
        layout = step.find("Layout")
        if layout is not None and layout.get("name") == "WV Framework - Demo":
            layout.set("id", "150")
            layout.set("name", "WV Framework - Hybrid")

    _, ids_step = find_variable(root, "$_ranked_ids")
    ids_index = list(root).index(ids_step)
    root.remove(ids_step)

    _, find_error_step = find_variable(root, "$_find_error")
    find_error_index = list(root).index(find_error_step)
    enter_find_index = next(
        index for index, step in enumerate(root[:find_error_index])
        if index >= ids_index and step.get("name") == "Enter Find Mode"
    )
    for step in list(root)[enter_find_index:find_error_index + 1]:
        root.remove(step)
    direct_find = [
        freeze_window(),
        if_step("IsEmpty ( $_genre_id ) and not $_band_active"),
        show_all_records(),
        set_variable("$_find_error", "0"),
        else_step(),
        enter_find_mode(),
        if_step("not IsEmpty ( $_genre_id )"),
        set_field("MOVIE_GENRE", "15", "id_genre", '"==" & $_genre_id'),
        end_if(),
        if_step("$_band_active"),
        set_field("MOVIE_GLOBAL_RATING", "16", "global_rating", 'GetAsText ( $_rating_lo ) & "..." & GetAsText ( $_rating_hi )'),
        end_if(),
        perform_find(),
        set_variable("$_find_error", "Get ( LastError )"),
        end_if(),
        sort_records("MOVIE_GLOBAL_RATING", "21", "global_rank_order"),
    ]
    for offset, step in enumerate(direct_find):
        root.insert(enter_find_index + offset, step)

    _, nav_index_step = find_variable(root, "$_nav_index")
    nav_index = list(root).index(nav_index_step)
    nav_if = nav_index - 1
    if root[nav_if].get("name") != "If":
        raise ValueError("expected selection-navigation If before $_nav_index")
    nav_end = matching_end_if(root, nav_if)
    for step in list(root)[nav_if:nav_end + 1]:
        root.remove(step)

    movie_id_steps = [step for step in root if variable_name(step) == "$_movie_id"]
    if len(movie_id_steps) != 2:
        raise ValueError(f"expected initial and normalized $_movie_id steps, found {len(movie_id_steps)}")
    calculation(movie_id_steps[1]).text = 'Case ( $_selected_valid ; $_movie_id ; Get ( FoundCount ) > 0 ; GetAsText ( MOVIE_GLOBAL_RATING::id_movie ) ; "" )'

    context_calcs = []
    for step in root:
        calc = calculation(step)
        text = "" if calc is None or calc.text is None else calc.text
        if "JSONSetElement" in text and '"ranked_view.rows"' in text:
            context_calcs.append(calc)
    if len(context_calcs) != 2:
        raise ValueError(f"Expected two context calculations, found {len(context_calcs)}")

    band_json = """  ; [ "ranked_view.rating_band.active" ; $_band_active ; JSONBoolean ]
  ; [ "ranked_view.rating_band.rating_lo" ; Case ( $_band_active ; $_rating_lo ; "" ) ; Case ( $_band_active ; JSONNumber ; JSONNull ) ]
  ; [ "ranked_view.rating_band.rating_hi" ; Case ( $_band_active ; $_rating_hi ; "" ) ; Case ( $_band_active ; JSONNumber ; JSONNull ) ]
  ; [ "ranked_view.rating_band.label" ; $_band_label ; JSONString ]
"""
    for calc in context_calcs:
        text = calc.text
        text = text.replace('  ; [ "__wv.source" ; "ranked_views_demo" ; JSONString ]', '  ; [ "__wv.source" ; "hybrid_rating_demo" ; JSONString ]')
        if '"__wv.page_name"' not in text:
            text = replace_once(text, '  ; [ "__wv.page" ; $_index ; JSONNumber ]\n', '  ; [ "__wv.page" ; $_index ; JSONNumber ]\n  ; [ "__wv.page_name" ; "hybrid_rating" ; JSONString ]\n')
        else:
            text = text.replace('"ranked_list"', '"hybrid_rating"')
        text = replace_once(text, '  ; [ "ranked_view.selected_movie_id"', band_json + '  ; [ "ranked_view.selected_movie_id"')
        text = text.replace(
            '  ; [ "ranked_view.current_record_id" ; GetAsText ( MOVIE::ID ) ; JSONString ]',
            '  ; [ "ranked_view.current_record_id" ; Case ( Get ( FoundCount ) > 0 ; GetAsText ( MOVIE_GLOBAL_RATING::id_movie ) ; "" ) ; JSONString ]',
        )
        calc.text = text

    _, status_step = find_variable(root, "$_status")
    calculation(status_step).text = '"Hybrid native list context built: " & $_row_count & " movies | " & $_band_label &\n  If ( not IsEmpty ( $_movie_id ) ; " | selected movie " & $_movie_id & " | " & Get ( FoundCount ) & " native rating rows" ; " | no native selection" )'

    return root


def rejection_steps(message: str, error: str, extra_json: str = "") -> list[ET.Element]:
    result = [
        set_field_by_name("FOCUS::g_wv_action_json", "$_formatted"),
        set_field_by_name("FOCUS::g_wv_action_type", "$_type"),
        set_field_by_name("FOCUS::g_wv_action_status", f'"{message}"'),
    ]
    calc = 'JSONSetElement ( "{}"\n  ; [ "ok" ; 0 ; JSONBoolean ]\n  ; [ "error" ; "' + error + '" ; JSONString ]'
    if extra_json:
        calc += "\n" + extra_json
    calc += "\n)"
    # A rejected intent still receives the last authoritative context, but it
    # must not pay for a full SQL/find rebuild. WV__Demo_Push_Context builds
    # only when no context exists yet.
    result.extend([
        perform_script("482", "WV__Demo_Push_Context"),
        set_variable("$_push_result", "GetAsText ( Get ( ScriptResult ) )"),
        exit_script(calc),
    ])
    return result


def build_handler() -> ET.Element:
    root = ET.parse(HANDLER_SOURCE).getroot()

    header = [
        " Purpose:\tReceive and validate inherited or hybrid action envelopes, apply FileMaker-owned state, and push acknowledgement context.",
        " In:\t\t\tGet ( ScriptParameter ) as raw JSON.",
        " Out:\t\tJSON status object.",
        " Anchor:\t\tMOVIE_GLOBAL_RATING on WV Framework - Hybrid for hybrid actions; inherited actions retain their original target layout.",
        " Calls:\t\tWV__Demo_Apply_Hybrid_Context, WV__Demo_Build_Context, WV__Demo_Push_Context.",
    ]
    for step, text in zip(root[:5], header):
        step.find("Text").text = text
    root.insert(5, comment(" Modified:\t15 Aug 2026, 19hr31PT — Lon Cook — lon@portagebay.com : validate hybrid selection and rating-band intent, apply native state, and return acknowledgement context."))
    root.insert(5, comment(" Modified:\t15 Aug 2026, 23hr32PT — Lon Cook — lon@portagebay.com : push fresh acknowledgement context into the loaded Web Viewer without reloading it."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 01hr12PT — Lon Cook — lon@portagebay.com : defer hybrid navigation and acknowledgement until the Web Viewer-originated script returns."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 01hr42PT — Lon Cook — lon@portagebay.com : avoid irrelevant JSON scans and queue one low-latency hybrid continuation."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 02hr10PT — Lon Cook — lon@portagebay.com : stabilize the host-idle handoff with a reliable 0.10-second continuation interval."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 13hr44PT — Lon Cook — lon@portagebay.com : remove the starved OnTimer handoff and build and push hybrid acknowledgement in the action script."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 14hr03PT — Lon Cook — lon@portagebay.com : queue acknowledgement through an fmp URL callback after authoritative native state and context are built."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 14hr25PT — Lon Cook — lon@portagebay.com : settle native state with exact-id finds and patch the resident context without rebuilding the chart payload."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 14hr40PT — Lon Cook — lon@portagebay.com : push acknowledgement directly after the deferred WV.sendAction bridge releases the browser event stack."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 14hr58PT — Lon Cook — lon@portagebay.com : preserve the acknowledged movie across rating-band finds when it remains in the resulting native found set."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 15hr02PT — Lon Cook — lon@portagebay.com : locate the selected native record with GetNthRecord and navigate once so selection does not blank the resident viewer record by record."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 15hr38PT — Lon Cook — lon@portagebay.com : settle hybrid actions entirely through globals on a stable host, rebuild context without finds, and acknowledge one coalesced bridge request at a time."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 16hr18PT — Lon Cook — lon@portagebay.com : treat receipt of authoritative pushed context as the bridge acknowledgement and remove the redundant second JavaScript call."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 16hr39PT — Lon Cook — lon@portagebay.com : push authoritative acknowledgement context on every rejected hybrid intent before exiting."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 17hr05PT — Lon Cook — lon@portagebay.com : synchronize Web Viewer selections to the exact stable-ID row in the resident native portal."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 17hr31PT — Lon Cook — lon@portagebay.com : accept every selectable movie exposed by the authoritative context, including dimmed points outside the active rating band."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 17hr36PT — Lon Cook — lon@portagebay.com : restore stable-id selection to the MOVIE-based native List View with one calculated record navigation."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 18hr12PT — Lon Cook — lon@portagebay.com : remove interaction-time context rebuilds, settle through the Article 4 patch script, and freeze the one native navigation."))
    root.insert(5, comment(" Modified:\t16 Aug 2026, 19hr08PT — Lon Cook — lon@portagebay.com : validate hybrid selections against context and cross-highlight by stable id without changing the current record."))

    payload_index, _ = find_variable(root, "$_payload_movie_id")
    payload_steps = [
        set_variable("$_payload_rating_lo", 'GetAsNumber ( JSONGetElement ( $_raw ; "payload.rating_lo" ) )'),
        set_variable("$_payload_rating_hi", 'GetAsNumber ( JSONGetElement ( $_raw ; "payload.rating_hi" ) )'),
    ]
    for offset, step in enumerate(payload_steps, 1):
        root.insert(payload_index + offset, step)

    _, known_step = find_variable(root, "$_known_action")
    known_calc = calculation(known_step)
    known_calc.text = known_calc.text.replace('$_type = "ranked.select_movie"', '$_type = "ranked.select_movie" or\n$_type = "hybrid.select_movie" or\n$_type = "hybrid.set_rating_band" or\n$_type = "hybrid.clear_rating_band"')

    ranked_index, _ = find_variable(root, "$_ranked_action")
    action_steps = [
        set_variable("$_hybrid_select_action", '$_type = "hybrid.select_movie"'),
        set_variable("$_hybrid_set_band_action", '$_type = "hybrid.set_rating_band"'),
        set_variable("$_hybrid_clear_band_action", '$_type = "hybrid.clear_rating_band"'),
        set_variable("$_hybrid_action", "$_hybrid_select_action or $_hybrid_set_band_action or $_hybrid_clear_band_action"),
    ]
    for offset, step in enumerate(action_steps, 1):
        root.insert(ranked_index + offset, step)

    invalid_ranked_index, _ = find_variable(root, "$_invalid_ranked_selection")
    invalid_ranked_if = invalid_ranked_index + 1
    invalid_ranked_end = matching_end_if(root, invalid_ranked_if)

    hybrid_selection_available = set_variable("$_hybrid_selection_available", """Case ( not $_hybrid_select_action ; False ;
Let ( [
  context_json = GetAsText ( GetField ( "FOCUS::g_wv_context_json" ) ) ;
  rows = JSONGetElement ( context_json ; "ranked_view.rows" ) ;
  n = ValueCount ( JSONListKeys ( rows ; "" ) )
] ;
  While (
    [ i = 0 ; found = False ] ;
    i < n and not found ;
    [
      found = GetAsText ( JSONGetElement ( rows ; "[" & i & "].movie_id" ) ) = $_payload_movie_id ;
      i = i + 1
    ] ;
    found
  )
)
)""")
    hybrid_validation = set_variable("$_invalid_hybrid_selection", """Case ( not $_hybrid_select_action ; False ;
Let ( [
  payload_type_error = EvaluationError ( JSONGetElementType ( $_raw ; "payload.movie_id" ) ) ;
  found = $_hybrid_selection_available
] ;
  $_hybrid_select_action and (
    $_page <> 43 or
    $_source <> "wv.renderer.hybrid.rating" or
    payload_type_error <> 0 or
    JSONGetElementType ( $_raw ; "payload.movie_id" ) <> JSONString or
    IsEmpty ( $_payload_movie_id ) or
    not found
  )
)
)""")
    hybrid_band_validation = set_variable("$_invalid_hybrid_band", """Case ( not ( $_hybrid_set_band_action or $_hybrid_clear_band_action ) ; False ;
Let ( [
  lo_type_error = EvaluationError ( JSONGetElementType ( $_raw ; "payload.rating_lo" ) ) ;
  hi_type_error = EvaluationError ( JSONGetElementType ( $_raw ; "payload.rating_hi" ) ) ;
  payload_key_count = ValueCount ( JSONListKeys ( $_raw ; "payload" ) )
] ;
  ( $_hybrid_set_band_action or $_hybrid_clear_band_action ) and (
    $_page <> 43 or
    $_source <> "wv.renderer.hybrid.rating" or
    ( $_hybrid_set_band_action and (
      lo_type_error <> 0 or hi_type_error <> 0 or
      JSONGetElementType ( $_raw ; "payload.rating_lo" ) <> JSONNumber or
      JSONGetElementType ( $_raw ; "payload.rating_hi" ) <> JSONNumber or
      $_payload_rating_lo > $_payload_rating_hi
    ) ) or
    ( $_hybrid_clear_band_action and payload_key_count <> 0 )
  )
)
)""")

    insertion = [
        hybrid_selection_available,
        hybrid_validation,
        if_step("$_invalid_hybrid_selection"),
        *rejection_steps(
            "Rejected hybrid selection: the movie id is not available in the authoritative hybrid context.",
            "invalid_hybrid_selection",
            '  ; [ "movie_id" ; $_payload_movie_id ; JSONString ]',
        ),
        end_if(),
        hybrid_band_validation,
        if_step("$_invalid_hybrid_band"),
        *rejection_steps(
            "Rejected hybrid rating band: the bounds or payload shape are not valid.",
            "invalid_hybrid_band",
        ),
        end_if(),
    ]
    for offset, step in enumerate(insertion, 1):
        root.insert(invalid_ranked_end + offset, step)

    ranked_if = find_if(root, "$_ranked_action")
    ranked_end = matching_end_if(root, ranked_if)
    hybrid_state = [
        if_step("$_hybrid_select_action"),
        set_field_by_name("FOCUS::g_wv_demo_movie_id", "$_payload_movie_id"),
        end_if(),
        if_step("$_hybrid_set_band_action"),
        set_field_by_name("FOCUS::g_wv_rating_lo", "$_payload_rating_lo"),
        set_field_by_name("FOCUS::g_wv_rating_hi", "$_payload_rating_hi"),
        else_step(),
        if_step("$_hybrid_clear_band_action"),
        set_field_by_name("FOCUS::g_wv_rating_lo", '""'),
        set_field_by_name("FOCUS::g_wv_rating_hi", '""'),
        end_if(),
        end_if(),
    ]
    for offset, step in enumerate(hybrid_state, 1):
        root.insert(ranked_end + offset, step)

    _, status_step = find_variable(root, "$_status")
    calculation(status_step).text = """Case (
  $_ranked_action ; "Selected native movie " & GetAsText ( MOVIE::ID ) ;
  $_hybrid_select_action ; "Selected hybrid movie " & $_payload_movie_id & " in native list" ;
  $_hybrid_set_band_action ; "Applied native rating band " & $_payload_rating_lo & "–" & $_payload_rating_hi ;
  $_hybrid_clear_band_action ; "Cleared native rating band" ;
  "Handled " & $_type
)"""

    remove_interaction_reload(root)

    build_steps = [
        (index, step) for index, step in enumerate(root)
        if step.get("name") == "Perform Script"
        and step.find("Script") is not None
        and step.find("Script").get("name") == "WV__Demo_Build_Context"
    ]
    if not build_steps:
        raise ValueError("expected a final context build")
    # Rejection branches also build and push settlement context. The last
    # builder remains the accepted-action continuation verified below.
    build_index, build_step = build_steps[-1]
    push_step = root[build_index + 1]
    push_result_step = root[build_index + 2]
    if (
        push_step.get("name") != "Perform Script"
        or push_step.find("Script") is None
        or push_step.find("Script").get("name") != "WV__Demo_Push_Context"
        or variable_name(push_result_step) != "$_push_result"
    ):
        raise ValueError("expected final context push immediately after context build")
    root.remove(build_step)
    settlement = [
        if_step("$_hybrid_action"),
        perform_script("502", "WV__Demo_Apply_Hybrid_Context"),
        else_step(),
        perform_script("480", "WV__Demo_Build_Context"),
        end_if(),
    ]
    for offset, step in enumerate(settlement):
        root.insert(build_index + offset, step)
    exit_steps = [step for step in root if step.get("id") == "103"]
    final_exit = exit_steps[-1]
    calculation(final_exit).text = """Let ( [
  band_lo = GetAsText ( GetField ( "FOCUS::g_wv_rating_lo" ) ) ;
  band_hi = GetAsText ( GetField ( "FOCUS::g_wv_rating_hi" ) ) ;
  band_active = not IsEmpty ( band_lo ) and not IsEmpty ( band_hi )
] ;
JSONSetElement ( "{}"
  ; [ "ok" ; 1 ; JSONBoolean ]
  ; [ "type" ; $_type ; JSONString ]
  ; [ "count" ; $_count ; JSONNumber ]
  ; [ "selected_movie_id" ; GetAsText ( GetField ( "FOCUS::g_wv_demo_movie_id" ) ) ; JSONString ]
  ; [ "rating_band.active" ; band_active ; JSONBoolean ]
  ; [ "rating_band.rating_lo" ; Case ( band_active ; GetAsNumber ( band_lo ) ; "" ) ; Case ( band_active ; JSONNumber ; JSONNull ) ]
  ; [ "rating_band.rating_hi" ; Case ( band_active ; GetAsNumber ( band_hi ) ; "" ) ; Case ( band_active ; JSONNumber ; JSONNull ) ]
  ; [ "push_result" ; $_push_result ; JSONString ]
 )
)"""

    settlement_names = ["Perform Script", "Set Variable"]
    exit_indexes = [index for index, step in enumerate(root) if step.get("name") == "Exit Script"]
    for exit_index in reversed(exit_indexes):
        prior_names = [step.get("name") for step in root[max(0, exit_index - 2):exit_index]]
        if prior_names != settlement_names:
            for offset, step in enumerate([
                perform_script("482", "WV__Demo_Push_Context"),
                set_variable("$_push_result", "GetAsText ( Get ( ScriptResult ) )"),
            ]):
                root.insert(exit_index + offset, step)

    return root


def build_apply_hybrid_context_script() -> ET.Element:
    root = ET.Element("fmxmlsnippet", {"type": "FMObjectList"})
    steps = [
        comment(" Purpose:\tApply Article 4 native List View state and patch the resident hybrid context without rebuilding its SQL payload."),
        comment(" In:\t\t\tFOCUS hybrid selection, rating band, action state, and existing page-43 context JSON."),
        comment(" Out:\t\tFOCUS::g_wv_context_json patched from authoritative native state; exits with raw context JSON."),
        comment(" Anchor:\t\tMOVIE_GLOBAL_RATING on WV Framework - Hybrid."),
        comment(" Calls:\t\tWV__Demo_Build_Context only when no valid page-43 context exists."),
        comment(" Notes:\t\tSelection changes only FileMaker-owned global state. Band changes perform one stored global_rating range find."),
        comment(" Modified:\t16 Aug 2026, 19hr08PT — Lon Cook — lon@portagebay.com : replace multi-request movie-id finds and record navigation with one rating-range find and stable-id cross-highlighting."),
        comment(" Modified:\t16 Aug 2026, 18hr12PT — Lon Cook — lon@portagebay.com : repurpose the continuation as the interaction-time native List View/context patch path."),
        comment(" Modified:\t16 Aug 2026, 14hr03PT — Lon Cook — lon@portagebay.com : replace host-idle scheduling with a queued fmp URL acknowledgement callback."),
        comment(" Modified:\t16 Aug 2026, 02hr10PT — Lon Cook — lon@portagebay.com : stabilize initial and re-armed host-idle handoffs at a reliable 0.10-second interval."),
        comment(" Modified:\t16 Aug 2026, 01hr57PT — Lon Cook — lon@portagebay.com : re-arm the continuation when a newer Web Viewer intent arrives during the active acknowledgement pass."),
        comment(" Modified:\t16 Aug 2026, 01hr42PT — Lon Cook — lon@portagebay.com : collapse two timer passes into one and skip redundant selection finds."),
        comment(" Modified:\t16 Aug 2026, 01hr25PT — Lon Cook — lon@portagebay.com : separate native navigation and Web Viewer push into consecutive one-shot passes."),
        comment(" Modified:\t16 Aug 2026, 00hr49PT — Lon Cook — lon@portagebay.com : created"),
        comment(""),
        parse_step('<Step enable="True" id="86" name="Set Error Capture"><Set state="True" /></Step>'),
        set_variable("$_type", 'GetAsText ( GetField ( "FOCUS::g_wv_action_type" ) )'),
        set_variable("$_context_json", 'GetAsText ( GetField ( "FOCUS::g_wv_context_json" ) )'),
        set_variable("$_context_invalid", 'IsEmpty ( $_context_json ) or JSONFormatElements ( $_context_json ) = "?" or\nGetAsNumber ( JSONGetElement ( $_context_json ; "__wv.page" ) ) <> 43 or\nEvaluationError ( JSONGetElementType ( $_context_json ; "ranked_view.rows" ) ) <> 0 or\nJSONGetElementType ( $_context_json ; "ranked_view.rows" ) <> JSONArray'),
        if_step("$_context_invalid"),
        perform_script("480", "WV__Demo_Build_Context"),
        exit_script("GetAsText ( Get ( ScriptResult ) )"),
        end_if(),
        set_variable("$_select_action", '$_type = "hybrid.select_movie"'),
        set_variable("$_set_band_action", '$_type = "hybrid.set_rating_band"'),
        set_variable("$_clear_band_action", '$_type = "hybrid.clear_rating_band"'),
        set_variable("$_rating_lo_raw", 'GetAsText ( GetField ( "FOCUS::g_wv_rating_lo" ) )'),
        set_variable("$_rating_hi_raw", 'GetAsText ( GetField ( "FOCUS::g_wv_rating_hi" ) )'),
        set_variable("$_band_active", 'not IsEmpty ( $_rating_lo_raw ) and not IsEmpty ( $_rating_hi_raw ) and\nGetAsNumber ( $_rating_lo_raw ) <= GetAsNumber ( $_rating_hi_raw )'),
        set_variable("$_rating_lo", 'Case ( $_band_active ; GetAsNumber ( $_rating_lo_raw ) ; "" )'),
        set_variable("$_rating_hi", 'Case ( $_band_active ; GetAsNumber ( $_rating_hi_raw ) ; "" )'),
        set_variable("$_band_label", 'Case ( $_band_active ; "Ratings " & $_rating_lo & "–" & $_rating_hi ; "All ratings" )'),
        set_variable("$_genre_id", 'GetAsText ( GetField ( "FOCUS::g_wv_demo_genre_id" ) )'),
        set_variable("$_row_count", 'ValueCount ( JSONListKeys ( $_context_json ; "ranked_view.rows" ) )'),
        if_step("$_set_band_action or $_clear_band_action"),
        freeze_window(),
        if_step("IsEmpty ( $_genre_id ) and not $_band_active"),
        show_all_records(),
        set_variable("$_find_error", "0"),
        else_step(),
        enter_find_mode(),
        if_step("not IsEmpty ( $_genre_id )"),
        set_field("MOVIE_GENRE", "15", "id_genre", '"==" & $_genre_id'),
        end_if(),
        if_step("$_band_active"),
        set_field("MOVIE_GLOBAL_RATING", "16", "global_rating", 'GetAsText ( $_rating_lo ) & "..." & GetAsText ( $_rating_hi )'),
        end_if(),
        perform_find(),
        set_variable("$_find_error", "Get ( LastError )"),
        end_if(),
        sort_records("MOVIE_GLOBAL_RATING", "21", "global_rank_order"),
        end_if(),
        set_variable("$_selected_movie_id", 'GetAsText ( GetField ( "FOCUS::g_wv_demo_movie_id" ) )'),
        set_variable("$_current_movie_id", 'Case ( Get ( FoundCount ) > 0 ; GetAsText ( MOVIE_GLOBAL_RATING::id_movie ) ; "" )'),
        set_field_by_name("FOCUS::g_wv_demo_movie_id", "$_selected_movie_id"),
        set_variable("$_rows_json", 'JSONGetElement ( $_context_json ; "ranked_view.rows" )'),
        set_variable("$_rows_json", """While (
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
)"""),
        set_variable("$_context_json", """JSONSetElement ( $_context_json
  ; [ "__wv.ts" ; Get ( CurrentTimestamp ) ; JSONString ]
  ; [ "ranked_view.rating_band.active" ; $_band_active ; JSONBoolean ]
  ; [ "ranked_view.rating_band.rating_lo" ; Case ( $_band_active ; $_rating_lo ; "" ) ; Case ( $_band_active ; JSONNumber ; JSONNull ) ]
  ; [ "ranked_view.rating_band.rating_hi" ; Case ( $_band_active ; $_rating_hi ; "" ) ; Case ( $_band_active ; JSONNumber ; JSONNull ) ]
  ; [ "ranked_view.rating_band.label" ; $_band_label ; JSONString ]
  ; [ "ranked_view.selected_movie_id" ; $_selected_movie_id ; JSONString ]
  ; [ "ranked_view.native_found_count" ; Get ( FoundCount ) ; JSONNumber ]
  ; [ "ranked_view.current_record_number" ; Case ( Get ( FoundCount ) > 0 ; Get ( RecordNumber ) ; 0 ) ; JSONNumber ]
  ; [ "ranked_view.current_record_id" ; $_current_movie_id ; JSONString ]
  ; [ "ranked_view.rows" ; $_rows_json ; JSONArray ]
  ; [ "actions.count" ; GetAsNumber ( GetField ( "FOCUS::g_wv_action_count" ) ) ; JSONNumber ]
  ; [ "actions.last_type" ; $_type ; JSONString ]
  ; [ "actions.status" ; GetAsText ( GetField ( "FOCUS::g_wv_action_status" ) ) ; JSONString ]
)"""),
        set_field_by_name("FOCUS::g_wv_context_json", "JSONFormatElements ( $_context_json )"),
        exit_script("$_context_json"),
    ]
    root.extend(steps)
    return root


def build_persistent_webviewer_loader() -> ET.Element:
    root = ET.parse(SHARED_LOADER_SOURCE).getroot()

    for expected in [
        "FULL REPLACEMENT for script: . webviewer . load ( index ; -object_name )",
        "Select all existing steps in this script, paste this snippet, then smoke test.",
    ]:
        if root[0].findtext("Text") != expected:
            raise ValueError(f"shared loader instruction did not match: {expected}")
        root.remove(root[0])

    history = root[3]
    history_text = history.findtext("Text") or ""
    if not history_text.startswith(" Modified:\t28 Jan 2026"):
        raise ValueError("shared loader history did not match the reviewed source")
    history.find("Text").text = (
        " Modified:\t16 Aug 2026, 00hr07PT — Lon Cook — lon@portagebay.com : preserve rendered data URLs by object so record navigation can retain an already-loaded Web Viewer.\n"
        "  \t\t\t"
        + history_text.removeprefix(" Modified:\t")
    )

    viewer_steps = [
        (index, step) for index, step in enumerate(root)
        if step.get("name") == "Set Web Viewer"
    ]
    if len(viewer_steps) != 1:
        raise ValueError(f"expected one Set Web Viewer step, found {len(viewer_steps)}")
    viewer_index, _ = viewer_steps[0]
    root.insert(
        viewer_index,
        set_variable(
            "$$wv_url_map",
            'JSONSetElement (\n  Case (\n    IsEmpty ( $$wv_url_map ) or JSONFormatElements ( $$wv_url_map ) = "?" ;\n    "{}" ;\n    $$wv_url_map\n  )\n  ; [ $_object_name ; $_url ; JSONString ]\n)',
        ),
    )
    return root


def build_native_row_script() -> ET.Element:
    root = ET.Element("fmxmlsnippet", {"type": "FMObjectList"})
    steps = [
        comment(" Purpose:\tAcknowledge the current native MOVIE row as FileMaker-owned hybrid selection and refresh both surfaces."),
        comment(" In:\t\t\tGet ( ScriptParameter ) as stable MOVIE::ID; falls back to the current MOVIE record."),
        comment(" Out:\t\tJSON status object."),
        comment(" Anchor:\t\tMOVIE on WV Framework - Hybrid."),
        comment(" Calls:\t\tWV__Demo_Apply_Hybrid_Context, WV__Demo_Push_Context."),
        comment(" Modified:\t16 Aug 2026, 18hr12PT — Lon Cook — lon@portagebay.com : patch selection context without rebuilding SQL or changing the native found set."),
        comment(" Modified:\t15 Aug 2026, 23hr32PT — Lon Cook — lon@portagebay.com : push fresh acknowledgement context into the loaded Web Viewer without reloading it."),
        comment(" Modified:\t15 Aug 2026, 21hr40PT — Lon Cook — lon@portagebay.com : accept the clicked native row ID instead of relying on the previously active record."),
        comment(" Modified:\t15 Aug 2026, 19hr31PT — Lon Cook — lon@portagebay.com : created"),
        parse_step('<Step enable="True" id="86" name="Set Error Capture"><Set state="True" /></Step>'),
        set_variable("$_movie_id", """Let ( [
  p = GetAsText ( Get ( ScriptParameter ) )
] ;
  Case (
    not IsEmpty ( p ) ; p ;
    GetAsText ( MOVIE::ID )
  )
)"""),
        if_step('Get ( FoundCount ) = 0 or IsEmpty ( $_movie_id )'),
        exit_script('JSONSetElement ( "{}"\n  ; [ "ok" ; 0 ; JSONBoolean ]\n  ; [ "error" ; "no_native_movie" ; JSONString ]\n)'),
        end_if(),
        set_variable("$_count", 'GetAsNumber ( GetField ( "FOCUS::g_wv_action_count" ) ) + 1'),
        set_variable("$_status", '"Selected native movie " & $_movie_id & " from native list"'),
        set_field_by_name("FOCUS::g_wv_demo_movie_id", "$_movie_id"),
        set_field_by_name("FOCUS::g_wv_action_json", 'JSONFormatElements ( JSONSetElement ( "{}"\n  ; [ "__wv_action.version" ; 1 ; JSONNumber ]\n  ; [ "__wv_action.source" ; "filemaker.native.hybrid_list" ; JSONString ]\n  ; [ "__wv_action.page" ; 43 ; JSONNumber ]\n  ; [ "type" ; "hybrid.select_movie" ; JSONString ]\n  ; [ "payload.movie_id" ; $_movie_id ; JSONString ]\n) )'),
        set_field_by_name("FOCUS::g_wv_action_type", '"hybrid.select_movie"'),
        set_field_by_name("FOCUS::g_wv_action_count", "$_count"),
        set_field_by_name("FOCUS::g_wv_action_status", "$_status"),
        perform_script("502", "WV__Demo_Apply_Hybrid_Context"),
        perform_script("482", "WV__Demo_Push_Context"),
        set_variable("$_push_result", "GetAsText ( Get ( ScriptResult ) )"),
        exit_script('JSONSetElement ( "{}"\n  ; [ "ok" ; 1 ; JSONBoolean ]\n  ; [ "type" ; "hybrid.select_movie" ; JSONString ]\n  ; [ "selected_movie_id" ; $_movie_id ; JSONString ]\n  ; [ "push_result" ; $_push_result ; JSONString ]\n)'),
    ]
    root.extend(steps)
    return root


def validate(root: ET.Element, label: str) -> None:
    if root.tag != "fmxmlsnippet" or root.get("type") != "FMObjectList":
        raise ValueError(f"{label}: wrong paste shape")
    if any(step.tag != "Step" for step in root):
        raise ValueError(f"{label}: unexpected non-Step child")
    text = ET.tostring(root, encoding="unicode")
    if "≠" in text:
        raise ValueError(f"{label}: Unicode not-equal operator found")
    if "<Script>" in text or "<?xml" in text:
        raise ValueError(f"{label}: disallowed wrapper or declaration")
    for step in root:
        if step.get("name") == "Loop":
            flush = step.find("FlushType")
            if flush is None or flush.get("value") != "Always":
                raise ValueError(f"{label}: Loop must use FlushType=Always")


def normalize_loop_flush(root: ET.Element) -> None:
    for step in root:
        if step.get("name") != "Loop":
            continue
        for child in list(step):
            if child.tag in {"FlushType", "Restore"}:
                step.remove(child)
        ET.SubElement(step, "FlushType", {"value": "Always"})


def write(root: ET.Element, path: Path) -> None:
    normalize_loop_flush(root)
    validate(root, path.name)
    ET.indent(root, space="  ")
    path.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        OUTPUT_DIR / "WV__Demo_Build_Context_Hybrid.fmxmlsnippet": build_context(),
        OUTPUT_DIR / "WV__Demo_Handle_Action_Hybrid.fmxmlsnippet": build_handler(),
        OUTPUT_DIR / "WV__Demo_Apply_Hybrid_Context.fmxmlsnippet": build_apply_hybrid_context_script(),
        OUTPUT_DIR / "WV__Demo_Select_Native_Row.fmxmlsnippet": build_native_row_script(),
        OUTPUT_DIR / "WebViewer_Load_Persistent_URL.fmxmlsnippet": build_persistent_webviewer_loader(),
    }
    for path, root in outputs.items():
        write(root, path)
        print(path)


if __name__ == "__main__":
    main()
