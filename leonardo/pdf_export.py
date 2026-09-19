import re
from datetime import datetime
from io import BytesIO
from pathlib import Path

import reportlab
from i18n import normalize_language, translate
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT = 50
RIGHT = 50
TOP = 50
BOTTOM = 50
LINE_HEIGHT = 18
_SVG_PATTERN = re.compile(r"<svg\b.*?</svg>", re.DOTALL)
_SVG_ROOT_STYLE_PATTERN = re.compile(
    r"(?P<prefix><svg\b[^>]*?)(?P<space>\s+)style="
    r"(?P<quote>[\"'])(?P<style>.*?)(?P=quote)",
    re.DOTALL,
)


def _pdf_fonts(language):
    language = normalize_language(language)
    if language in {"zh", "ja", "ko"}:
        unicode_font_candidates = (
            Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
            Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        )
        for font_path in unicode_font_candidates:
            if font_path.exists():
                font_name = "LeonardoCJK"
                if font_name not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name, font_name

    if language == "zh":
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        return "STSong-Light", "STSong-Light"
    if language == "ja":
        pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
        return "HeiseiKakuGo-W5", "HeiseiKakuGo-W5"
    if language == "ko":
        pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))
        return "HYSMyeongJo-Medium", "HYSMyeongJo-Medium"

    fonts_dir = Path(reportlab.__file__).resolve().parent / "fonts"
    regular_name = "LeonardoSans"
    bold_name = "LeonardoSans-Bold"
    font_candidates = (
        (
            Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
            Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        ),
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ),
        (fonts_dir / "Vera.ttf", fonts_dir / "VeraBd.ttf"),
    )
    regular_path, bold_path = next(
        (paths for paths in font_candidates if all(path.exists() for path in paths)),
        font_candidates[-1],
    )
    if regular_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(regular_name, regular_path))
    if bold_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(bold_name, bold_path))
    return regular_name, bold_name


def _wrap_text(value, font_name, font_size, width):
    text = str(value)
    if not any(
        "\u3040" <= character <= "\u30ff"
        or "\u3400" <= character <= "\u9fff"
        or "\uac00" <= character <= "\ud7af"
        for character in text
    ):
        return simpleSplit(text, font_name, font_size, width)

    lines = []
    for paragraph in text.splitlines() or [""]:
        current = ""
        for character in paragraph:
            candidate = current + character
            if current and pdfmetrics.stringWidth(candidate, font_name, font_size) > width:
                lines.append(current.rstrip())
                current = character.lstrip()
            else:
                current = candidate
        lines.append(current)
    return lines or [""]


def _draw_title(c, text, y, fonts):
    if y < BOTTOM + 50:
        c.showPage()
        y = PAGE_HEIGHT - TOP
    c.setFont(fonts[1], 20)
    c.drawString(LEFT, y, text)
    return y - 30


def _draw_heading(c, text, y, fonts):
    if y < BOTTOM + 40:
        c.showPage()
        y = PAGE_HEIGHT - TOP
    c.setFont(fonts[1], 15)
    c.drawString(LEFT, y, text)
    return y - 22


def _draw_label_value(c, label, value, y, fonts, width=500):
    c.setFont(fonts[1], 11)
    c.drawString(LEFT, y, f"{label}:")
    y -= 16

    c.setFont(fonts[0], 11)
    lines = _wrap_text(value, fonts[0], 11, width)

    for line in lines:
        if y < BOTTOM:
            c.showPage()
            y = PAGE_HEIGHT - TOP
            c.setFont(fonts[0], 11)
        c.drawString(LEFT, y, line)
        y -= LINE_HEIGHT

    return y - 8


def _draw_list(c, label, items, y, fonts, width=500):
    c.setFont(fonts[1], 11)
    c.drawString(LEFT, y, f"{label}:")
    y -= 16

    c.setFont(fonts[0], 11)

    for item in items:
        lines = _wrap_text(f"- {item}", fonts[0], 11, width)
        for line in lines:
            if y < BOTTOM:
                c.showPage()
                y = PAGE_HEIGHT - TOP
                c.setFont(fonts[0], 11)
            c.drawString(LEFT, y, line)
            y -= LINE_HEIGHT

    return y - 8


