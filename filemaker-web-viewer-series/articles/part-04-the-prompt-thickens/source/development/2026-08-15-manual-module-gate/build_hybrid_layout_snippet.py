#!/usr/bin/env python3
"""Build the Article 4 Hybrid layout-object paste payload from Article 3 DDR objects."""

from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "2026-08-12-prebuild-article-03" / "Flicks_WebViewer_Framework_03_RankedViews_fmp12.xml"
OUTPUT = HERE / "hybrid-layout-objects.fmxmlsnippet"
ROW_BUTTON_OUTPUT = HERE / "hybrid-native-row-button.fmxmlsnippet"


def set_bounds(obj: ET.Element, top: float, left: float, bottom: float, right: float) -> None:
    bounds = obj.find("Bounds")
    if bounds is None:
        raise ValueError(f"Object {obj.get('key')} has no Bounds")
    for name, value in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        bounds.set(name, f"{value:.7f}")


def set_text(obj: ET.Element, value: str) -> None:
    data_nodes = obj.findall(".//CharacterStyleVector/Style/Data") + obj.findall(".//ParagraphStyleVector/Style/Data")
    if not data_nodes:
        raise ValueError(f"Object {obj.get('key')} has no text Data nodes")
    for node in data_nodes:
        node.text = value


def clone(source: dict[str, ET.Element], key: str, new_key: int, bounds: tuple[float, float, float, float]) -> ET.Element:
    obj = deepcopy(source[key])
    obj.set("key", str(new_key))
    obj.set("LabelKey", "0")
    set_bounds(obj, *bounds)
    return obj


tree = ET.parse(SOURCE)
root = tree.getroot()
layout = next(item for item in root.iter("Layout") if item.get("name") == "WV Framework - Demo")
source = {obj.get("key"): obj for obj in layout.findall("Object")}

# Verified Article 3 objects, retained with their existing names and script bindings.
objects: list[ET.Element] = []

placements = {
    "4": (12, 12, 420, 650),
    "27": (42, 670, 210, 950),
    "28": (18, 670, 39, 750),
    "39": (237, 670, 405, 950),
    "40": (213, 670, 234, 750),
    "46": (42, 1082, 63, 1273),
    "44": (66, 1082, 87, 1273),
    "19": (90, 1082, 111, 1273),
    "20": (93, 1037, 114, 1071),
    "23": (114, 1082, 135, 1273),
    "24": (117, 992, 138, 1071),
    "21": (138, 1082, 159, 1273),
    "22": (141, 1035, 162, 1071),
    "33": (162, 1082, 183, 1273),
    "54": (165, 962, 186, 1076),
    "35": (186, 1082, 207, 1273),
    "53": (189, 962, 210, 1076),
    "52": (210, 1082, 231, 1273),
    "51": (213, 962, 234, 1076),
    "29": (332, 960, 361, 1113),
    "47": (332, 1120, 361, 1273),
    "31": (372, 960, 401, 1113),
    "48": (372, 1120, 401, 1273),
}

for key in ("4", "27", "28", "39", "40", "46", "44", "19", "20", "23", "24", "21", "22", "33", "54", "35", "53", "52", "51", "29", "47", "31", "48"):
    obj = deepcopy(source[key])
    set_bounds(obj, *placements[key])
    objects.append(obj)

# Exact ids come from the 2026-08-15 current-solution XML export, after the two
# globals were created and natively verified.
for new_key, field_name, field_id, label, y in (
    (101, "FOCUS::g_wv_rating_lo", "122", "rating_lo", 234),
    (103, "FOCUS::g_wv_rating_hi", "123", "rating_hi", 258),
):
    field = clone(source, "21", new_key, (y, 1082, y + 21, 1273))
    field.find(".//Name").text = field_name
    field_obj = field.find("FieldObj")
    ddr_field = field_obj.find("DDRInfo/Field") if field_obj is not None else None
    if ddr_field is None:
        raise ValueError(f"Clone for {field_name} has no DDR field reference")
    ddr_field.set("name", field_name.split("::", 1)[1])
    ddr_field.set("id", field_id)
    ddr_field.set("repetition", "1")
    ddr_field.set("maxRepetition", "1")
    ddr_field.set("table", "FOCUS")
    objects.append(field)

    text = clone(source, "22", new_key + 1, (y + 3, 995, y + 24, 1071))
    set_text(text, label)
    objects.append(text)

# Native state evidence requested by the brief. Merge symbols are evaluated by
# FileMaker; the labels and values remain ordinary native layout text objects.
for new_key, label, symbol, y in (
    (105, "found_count", "{{FoundCount}}", 282),
    (107, "record_number", "{{RecordNumber}}", 306),
):
    label_obj = clone(source, "22", new_key, (y + 3, 972, y + 24, 1071))
    set_text(label_obj, label)
    objects.append(label_obj)
    value_obj = clone(source, "22", new_key + 1, (y, 1082, y + 21, 1273))
    set_text(value_obj, symbol)
    value_text_obj = value_obj.find("TextObj")
    value_text_obj.set("flags", "8")
    ET.SubElement(value_text_obj, "FieldList", {"quickFind": "False"})
    objects.append(value_obj)

