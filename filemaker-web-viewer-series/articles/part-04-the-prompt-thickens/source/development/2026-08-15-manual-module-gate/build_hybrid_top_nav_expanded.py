#!/usr/bin/env python3
"""Build the expanded Article 4 Hybrid Top Navigation object snippet."""

from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "hybrid-layout-objects.fmxmlsnippet"
OUTPUT = HERE / "hybrid-top-nav-expanded-diagnostics.fmxmlsnippet"


def set_bounds(obj: ET.Element, top: float, left: float, bottom: float, right: float) -> None:
    bounds = obj.find("Bounds")
    if bounds is None:
        raise ValueError(f"Object {obj.get('key')} has no Bounds")
    for name, value in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        bounds.set(name, f"{value:.7f}")


def set_text(obj: ET.Element, value: str) -> None:
    nodes = (
        obj.findall(".//CharacterStyleVector/Style/Data")
        + obj.findall(".//ParagraphStyleVector/Style/Data")
    )
    if not nodes:
        raise ValueError(f"Object {obj.get('key')} has no text nodes")
    for node in nodes:
        node.text = value


tree = ET.parse(SOURCE)
source_layout = tree.getroot().find("Layout")
if source_layout is None:
    raise ValueError("Source snippet has no Layout container")

source = {obj.get("key"): obj for obj in source_layout.findall("Object")}

# The JSON fields and their labels move into the Diagnostics popover. Body-part
# objects 109–112 are deliberately excluded: this is a Top Navigation-only paste.
top_level_keys = (
    "4",
    "46", "44", "19", "20", "23", "24", "21", "22",
    "33", "54", "35", "53", "52", "51",
    "101", "102", "103", "104", "105", "106", "107", "108",
    "29", "47", "48",
)

objects: list[ET.Element] = []
for key in top_level_keys:
    obj = deepcopy(source[key])
    if key == "4":
        set_bounds(obj, 12, 12, 420, 950)
    objects.append(obj)

# Convert the former visible Push Context button into a Diagnostics popover
# button. The original Push Context button remains available inside the panel.
diagnostics = deepcopy(source["31"])
diagnostics.set("type", "PopoverButton")
diagnostics.set("key", "201")
diagnostics.set("LabelKey", "0")
diagnostics.set("name", "popover.hybrid_diagnostics")
set_bounds(diagnostics, 372, 960, 401, 1113)
set_text(diagnostics, "Diagnostics")

button_obj = diagnostics.find("ButtonObj")
if button_obj is None:
    raise ValueError("Source Push Context button has no ButtonObj")
diagnostics.remove(button_obj)

popover_button = ET.SubElement(
    diagnostics,
    "PopoverButtonObj",
    {"buttonFlags": "0", "key": "202", "iconSize": "12", "displayType": "0"},
)
popover = ET.SubElement(
    popover_button,
    "Object",
    {"type": "Popover", "key": "202", "LabelKey": "0", "flags": "0", "rotation": "0"},
)
ET.SubElement(
    popover,
    "Bounds",
    {"top": "20.0000000", "left": "410.0000000", "bottom": "365.0000000", "right": "940.0000000"},
)
styles = ET.SubElement(popover, "Styles")
local_css = ET.SubElement(styles, "LocalCSS")
local_css.text = """self:normal .self
{
  background-image: none;
  background-color: rgba(8%,8%,8%,0.98);
  border-top-color: rgba(30%,30%,30%,1);
  border-right-color: rgba(30%,30%,30%,1);
  border-bottom-color: rgba(30%,30%,30%,1);
  border-left-color: rgba(30%,30%,30%,1);
  border-top-right-radius: 6pt 6pt;
  border-bottom-right-radius: 6pt 6pt;
  border-bottom-left-radius: 6pt 6pt;
  border-top-left-radius: 6pt 6pt;
  border-image-source: none;
  color: rgba(88%,88%,88%,1);
  box-shadow: 0pt 8pt 24pt rgba(0%,0%,0%,0.55);
}
self:normal .contents
{
  background-image: none;
  background-color: rgba(0%,0%,0%,0);
  border-top-style: none;
  border-right-style: none;
  border-bottom-style: none;
  border-left-style: none;
}
"""
title_calc = ET.SubElement(popover, "TitleCalc")
calculation = ET.SubElement(title_calc, "Calculation")
calculation.text = '"Diagnostics"'
display = ET.SubElement(title_calc, "DisplayCalculation")
chunk = ET.SubElement(display, "Chunk", {"type": "NoRef"})
chunk.text = '"Diagnostics"'

# Position 3 opens the panel above the button, keeping it inside the Top
# Navigation while overlaying the viewer only when diagnostics are requested.
popover_obj = ET.SubElement(
    popover,
    "PopoverObj",
    {"flags": "2", "position": "3", "key": "201"},
)

context_label = deepcopy(source["28"])
context_label.set("flags", "0")
set_bounds(context_label, 45, 430, 66, 550)
set_text(context_label, "Context JSON")
popover_obj.append(context_label)

context_field = deepcopy(source["27"])
context_field.set("flags", "0")
set_bounds(context_field, 68, 430, 190, 920)
popover_obj.append(context_field)

action_label = deepcopy(source["40"])
action_label.set("flags", "0")
set_bounds(action_label, 200, 430, 221, 550)
set_text(action_label, "Last Action JSON")
popover_obj.append(action_label)

action_field = deepcopy(source["39"])
action_field.set("flags", "0")
set_bounds(action_field, 223, 430, 325, 920)
popover_obj.append(action_field)

push_context = deepcopy(source["31"])
push_context.set("key", "203")
push_context.set("LabelKey", "0")
set_bounds(push_context, 332, 767, 357, 920)
popover_obj.append(push_context)

objects.append(diagnostics)

snippet = ET.Element("fmxmlsnippet", {"type": "LayoutObjectList"})
layout = ET.SubElement(
    snippet,
    "Layout",
    {
        "enclosingRectTop": "12.0000000",
        "enclosingRectLeft": "12.0000000",
        "enclosingRectBottom": "420.0000000",
        "enclosingRectRight": "1273.0000000",
    },
)
for obj in objects:
    layout.append(obj)

ET.indent(snippet, space="  ")
payload = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(snippet, encoding="unicode") + "\n"
OUTPUT.write_text(payload, encoding="utf-8")
print(OUTPUT)
print(f"top_level_objects={len(objects)}")
print("nested_diagnostics_objects=5")