def _draw_image(c, image_bytes, y, max_width=500, max_height=260):
    image = ImageReader(BytesIO(image_bytes))
    img_width, img_height = image.getSize()

    scale = min(max_width / img_width, max_height / img_height)
    draw_width = img_width * scale
    draw_height = img_height * scale

    if y - draw_height < BOTTOM:
        c.showPage()
        y = PAGE_HEIGHT - TOP

    c.drawImage(
        image,
        LEFT,
        y - draw_height,
        width=draw_width,
        height=draw_height,
        preserveAspectRatio=True,
        mask="auto"
    )

    return y - draw_height - 16


def _draw_cover_page(c, concept_data, saved_images=None, language="en", fonts=None):
    fonts = fonts or _pdf_fonts(language)
    y = PAGE_HEIGHT - 80

    c.setFont(fonts[1], 28)
    c.drawString(LEFT, y, "Leonardo AI")
    y -= 34

    c.setFont(fonts[0], 14)
    c.drawString(LEFT, y, translate("pdf.package_subtitle", language))
    y -= 40

    title = concept_data.get("title", translate("pdf.untitled", language))
    c.setFont(fonts[1], 22)
    for line in _wrap_text(title, fonts[1], 22, 500):
        c.drawString(LEFT, y, line)
        y -= 28

    y -= 10

    c.setFont(fonts[0], 12)
    category = concept_data.get("modern_category", translate("pdf.not_available", language))
    product_name = concept_data.get("modern_product_name", translate("pdf.not_available", language))
    export_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    creator = translate("pdf.creator", language)

    c.drawString(LEFT, y, f"{translate('common.category', language)}: {category}")
    y -= 20
    c.drawString(LEFT, y, f"{translate('concept.product_name', language)}: {product_name}")
    y -= 20
    c.drawString(LEFT, y, f"{translate('pdf.creator_label', language)}: {creator}")
    y -= 20
    c.drawString(LEFT, y, f"{translate('pdf.export_date', language)}: {export_date}")
    y -= 30

    executive_summary = concept_data.get("executive_summary", "")
    if executive_summary:
        c.setFont(fonts[1], 14)
        c.drawString(LEFT, y, translate("concept.executive_summary", language))
        y -= 22

        c.setFont(fonts[0], 12)
        for line in _wrap_text(executive_summary, fonts[0], 12, 500):
            c.drawString(LEFT, y, line)
            y -= 18

    # Cover preview images
    if saved_images:
        leonardo_images = [img for img in saved_images if img[1] == "leonardo"]
        blueprint_images = [img for img in saved_images if img[1] == "blueprint"]

        preview_y = y - 20
        preview_height = 140
        preview_width = 220

        if leonardo_images:
            c.setFont(fonts[1], 12)
            c.drawString(LEFT, preview_y, translate("images.leonardo_caption", language))
            leonardo_reader = ImageReader(BytesIO(leonardo_images[0][3]))
            c.drawImage(
                leonardo_reader,
                LEFT,
                preview_y - preview_height - 10,
                width=preview_width,
                height=preview_height,
                preserveAspectRatio=True,
                mask="auto"
            )

        if blueprint_images:
            c.setFont(fonts[1], 12)
            c.drawString(LEFT + 250, preview_y, translate("images.blueprint_caption", language))
            blueprint_reader = ImageReader(BytesIO(blueprint_images[0][3]))
            c.drawImage(
                blueprint_reader,
                LEFT + 250,
                preview_y - preview_height - 10,
                width=preview_width,
                height=preview_height,
                preserveAspectRatio=True,
                mask="auto"
            )

    c.showPage()