# Repeating list-row objects in the Body part. The click target is intentionally
# added only after the governed row-selection script exists and can be bound.
row_number = clone(source, "22", 109, (435, 12, 456, 55))
set_text(row_number, "{{RecordNumber}}")
row_number_text_obj = row_number.find("TextObj")
row_number_text_obj.set("flags", "8")
ET.SubElement(row_number_text_obj, "FieldList", {"quickFind": "False"})
objects.append(row_number)

row_title = clone(source, "46", 110, (433, 65, 458, 500))
objects.append(row_title)

row_id = clone(source, "44", 111, (433, 510, 458, 650))
objects.append(row_id)

# Source-backed full-row click target. Production UI__Ranked_List uses an
# empty-text Button over the native row and routes it to a narrow focus script.
# This teaching-file adaptation keeps the same one-button/one-script shape,
# uses the current target's verified script id, and makes every visual state
# transparent so it does not obscure the native fields beneath it.
row_button = clone(source, "29", 112, (433, 12, 458, 650))
row_button.set("name", "button.native_row_select")
set_text(row_button, "")
styles = row_button.find("TextObj/Styles")
if styles is None:
    raise ValueError("Native row button has no Styles node")
for local_css in list(styles.findall("LocalCSS")):
    styles.remove(local_css)
local_css = ET.Element("LocalCSS")
local_css.text = """self:normal .self
{
  background-image: none;
  background-color: rgba(0%,0%,0%,0);
  border-top-style: none;
  border-right-style: none;
  border-bottom-style: none;
  border-left-style: none;
  border-image-source: none;
}
self:hover .self
{
  background-image: none;
  background-color: rgba(0%,0%,0%,0);
  border-top-style: none;
  border-right-style: none;
  border-bottom-style: none;
  border-left-style: none;
  border-image-source: none;
}
self:pressed .self
{
  background-image: none;
  background-color: rgba(0%,0%,0%,0);
  border-top-style: none;
  border-right-style: none;
  border-bottom-style: none;
  border-left-style: none;
  border-image-source: none;
}
self:focus .self
{
  background-image: none;
  background-color: rgba(0%,0%,0%,0);
  border-top-style: none;
  border-right-style: none;
  border-bottom-style: none;
  border-left-style: none;
  border-image-source: none;
}
"""
styles.insert(0, local_css)
button_obj = row_button.find("ButtonObj")
if button_obj is None:
    raise ValueError("Native row button has no ButtonObj")
for child in list(button_obj):
    button_obj.remove(child)
button_obj.set("displayType", "0")
step = ET.SubElement(button_obj, "Step", {"enable": "True", "id": "1", "name": "Perform Script"})
step_text = ET.SubElement(step, "StepText")
step_text.text = "Perform Script [ “WV__Demo_Select_Native_Row”; Parameter: GetAsText ( MOVIE::ID ) ]"
ET.SubElement(step, "DisableStepCollapsed", {"state": "False"})
ET.SubElement(step, "CurrentScript", {"value": "Pause"})
calculation = ET.SubElement(step, "Calculation")
calculation.text = "GetAsText ( MOVIE::ID )"
ET.SubElement(step, "Script", {"id": "501", "name": "WV__Demo_Select_Native_Row"})
objects.append(row_button)

snippet = ET.Element("fmxmlsnippet", {"type": "LayoutObjectList"})
container = ET.SubElement(snippet, "Layout", {
    "enclosingRectTop": "12.0000000",
    "enclosingRectLeft": "12.0000000",
    "enclosingRectBottom": "458.0000000",
    "enclosingRectRight": "1273.0000000",
})
for obj in objects:
    container.append(obj)

ET.indent(snippet, space="  ")
payload = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(snippet, encoding="unicode") + "\n"
OUTPUT.write_text(payload, encoding="utf-8")
print(OUTPUT)
print(f"objects={len(objects)}")

row_snippet = ET.Element("fmxmlsnippet", {"type": "LayoutObjectList"})
row_container = ET.SubElement(row_snippet, "Layout", {
    "enclosingRectTop": "433.0000000",
    "enclosingRectLeft": "12.0000000",
    "enclosingRectBottom": "458.0000000",
    "enclosingRectRight": "650.0000000",
})
row_container.append(deepcopy(row_button))
ET.indent(row_snippet, space="  ")
row_payload = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(row_snippet, encoding="unicode") + "\n"
ROW_BUTTON_OUTPUT.write_text(row_payload, encoding="utf-8")
print(ROW_BUTTON_OUTPUT)
print("row_button_objects=1")
