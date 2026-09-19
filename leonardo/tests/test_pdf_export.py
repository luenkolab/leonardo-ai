import copy
from pathlib import Path

import pytest

import application.project_export as project_export
import pdf_export
from ui.concept_page import _safe_pdf_filename


def _assert_pdf_bytes(value):
    assert isinstance(value, bytes)
    assert value.startswith(b"%PDF")
    assert len(value) > 100


def _drawing_package_payload(svg_markup):
    drawing_section = lambda key: {
        "key": key,
        "title": key.replace("_", " ").title(),
        "kind": "drawings",
        "missing_message": "Missing geometry",
        "groups": (
            {
                "title": None,
                "views": ({"title": "Top View", "markup": svg_markup},),
            },
        ),
    }
    return {
        "package_title": "Drawing Package",
        "title_block": (
            ("Project", "Test Project"),
            ("Category", "Mechanical"),
            ("Export Date", "2026-09-19 12:00"),
        ),
        "sections": (
            drawing_section("general_arrangement"),
            drawing_section("orthographic_views"),
            drawing_section("assembly_drawings"),
            drawing_section("component_detail_drawings"),
            {
                "key": "connections_fasteners",
                "title": "Connections & Fasteners",
                "kind": "connections",
                "connections": (),
            },
            {
                "key": "bill_of_materials",
                "title": "Bill of Materials",
                "kind": "bom",
                "headings": (
                    "Item",
                    "Component",
                    "Quantity",
                    "Material",
                    "Fasteners / Connections",
                    "Notes",
                ),
                "rows": (),
            },
        ),
    }


def test_pdf_export_without_images_returns_bytes(valid_concept):
    _assert_pdf_bytes(pdf_export.export_project_plan_pdf(valid_concept))


def test_pdf_export_with_images_returns_bytes(valid_concept, saved_images):
    _assert_pdf_bytes(
        pdf_export.export_project_plan_pdf(
            valid_concept,
            saved_images=saved_images,
        )
    )


def test_repeated_pdf_exports_are_independent_and_leave_no_files(
    valid_concept,
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)
    before = set(tmp_path.iterdir())

    first = pdf_export.export_project_plan_pdf(valid_concept)
    first_signature = first[:8]
    second = pdf_export.export_project_plan_pdf(valid_concept)

    _assert_pdf_bytes(first)
    _assert_pdf_bytes(second)
    assert first is not second
    assert first[:8] == first_signature
    assert set(tmp_path.iterdir()) == before


def test_pdf_export_exception_leaves_no_temporary_files(
    valid_concept,
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)
    before = set(tmp_path.iterdir())

    def fail_export(*args, **kwargs):
        raise RuntimeError("mock PDF failure")

    monkeypatch.setattr(pdf_export, "_write_project_plan_pdf", fail_export)

    with pytest.raises(RuntimeError, match="mock PDF failure"):
        pdf_export.export_project_plan_pdf(valid_concept)

    assert set(tmp_path.iterdir()) == before


def test_application_project_export_returns_bytes(valid_concept, monkeypatch):
    monkeypatch.setattr(
        project_export,
        "list_concept_images",
        lambda concept_id: [],
    )

    result = project_export.export_project_package(valid_concept, concept_id=42)

    _assert_pdf_bytes(result)


def test_drawing_package_pdf_writes_all_sections_in_order(monkeypatch):
    package = _drawing_package_payload("<div>Missing geometry</div>")
    rendered_sections = []

    def record_section(_canvas, section, _fonts):
        rendered_sections.append(section["key"])

    monkeypatch.setattr(pdf_export, "_draw_drawing_section", record_section)
    monkeypatch.setattr(pdf_export, "_draw_connections_section", record_section)
    monkeypatch.setattr(pdf_export, "_draw_bom_section", record_section)

    result = pdf_export.export_drawing_package_pdf(package)

    _assert_pdf_bytes(result)
    assert rendered_sections == [
        "general_arrangement",
        "orthographic_views",
        "assembly_drawings",
        "component_detail_drawings",
        "connections_fasteners",
        "bill_of_materials",
    ]


def test_drawing_package_pdf_converts_existing_svg_through_svglib(monkeypatch):
    svg_markup = (
        '<div><svg viewBox="0 0 100 50" style="width:100%; height:auto;">'
        '<rect x="5" y="5" width="90" height="40" stroke="#000" fill="none"/>'
        "</svg></div>"
    )
    package = _drawing_package_payload(svg_markup)
    original_package = copy.deepcopy(package)
    original_svg2rlg = pdf_export.svg2rlg
    converted_svg = []

    def record_conversion(source):
        converted_svg.append(source.read())
        source.seek(0)
        return original_svg2rlg(source)

    monkeypatch.setattr(pdf_export, "svg2rlg", record_conversion)

    result = pdf_export.export_drawing_package_pdf(package)

    _assert_pdf_bytes(result)
    assert len(converted_svg) == 4
    assert all(value.startswith(b"<svg") for value in converted_svg)
    assert all(b"height:auto" not in value for value in converted_svg)
    assert package == original_package


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        (
            '<svg viewBox="0 0 10 10" style="width:100%; height:auto; color:red">',
            '<svg viewBox="0 0 10 10" style="width:100%; color:red">',
        ),
        (
            '<svg viewBox="0 0 10 10" style="height:auto;">',
            '<svg viewBox="0 0 10 10">',
        ),
        (
            '<svg viewBox="0 0 10 10" style="width:100%; color:red">',
            '<svg viewBox="0 0 10 10" style="width:100%; color:red">',
        ),
    ],
)
def test_svg_root_style_removes_only_auto_height(markup, expected):
    assert pdf_export._clean_svg_root_style(markup) == expected


def test_missing_drawing_markup_is_not_converted_to_fake_geometry(monkeypatch):
    package = _drawing_package_payload("<div>Missing geometry</div>")
    conversions = []
    monkeypatch.setattr(
        pdf_export,
        "svg2rlg",
        lambda source: conversions.append(source),
    )

    result = pdf_export.export_drawing_package_pdf(package)

    _assert_pdf_bytes(result)
    assert conversions == []


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("Ordinary Project", "Ordinary_Project.pdf"),
        ("folder/name\\draft", "folder_name_draft.pdf"),
        ("../secret", "secret.pdf"),
        ("..", "leonardo_project.pdf"),
        ("", "leonardo_project.pdf"),
        ("safe\x00name\n", "safename.pdf"),
        ("Проект Леонардо", "Проект_Леонардо.pdf"),
    ],
)
def test_safe_pdf_filename(title, expected):
    assert _safe_pdf_filename(title) == expected


def test_safe_pdf_filename_limits_long_names():
    result = _safe_pdf_filename("a" * 250)

    assert result == f"{'a' * 100}.pdf"
    assert len(Path(result).stem) == 100