def _write_project_plan_pdf(c, concept_data, saved_images=None, language="en"):
    fonts = _pdf_fonts(language)
    _draw_cover_page(c, concept_data, saved_images=saved_images, language=language, fonts=fonts)

    y = PAGE_HEIGHT - TOP

    title = concept_data.get("title", translate("pdf.project_plan", language))
    y = _draw_title(c, title, y, fonts)

    y = _draw_label_value(c, translate("common.category", language), concept_data.get("modern_category", ""), y, fonts)
    y = _draw_label_value(c, translate("concept.product_name", language), concept_data.get("modern_product_name", ""), y, fonts)

    y = _draw_heading(c, translate("pdf.leonardo_inspiration", language), y, fonts)
    y = _draw_label_value(c, translate("concept.concept", language), concept_data.get("leonardo_concept", ""), y, fonts)
    y = _draw_label_value(c, translate("concept.sketch_description", language), concept_data.get("leonardo_sketch_description", ""), y, fonts)

    y = _draw_heading(c, translate("pdf.modern_definition", language), y, fonts)
    y = _draw_label_value(c, translate("concept.product_name", language), concept_data.get("modern_product_name", ""), y, fonts)
    y = _draw_label_value(c, translate("common.category", language), concept_data.get("modern_category", ""), y, fonts)
    y = _draw_label_value(c, translate("concept.executive_summary", language), concept_data.get("executive_summary", ""), y, fonts)

    y = _draw_heading(c, translate("concept.business_need", language), y, fonts)
    y = _draw_label_value(c, translate("concept.problem_statement", language), concept_data.get("problem_statement", ""), y, fonts)
    y = _draw_list(c, translate("concept.target_users", language), concept_data.get("target_users", []), y, fonts)
    y = _draw_list(c, translate("concept.industries", language), concept_data.get("industries", []), y, fonts)
    y = _draw_list(c, translate("concept.use_cases", language), concept_data.get("use_cases", []), y, fonts)

    y = _draw_heading(c, translate("concept.engineering", language), y, fonts)
    y = _draw_label_value(c, translate("concept.modern_principle", language), concept_data.get("modern_principle", ""), y, fonts)
    y = _draw_list(c, translate("concept.system_components", language), concept_data.get("system_components", []), y, fonts)
    y = _draw_list(c, translate("concept.materials", language), concept_data.get("materials", []), y, fonts)
    y = _draw_list(c, translate("concept.technical_requirements", language), concept_data.get("technical_requirements", []), y, fonts)
    y = _draw_label_value(c, translate("concept.modern_sketch_description", language), concept_data.get("modern_sketch_description", ""), y, fonts)

    if saved_images:
        leonardo_images = [img for img in saved_images if img[1] == "leonardo"]
        blueprint_images = [img for img in saved_images if img[1] == "blueprint"]

        if leonardo_images or blueprint_images:
            y = _draw_heading(c, translate("images.generated_assets", language), y, fonts)

        if leonardo_images:
            y = _draw_label_value(c, translate("images.leonardo_caption", language), leonardo_images[0][2] or translate("pdf.generated_image", language), y, fonts)
            y = _draw_image(c, leonardo_images[0][3], y)

        if blueprint_images:
            y = _draw_label_value(c, translate("images.blueprint_caption", language), blueprint_images[0][2] or translate("pdf.generated_image", language), y, fonts)
            y = _draw_image(c, blueprint_images[0][3], y)

    y = _draw_heading(c, translate("concept.roadmap", language), y, fonts)
    roadmap = concept_data.get("implementation_roadmap", {})
    y = _draw_label_value(c, translate("concept.prototype", language), roadmap.get("prototype", ""), y, fonts)
    y = _draw_label_value(c, translate("concept.mvp", language), roadmap.get("mvp", ""), y, fonts)
    y = _draw_label_value(c, translate("concept.pilot", language), roadmap.get("pilot", ""), y, fonts)
    y = _draw_label_value(c, translate("concept.production", language), roadmap.get("production", ""), y, fonts)
    y = _draw_label_value(c, translate("concept.deployment_strategy", language), concept_data.get("deployment_strategy", ""), y, fonts)

    y = _draw_heading(c, translate("concept.commercial_outlook", language), y, fonts)
    y = _draw_label_value(c, translate("concept.market_demand", language), concept_data.get("market_demand", ""), y, fonts)
    y = _draw_label_value(c, translate("concept.startup_cost", language), concept_data.get("startup_cost", ""), y, fonts)
    y = _draw_label_value(c, translate("concept.roi", language), concept_data.get("roi", ""), y, fonts)
    y = _draw_label_value(c, translate("concept.investor_summary", language), concept_data.get("investor_summary", ""), y, fonts)

    y = _draw_heading(c, translate("concept.delivery_metrics", language), y, fonts)
    y = _draw_label_value(c, translate("concept.concept_difficulty", language), concept_data.get("difficulty", ""), y, fonts)
    y = _draw_label_value(c, translate("concept.modern_difficulty", language), concept_data.get("modern_difficulty", ""), y, fonts)
    y = _draw_label_value(c, translate("concept.development_time", language), concept_data.get("dev_time", ""), y, fonts)

    c.save()


