#!/usr/bin/env python3
"""Correct the FileMaker 22+ Go to List of Records FMXML paste container."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import xml.etree.ElementTree as ET


ARTICLE_FOUR = Path(__file__).resolve().parents[2]
SNIPPET_DIR = ARTICLE_FOUR / "fmxmlsnippets"

BUILD_SOURCE = SNIPPET_DIR / "WV__Demo_Build_Context_ROWID_List.fmxmlsnippet"
APPLY_SOURCE = SNIPPET_DIR / "WV__Demo_Apply_Hybrid_Context_ROWID_List.fmxmlsnippet"

BUILD_OUTPUT = SNIPPET_DIR / "WV__Demo_Build_Context_ROWID_List_v2.fmxmlsnippet"
APPLY_OUTPUT = SNIPPET_DIR / "WV__Demo_Apply_Hybrid_Context_ROWID_List_v2.fmxmlsnippet"

EXPECTED_SOURCE_HASHES = {
    BUILD_SOURCE: "cb6a398bd3640912f9398b15b4c75ae30f6e19b2d75936c9f9e5207604e68ca0",
    APPLY_SOURCE: "13122794c07e2f6aa5392c1b482ed40199768e49b2fe7b6af669868aeb69abe0",
}

NEW_BUILD_HISTORY = (
    " Modified:\t16 Aug 2026, 20hr06PT — Lon Cook — lon@portagebay.com : "
    "correct the FileMaker 22+ Go to List of Records FMXML container so its record-ID calculation survives paste."
)
NEW_APPLY_HISTORY = (
    " Modified:\t16 Aug 2026, 20hr06PT — Lon Cook — lon@portagebay.com : "
    "correct the FileMaker 22+ Go to List of Records FMXML container so its record-ID calculation survives paste."
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def parse(path: Path) -> ET.Element:
    root = ET.parse(path).getroot()
    if root.tag != "fmxmlsnippet" or root.get("type") != "FMObjectList":
        raise AssertionError(f"Unexpected FMXML root in {path.name}")
    if any(child.tag != "Step" for child in root):
        raise AssertionError(f"Non-Step child in {path.name}")
    return root


def comment(text: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "89", "name": "# (comment)"})
    ET.SubElement(step, "Text").text = text
    return step


def history(root: ET.Element) -> list[str]:
    return [
        step.findtext("Text", default="")
        for step in root
        if step.get("name") == "# (comment)"
        and step.findtext("Text", default="").startswith(" Modified:\t")
    ]


def history_insert_index(root: ET.Element) -> int:
    for index, step in enumerate(root):
        if (
            step.get("name") == "# (comment)"
            and step.findtext("Text", default="").startswith(" Modified:\t")
        ):
            return index
    raise AssertionError("Existing history not found")


def go_to_list_step(root: ET.Element) -> ET.Element:
    matches = [step for step in root if step.get("name") == "Go to List of Records"]
    if len(matches) != 1:
        raise AssertionError(f"Expected one Go to List of Records step, found {len(matches)}")
    return matches[0]


def canonical(element: ET.Element) -> bytes:
    return ET.tostring(element, encoding="utf-8", short_empty_elements=True)


def corrected(source: ET.Element, new_history: str) -> ET.Element:
    root = deepcopy(source)
    old_history = history(source)
    root.insert(history_insert_index(root), comment(new_history))

    step = go_to_list_step(root)
    if [child.tag for child in step] != ["Calculation", "LayoutDestination"]:
        raise AssertionError("Unexpected pre-correction Go to List of Records shape")
    if step.findtext("Calculation") != "$_record_ids_for_step":
        raise AssertionError("Unexpected record-ID calculation")
    layout = step.find("LayoutDestination")
    if layout is None or layout.get("value") != "CurrentLayout":
        raise AssertionError("Unexpected pre-correction layout destination")

    # Go to List of Records is a FileMaker 22+ V2 step. Its FMXML deserializer
    # reads the step-specific calculation only from a Parameter container.
    # Omitting an explicit layout child retains the step's verified Current
    # Layout default and avoids inventing a V2 LayoutReferenceContainer shape.
    step.clear()
    step.attrib.update({"enable": "True", "id": "228", "name": "Go to List of Records"})
    parameter = ET.SubElement(step, "Parameter")
    ET.SubElement(parameter, "Calculation").text = "$_record_ids_for_step"

    if history(root) != [new_history, *old_history]:
        raise AssertionError("Header history was not preserved verbatim")
    return root


def validate_only_authorized_changes(
    source: ET.Element, output: ET.Element, new_history: str
) -> None:
    source_copy = deepcopy(source)
    output_copy = deepcopy(output)

    source_go_list = go_to_list_step(source_copy)
    output_go_list = go_to_list_step(output_copy)
    source_index = list(source_copy).index(source_go_list)
    output_index = list(output_copy).index(output_go_list)
    assert source_index + 1 == output_index

    source_copy.remove(source_go_list)
    output_copy.remove(output_go_list)
    output_copy.remove(output_copy[history_insert_index(output_copy)])
    assert canonical(source_copy) == canonical(output_copy)

    assert output_go_list.get("id") == "228"
    assert output_go_list.get("enable") == "True"
    assert [child.tag for child in output_go_list] == ["Parameter"]
    parameter = output_go_list.find("Parameter")
    assert parameter is not None
    assert [child.tag for child in parameter] == ["Calculation"]
    assert parameter.findtext("Calculation") == "$_record_ids_for_step"
    assert output_go_list.find("LayoutDestination") is None
    assert output_go_list.find("LayoutReferenceContainer") is None
    assert output_go_list.find("WindowReference") is None

    assert history(output)[0] == new_history
    assert all(step.tag == "Step" for step in output)
    assert not any(
        step.get("name") in {"Enter Find Mode", "New Record/Request", "Perform Find"}
        for step in output
    )


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
    build_output = corrected(build_source, NEW_BUILD_HISTORY)
    apply_output = corrected(apply_source, NEW_APPLY_HISTORY)

    validate_only_authorized_changes(BUILD_SOURCE_ROOT := build_source, build_output, NEW_BUILD_HISTORY)
    validate_only_authorized_changes(APPLY_SOURCE_ROOT := apply_source, apply_output, NEW_APPLY_HISTORY)
    assert BUILD_SOURCE_ROOT is build_source and APPLY_SOURCE_ROOT is apply_source

    write(build_output, BUILD_OUTPUT)
    write(apply_output, APPLY_OUTPUT)

    print(f"Wrote {BUILD_OUTPUT.name}: {len(build_output)} steps, sha256={digest(BUILD_OUTPUT)}")
    print(f"Wrote {APPLY_OUTPUT.name}: {len(apply_output)} steps, sha256={digest(APPLY_OUTPUT)}")
    print("Static validation passed: V2 Parameter/Calculation shape; step-only FMObjectList roots;")
    print("all prior steps and header-history entries preserved; no find/request steps.")


if __name__ == "__main__":
    main()
