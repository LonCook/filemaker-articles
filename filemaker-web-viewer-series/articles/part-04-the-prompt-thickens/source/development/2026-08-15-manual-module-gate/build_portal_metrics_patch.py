#!/usr/bin/env python3
"""Build the post-acceptance Article 4 portal metric display patch."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET


HERE = Path(__file__).resolve().parent
ARTICLE_FOUR = HERE.parents[1]
DDR = ARTICLE_FOUR / "Flicks_WebViewer_Framework_04_HybridInterface_fmp12.xml"
OUTPUT = ARTICLE_FOUR / "fmxmlsnippets"
METRICS_STAMP = "18 Aug 2026, 23hr43PT — Lon Cook — lon@portagebay.com"
REFRESH_STAMP = "18 Aug 2026, 23hr58PT — Lon Cook — lon@portagebay.com"


def concrete_steps(root: ET.Element, name: str) -> list[ET.Element]:
    matches = []
    for script in root.iter("Script"):
        if script.get("name") != name:
            continue
        step_list = script.find("StepList")
        if step_list is not None and len(step_list):
            matches.append(step_list)
    if len(matches) != 1:
        raise ValueError(f"Expected one concrete {name}, found {len(matches)}")
    return [deepcopy(step) for step in matches[0]]


def comment(text: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "89", "name": "# (comment)"})
    ET.SubElement(step, "Text").text = text
    return step


def set_variable(name: str, calculation: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "141", "name": "Set Variable"})
    value = ET.SubElement(step, "Value")
    ET.SubElement(value, "Calculation").text = calculation
    repetition = ET.SubElement(step, "Repetition")
    ET.SubElement(repetition, "Calculation").text = "1"
    ET.SubElement(step, "Name").text = name
    return step


def variable_name(step: ET.Element) -> str:
    return step.findtext("Name") or ""


def calculation(step: ET.Element) -> str:
    node = step.find(".//Calculation")
    return "" if node is None or node.text is None else node.text


def old_history(steps: list[ET.Element]) -> list[str]:
    result = []
    for step in steps:
        if step.get("name") != "# (comment)":
            break
        text = step.findtext("Text") or ""
        if text.lstrip().startswith("Modified:"):
            result.append(text)
    return result


def insert_history(steps: list[ET.Element], stamp: str, message: str) -> None:
    for index, step in enumerate(steps):
        if step.get("name") != "# (comment)":
            break
        if (step.findtext("Text") or "").lstrip().startswith("Modified:"):
            steps.insert(index, comment(f" Modified:\t{stamp} : {message}"))
            return
    raise ValueError("No existing modification history found")


def update_header_line(steps: list[ET.Element], prefix: str, text: str) -> None:
    for step in steps:
        if step.get("name") != "# (comment)":
            break
        node = step.find("Text")
        if node is not None and (node.text or "").lstrip().startswith(prefix):
            node.text = text
            return
    raise ValueError(f"Header line not found: {prefix}")


def strip_ddr_display_nodes(steps: list[ET.Element]) -> None:
    for step in steps:
        for parent in step.iter():
            for child in list(parent):
                if child.tag in {"StepText", "DisplayCalculation", "DisableStepCollapsed", "CurrentScript"}:
                    parent.remove(child)


def refresh_object(name: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "167", "name": "Refresh Object"})
    object_name = ET.SubElement(step, "ObjectName")
    ET.SubElement(object_name, "Calculation").text = f'"{name}"'
    repetition = ET.SubElement(step, "Repetition")
    ET.SubElement(repetition, "Calculation").text = "1"
    return step


def metric_refresh_steps() -> list[ET.Element]:
    return [
        refresh_object("metric.portal_count"),
        refresh_object("metric.selected_row"),
    ]


def write_script(filename: str, steps: list[ET.Element]) -> Path:
    strip_ddr_display_nodes(steps)
    root = ET.Element("fmxmlsnippet", {"type": "FMObjectList"})
    root.extend(steps)
    ET.indent(root, space="  ")
    path = OUTPUT / filename
    path.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")
    return path


def patch_build(root: ET.Element) -> tuple[Path, list[str]]:
    steps = concrete_steps(root, "WV__Demo_Build_Context")
    history = old_history(steps)
    insert_history(
        steps,
        METRICS_STAMP,
        "publish portal count and selected-row position to private merge variables for the SOLUTION-hosted layout.",
    )
    insert_history(
        steps,
        REFRESH_STAMP,
        "refresh only the named portal metric text objects after publishing merge variables; keep wv_main untouched.",
    )
    update_header_line(
        steps,
        "Out:",
        " Out:\t\tFOCUS context/status, SOLUTION__all::g_wv_hybrid_movie_ids, $$wv_hybrid_portal_count, and $$wv_hybrid_selected_position; exits with raw context JSON.",
    )
    rows_if = next(
        index for index, step in enumerate(steps)
        if step.get("name") == "If" and calculation(step).strip() == 'Left ( $_rows_text ; 1 ) = "?"'
    )
    error_context = next(
        index for index in range(rows_if + 1, len(steps))
        if variable_name(steps[index]) == "$_context_json"
    )
    steps[error_context:error_context] = [
        set_variable("$$wv_hybrid_portal_count", "0"),
        set_variable("$$wv_hybrid_selected_position", "0"),
    ] + metric_refresh_steps()
    selected_index = next(
        index for index, step in enumerate(steps)
        if variable_name(step) == "$_selected_position"
    )
    steps[selected_index + 1:selected_index + 1] = [
        set_variable("$$wv_hybrid_portal_count", "$_portal_count"),
        set_variable("$$wv_hybrid_selected_position", "$_selected_position"),
    ] + metric_refresh_steps()
    return write_script("WV__Demo_Build_Context_Portal_Metrics_v2.fmxmlsnippet", steps), history


def patch_apply(root: ET.Element) -> tuple[Path, list[str]]:
    steps = concrete_steps(root, "WV__Demo_Apply_Hybrid_Context")
    history = old_history(steps)
    insert_history(
        steps,
        METRICS_STAMP,
        "publish portal count and selected-row position to private merge variables after every acknowledged interaction.",
    )
    insert_history(
        steps,
        REFRESH_STAMP,
        "refresh only the named portal metric text objects after publishing merge variables; keep wv_main untouched.",
    )
    update_header_line(
        steps,
        "Out:",
        " Out:\t\tFOCUS::g_wv_context_json, SOLUTION__all::g_wv_hybrid_movie_ids, $$wv_hybrid_portal_count, and $$wv_hybrid_selected_position; exits with raw context JSON.",
    )
    selected_index = next(
        index for index, step in enumerate(steps)
        if variable_name(step) == "$_selected_position"
    )
    steps[selected_index + 1:selected_index + 1] = [
        set_variable("$$wv_hybrid_portal_count", "$_portal_count"),
        set_variable("$$wv_hybrid_selected_position", "$_selected_position"),
    ] + metric_refresh_steps()
    return write_script("WV__Demo_Apply_Hybrid_Context_Portal_Metrics_v2.fmxmlsnippet", steps), history


def set_text(obj: ET.Element, value: str) -> None:
    nodes = obj.findall(".//CharacterStyleVector/Style/Data") + obj.findall(".//ParagraphStyleVector/Style/Data")
    if not nodes:
        raise ValueError(f"Object {obj.get('key')} has no text nodes")
    for node in nodes:
        node.text = value


def set_bounds(obj: ET.Element, top: str, left: str, bottom: str, right: str) -> None:
    bounds = obj.find("Bounds")
    if bounds is None:
        raise ValueError(f"Object {obj.get('key')} has no bounds")
    bounds.attrib.update(top=top, left=left, bottom=bottom, right=right)


def build_layout(root: ET.Element) -> Path:
    layout = next(item for item in root.iter("Layout") if item.get("id") == "150")
    source = {obj.get("key"): obj for obj in layout.findall("Object")}
    definitions = (
        ("89", "711", "portal_count", None, "0", ("286.0000000", "972.0000000", "307.0000000", "1071.0000000")),
        ("90", "712", "<<ƒ:$$wv_hybrid_portal_count>>", "metric.portal_count", "168", ("283.0000000", "1089.0000000", "304.0000000", "1273.0000000")),
        ("91", "713", "selected_row", None, "0", ("310.0000000", "972.0000000", "331.0000000", "1071.0000000")),
        ("92", "714", "<<ƒ:$$wv_hybrid_selected_position>>", "metric.selected_row", "168", ("307.0000000", "1063.0000000", "328.0000000", "1273.0000000")),
    )
    objects = []
    for old_key, new_key, value, name, text_flags, bounds in definitions:
        obj = deepcopy(source[old_key])
        obj.set("key", new_key)
        obj.set("LabelKey", "0")
        if name is not None:
            obj.set("name", name)
        text_obj = obj.find("TextObj")
        if text_obj is None:
            raise ValueError(f"Object {old_key} has no TextObj")
        text_obj.set("flags", text_flags)
        set_bounds(obj, *bounds)
        set_text(obj, value)
        objects.append(obj)
    snippet = ET.Element("fmxmlsnippet", {"type": "LayoutObjectList"})
    container = ET.SubElement(snippet, "Layout", {
        "enclosingRectTop": "283.0000000",
        "enclosingRectLeft": "972.0000000",
        "enclosingRectBottom": "331.0000000",
        "enclosingRectRight": "1273.0000000",
    })
    container.extend(objects)
    ET.indent(snippet, space="  ")
    path = OUTPUT / "WV_Framework_Hybrid_Portal_Metrics_v2.fmxmlsnippet"
    path.write_text(ET.tostring(snippet, encoding="unicode") + "\n", encoding="utf-8")
    return path


def validate_script(path: Path, history: list[str], expected_refreshes: int) -> None:
    root = ET.parse(path).getroot()
    assert root.tag == "fmxmlsnippet" and root.get("type") == "FMObjectList"
    assert all(child.tag == "Step" for child in root)
    new_history = [
        step.findtext("Text") or ""
        for step in root
        if step.get("name") == "# (comment)"
        and (step.findtext("Text") or "").lstrip().startswith("Modified:")
    ]
    assert new_history[2:] == history
    assert "refresh only the named portal metric text objects" in new_history[0]
    assert "publish portal count and selected-row position" in new_history[1]
    names = {step.get("name") for step in root}
    forbidden = {
        "Enter Find Mode", "Perform Find", "New Record/Request",
        "Go to List of Records", "Go to Record/Request/Page", "Install OnTimer Script",
    }
    assert not names.intersection(forbidden)
    assert "Refresh Window" not in names
    refreshes = [step for step in root if step.get("name") == "Refresh Object"]
    assert len(refreshes) == expected_refreshes
    refresh_targets = [calculation(step) for step in refreshes]
    assert refresh_targets.count('"metric.portal_count"') == expected_refreshes // 2
    assert refresh_targets.count('"metric.selected_row"') == expected_refreshes // 2
    text = path.read_text(encoding="utf-8")
    assert "$$wv_hybrid_portal_count" in text
    assert "$$wv_hybrid_selected_position" in text
    assert "≠" not in text


def main() -> None:
    root = ET.parse(DDR).getroot()
    build_path, build_history = patch_build(root)
    apply_path, apply_history = patch_apply(root)
    validate_script(build_path, build_history, 4)
    validate_script(apply_path, apply_history, 2)
    layout_path = build_layout(root)
    layout_root = ET.parse(layout_path).getroot()
    assert layout_root.get("type") == "LayoutObjectList"
    layout_values = [
        node.text or ""
        for node in layout_root.findall(".//CharacterStyleVector/Style/Data")
    ]
    assert "<<ƒ:$$wv_hybrid_portal_count>>" in layout_values
    assert "<<ƒ:$$wv_hybrid_selected_position>>" in layout_values
    named = {obj.get("name"): obj for obj in layout_root.findall(".//Object") if obj.get("name")}
    assert named["metric.portal_count"].find("TextObj").get("flags") == "168"
    assert named["metric.selected_row"].find("TextObj").get("flags") == "168"
    for path in (build_path, apply_path, layout_path):
        print(path)
    print("Static validation passed: histories preserved; native merge-variable syntax verified; only named metric objects refresh; wv_main untouched.")


if __name__ == "__main__":
    main()
