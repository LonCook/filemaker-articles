#!/usr/bin/env python3
"""Emit Go to List of Records using FileMaker 26's verified RowList shape."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import xml.etree.ElementTree as ET


ARTICLE_FOUR = Path(__file__).resolve().parents[2]
SNIPPET_DIR = ARTICLE_FOUR / "fmxmlsnippets"

BUILD_SOURCE = SNIPPET_DIR / "WV__Demo_Build_Context_ROWID_List_v3.fmxmlsnippet"
APPLY_SOURCE = SNIPPET_DIR / "WV__Demo_Apply_Hybrid_Context_ROWID_List_v2.fmxmlsnippet"
BUILD_OUTPUT = SNIPPET_DIR / "WV__Demo_Build_Context_ROWID_List_v4.fmxmlsnippet"
APPLY_OUTPUT = SNIPPET_DIR / "WV__Demo_Apply_Hybrid_Context_ROWID_List_v4.fmxmlsnippet"

EXPECTED_SOURCE_HASHES = {
    BUILD_SOURCE: "2959fc22906107e438d36338dcc615d999817ca3a5dbbe4ccd1a9232fb6b8fc8",
    APPLY_SOURCE: "5293eab2fd3ef34d6bab0fc8eaa1eaf4f4e4acb2ae48431b6abdcb7bfce3489c",
}

NEW_HISTORY = (
    " Modified:\t16 Aug 2026, 20hr43PT — Lon Cook — lon@portagebay.com : "
    "use the verified RowList calculation wrapper required by Go to List of Records."
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
    step.clear()
    step.attrib.update({"enable": "True", "id": "228", "name": "Go to List of Records"})
    ET.SubElement(step, "ShowInNewWindow", {"state": "False"})
    ET.SubElement(step, "LayoutDestination", {"value": "CurrentLayout"})
    row_list = ET.SubElement(step, "RowList")
    ET.SubElement(row_list, "Calculation").text = "$_record_ids_for_step"
    ET.SubElement(
        step,
        "NewWndStyles",
        {
            "Style": "Document",
            "Close": "Yes",
            "Minimize": "Yes",
            "Maximize": "Yes",
            "Resize": "Yes",
            "Styles": "3606018",
        },
    )

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

    assert [child.tag for child in output_step] == [
        "ShowInNewWindow",
        "LayoutDestination",
        "RowList",
        "NewWndStyles",
    ]
    assert output_step.findtext("RowList/Calculation") == "$_record_ids_for_step"
    assert output_step.find("ShowInNewWindow").attrib == {"state": "False"}
    assert output_step.find("LayoutDestination").attrib == {"value": "CurrentLayout"}
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

    for source_path, output_path in (
        (BUILD_SOURCE, BUILD_OUTPUT),
        (APPLY_SOURCE, APPLY_OUTPUT),
    ):
        source = parse(source_path)
        output = build(source)
        validate(source, output)
        write(output, output_path)
        print(f"Wrote {output_path.name}: sha256={digest(output_path)}")

    print("Validated: step-only FMObjectList; verified RowList calculation wrapper;")
    print("all other steps and every prior live-script history entry preserved verbatim.")


if __name__ == "__main__":
    main()
