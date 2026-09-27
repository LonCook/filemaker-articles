#!/usr/bin/env python3
"""Emit the exact typed V2 calculation parameter for Go to List of Records."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import xml.etree.ElementTree as ET


ARTICLE_FOUR = Path(__file__).resolve().parents[2]
SNIPPET_DIR = ARTICLE_FOUR / "fmxmlsnippets"

BUILD_SOURCE = SNIPPET_DIR / "WV__Demo_Build_Context_ROWID_List_v2.fmxmlsnippet"
APPLY_SOURCE = SNIPPET_DIR / "WV__Demo_Apply_Hybrid_Context_ROWID_List_v2.fmxmlsnippet"
BUILD_OUTPUT = SNIPPET_DIR / "WV__Demo_Build_Context_ROWID_List_v3.fmxmlsnippet"
APPLY_OUTPUT = SNIPPET_DIR / "WV__Demo_Apply_Hybrid_Context_ROWID_List_v3.fmxmlsnippet"

EXPECTED_SOURCE_HASHES = {
    BUILD_SOURCE: "9e2df18b4bedf90af2589a83e10c70bb1b174e18eafbe8eacf166d10a64eefeb",
    APPLY_SOURCE: "5293eab2fd3ef34d6bab0fc8eaa1eaf4f4e4acb2ae48431b6abdcb7bfce3489c",
}

NEW_HISTORY = (
    " Modified:\t16 Aug 2026, 20hr28PT — Lon Cook — lon@portagebay.com : "
    "supply the typed, positioned FileMaker 22+ calculation parameter required by Go to List of Records."
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def parse(path: Path) -> ET.Element:
    root = ET.parse(path).getroot()
    assert root.tag == "fmxmlsnippet" and root.get("type") == "FMObjectList"
    assert all(child.tag == "Step" for child in root)
    return root


def history(root: ET.Element) -> list[str]:
    return [
        step.findtext("Text", default="")
        for step in root
        if step.get("name") == "# (comment)"
        and step.findtext("Text", default="").startswith(" Modified:\t")
    ]


def first_history_index(root: ET.Element) -> int:
    for index, step in enumerate(root):
        if (
            step.get("name") == "# (comment)"
            and step.findtext("Text", default="").startswith(" Modified:\t")
        ):
            return index
    raise AssertionError("No existing history")


def comment(text: str) -> ET.Element:
    step = ET.Element("Step", {"enable": "True", "id": "89", "name": "# (comment)"})
    ET.SubElement(step, "Text").text = text
    return step


def go_list(root: ET.Element) -> ET.Element:
    matches = [step for step in root if step.get("name") == "Go to List of Records"]
    assert len(matches) == 1
    return matches[0]


def canonical(element: ET.Element) -> bytes:
    return ET.tostring(element, encoding="utf-8", short_empty_elements=True)


def build(source: ET.Element) -> ET.Element:
    root = deepcopy(source)
    old_history = history(source)
    root.insert(first_history_index(root), comment(NEW_HISTORY))

    step = go_list(root)
    assert step.attrib == {"enable": "True", "id": "228", "name": "Go to List of Records"}
    assert [child.tag for child in step] == ["Parameter"]
    assert step.findtext("Parameter/Calculation") == "$_record_ids_for_step"

    step.clear()
    step.attrib.update({"enable": "True", "id": "228", "name": "Go to List of Records"})
    parameter = ET.SubElement(step, "Parameter", {"type": "Calculation"})
    calculation_container = ET.SubElement(
        parameter, "Calculation", {"datatype": "1", "position": "7"}
    )
    ET.SubElement(calculation_container, "Calculation").text = "$_record_ids_for_step"

    assert history(root) == [NEW_HISTORY, *old_history]
    return root


def validate(source: ET.Element, output: ET.Element) -> None:
    source_copy = deepcopy(source)
    output_copy = deepcopy(output)
    source_step = go_list(source_copy)
    output_step = go_list(output_copy)
    assert list(source_copy).index(source_step) + 1 == list(output_copy).index(output_step)
    source_copy.remove(source_step)
    output_copy.remove(output_step)
    output_copy.remove(output_copy[first_history_index(output_copy)])
    assert canonical(source_copy) == canonical(output_copy)

    assert [child.tag for child in output_step] == ["Parameter"]
    parameter = output_step.find("Parameter")
    assert parameter is not None and parameter.attrib == {"type": "Calculation"}
    outer_calc = parameter.find("Calculation")
    assert outer_calc is not None
    assert outer_calc.attrib == {"datatype": "1", "position": "7"}
    assert [child.tag for child in outer_calc] == ["Calculation"]
    assert outer_calc.findtext("Calculation") == "$_record_ids_for_step"
    assert not any(
        step.get("name") in {"Enter Find Mode", "New Record/Request", "Perform Find"}
        for step in output
    )


def write(root: ET.Element, path: Path) -> None:
    ET.indent(root, space="  ")
    path.write_text(
        ET.tostring(root, encoding="unicode", short_empty_elements=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    for path, expected in EXPECTED_SOURCE_HASHES.items():
        assert digest(path) == expected, f"Source drift: {path.name}"

    build_source = parse(BUILD_SOURCE)
    apply_source = parse(APPLY_SOURCE)
    build_output = build(build_source)
    apply_output = build(apply_source)
    validate(build_source, build_output)
    validate(apply_source, apply_output)
    write(build_output, BUILD_OUTPUT)
    write(apply_output, APPLY_OUTPUT)

    print(f"Wrote {BUILD_OUTPUT.name}: sha256={digest(BUILD_OUTPUT)}")
    print(f"Wrote {APPLY_OUTPUT.name}: sha256={digest(APPLY_OUTPUT)}")
    print("Validated: typed Calculation parameter; datatype 1; position 7; nested calculation;")
    print("all other steps and every prior history entry preserved verbatim.")


if __name__ == "__main__":
    main()