def export_project_plan_pdf(concept_data, saved_images=None, language="en") -> bytes:
    buffer = BytesIO()
    try:
        c = canvas.Canvas(buffer, pagesize=A4)
        _write_project_plan_pdf(c, concept_data, saved_images=saved_images, language=language)
        return buffer.getvalue()
    finally:
        buffer.close()


def _clean_svg_root_style(svg_markup):
    def clean_style(match):
        declarations = match.group("style").split(";")
        kept = [
            declaration
            for declaration in declarations
            if not re.fullmatch(
                r"height\s*:\s*auto",
                declaration.strip(),
                re.IGNORECASE,
            )
        ]
        if kept == declarations:
            return match.group(0)
        cleaned_style = ";".join(kept)
        if not cleaned_style.strip(" ;"):
            return match.group("prefix")
        return (
            f"{match.group('prefix')}{match.group('space')}style="
            f"{match.group('quote')}{cleaned_style}{match.group('quote')}"
        )

    return _SVG_ROOT_STYLE_PATTERN.sub(clean_style, svg_markup, count=1)


def _svg_drawing(markup):
    match = _SVG_PATTERN.search(markup)
    if match is None:
        return None
    svg_markup = _clean_svg_root_style(match.group(0))
    return svg2rlg(BytesIO(svg_markup.encode("utf-8")))


def _draw_svg_markup(c, markup, x, y, width, height):
    drawing = _svg_drawing(markup)
    if drawing is None:
        return False
    scale = min(width / drawing.width, height / drawing.height)
    c.saveState()
    c.translate(x + (width - drawing.width * scale) / 2, y)
    c.scale(scale, scale)
    renderPDF.draw(drawing, c, 0, 0)
    c.restoreState()
    return True


def _draw_wrapped(c, text, x, y, width, fonts, size=9, line_height=12):
    c.setFont(fonts[0], size)
    for line in _wrap_text(text, fonts[0], size, width):
        c.drawString(x, y, line)
        y -= line_height
    return y


def _draw_view_row(c, views, y, fonts, missing_message):
    column_gap = 10
    column_width = (PAGE_WIDTH - LEFT - RIGHT - column_gap * 2) / 3
    drawing_height = 108
    for index, view in enumerate(views):
        x = LEFT + index * (column_width + column_gap)
        c.setFont(fonts[1], 10)
        c.drawString(x, y, view["title"])
        if not _draw_svg_markup(
            c,
            view["markup"],
            x,
            y - drawing_height - 8,
            column_width,
            drawing_height,
        ):
            _draw_wrapped(
                c,
                missing_message,
                x,
                y - 24,
                column_width,
                fonts,
                size=8,
                line_height=10,
            )
    return y - drawing_height - 24


def _draw_drawing_section(c, section, fonts):
    c.showPage()
    y = PAGE_HEIGHT - TOP
    y = _draw_title(c, section["title"], y, fonts)
    missing_message = section["missing_message"]
    for group in section["groups"]:
        if y < BOTTOM + 150:
            c.showPage()
            y = PAGE_HEIGHT - TOP
        if group["title"]:
            c.setFont(fonts[1], 11)
            c.drawString(LEFT, y, group["title"])
            y -= 18
        y = _draw_view_row(c, group["views"], y, fonts, missing_message)
    for line in section.get("legend", ()):
        if y < BOTTOM + 16:
            c.showPage()
            y = PAGE_HEIGHT - TOP
        y = _draw_wrapped(c, line, LEFT, y, 500, fonts, size=9) - 2


def _draw_connections_section(c, section, fonts):
    c.showPage()
    y = PAGE_HEIGHT - TOP
    y = _draw_title(c, section["title"], y, fonts)
    for connection in section["connections"]:
        if y < BOTTOM + 90:
            c.showPage()
            y = PAGE_HEIGHT - TOP
        c.setFont(fonts[1], 11)
        c.drawString(LEFT, y, connection["components"])
        y -= 16
        for label, value in connection["fields"]:
            y = _draw_wrapped(
                c,
                f"{label}: {value}",
                LEFT + 12,
                y,
                488,
                fonts,
            )
        y -= 10


def _bom_cell_lines(value, font, width):
    text = "\n".join(value) if isinstance(value, tuple) else str(value or "")
    lines = []
    for paragraph in text.splitlines() or [""]:
        lines.extend(_wrap_text(paragraph, font, 7, width - 6) or [""])
    return lines


def _draw_bom_section(c, section, fonts):
    c.showPage()
    y = PAGE_HEIGHT - TOP
    y = _draw_title(c, section["title"], y, fonts)
    widths = (28, 82, 42, 75, 155, 118)

    def draw_row(values, row_y, bold=False):
        lines = [
            _bom_cell_lines(value, fonts[1] if bold else fonts[0], width)
            for value, width in zip(values, widths)
        ]
        row_height = max(len(value) for value in lines) * 9 + 6
        x = LEFT
        for cell_lines, width in zip(lines, widths):
            c.rect(x, row_y - row_height, width, row_height, stroke=1, fill=0)
            c.setFont(fonts[1] if bold else fonts[0], 7)
            text_y = row_y - 10
            for line in cell_lines:
                c.drawString(x + 3, text_y, line)
                text_y -= 9
            x += width
        return row_y - row_height

    y = draw_row(section["headings"], y, bold=True)
    for row in section["rows"]:
        values = (
            row["item"],
            row["component"],
            row["quantity"],
            row["material"],
            row["connections"],
            row["notes"],
        )
        height = max(
            len(_bom_cell_lines(value, fonts[0], width))
            for value, width in zip(values, widths)
        ) * 9 + 6
        if y - height < BOTTOM:
            c.showPage()
            y = PAGE_HEIGHT - TOP
            y = draw_row(section["headings"], y, bold=True)
        y = draw_row(values, y)


def _write_drawing_package_pdf(c, package, language="en"):
    fonts = _pdf_fonts(language)
    y = PAGE_HEIGHT - 90
    c.setFont(fonts[1], 26)
    c.drawString(LEFT, y, package["package_title"])
    y -= 48
    for label, value in package["title_block"]:
        c.setFont(fonts[1], 11)
        c.drawString(LEFT, y, f"{label}:")
        y = _draw_wrapped(c, value, LEFT + 130, y, 370, fonts, size=11) - 8

    for section in package["sections"]:
        if section["kind"] == "drawings":
            _draw_drawing_section(c, section, fonts)
        elif section["kind"] == "connections":
            _draw_connections_section(c, section, fonts)
        elif section["kind"] == "bom":
            _draw_bom_section(c, section, fonts)
    c.save()


def export_drawing_package_pdf(package, language="en") -> bytes:
    buffer = BytesIO()
    try:
        c = canvas.Canvas(buffer, pagesize=A4)
        _write_drawing_package_pdf(c, package, language=language)
        return buffer.getvalue()
    finally:
        buffer.close()
