from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.utils import ImageReader

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT = 50
RIGHT = 50
TOP = 50
BOTTOM = 50
LINE_HEIGHT = 18


def _draw_title(c, text, y):
    c.setFont("Helvetica-Bold", 20)
    c.drawString(LEFT, y, text)
    return y - 30


def _draw_heading(c, text, y):
    c.setFont("Helvetica-Bold", 15)
    c.drawString(LEFT, y, text)
    return y - 22


def _draw_label_value(c, label, value, y, width=500):
    c.setFont("Helvetica-Bold", 11)
    c.drawString(LEFT, y, f"{label}:")
    y -= 16

    c.setFont("Helvetica", 11)
    lines = simpleSplit(str(value), "Helvetica", 11, width)

    for line in lines:
        if y < BOTTOM:
            c.showPage()
            y = PAGE_HEIGHT - TOP
            c.setFont("Helvetica", 11)
        c.drawString(LEFT, y, line)
        y -= LINE_HEIGHT

    return y - 8


def _draw_list(c, label, items, y, width=500):
    c.setFont("Helvetica-Bold", 11)
    c.drawString(LEFT, y, f"{label}:")
    y -= 16

    c.setFont("Helvetica", 11)

    for item in items:
        lines = simpleSplit(f"- {item}", "Helvetica", 11, width)
        for line in lines:
            if y < BOTTOM:
                c.showPage()
                y = PAGE_HEIGHT - TOP
                c.setFont("Helvetica", 11)
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


def export_project_plan_pdf(concept_data, output_path, saved_images=None):
    c = canvas.Canvas(output_path, pagesize=A4)
    y = PAGE_HEIGHT - TOP

    title = concept_data.get("title", "Leonardo AI Project Plan")
    y = _draw_title(c, title, y)

    y = _draw_heading(c, "Leonardo Inspiration", y)
    y = _draw_label_value(c, "Concept", concept_data.get("leonardo_concept", ""), y)
    y = _draw_label_value(c, "Sketch Description", concept_data.get("leonardo_sketch_description", ""), y)

    y = _draw_heading(c, "Modern Product Definition", y)
    y = _draw_label_value(c, "Product Name", concept_data.get("modern_product_name", ""), y)
    y = _draw_label_value(c, "Category", concept_data.get("modern_category", ""), y)
    y = _draw_label_value(c, "Executive Summary", concept_data.get("executive_summary", ""), y)

    y = _draw_heading(c, "Business Need", y)
    y = _draw_label_value(c, "Problem Statement", concept_data.get("problem_statement", ""), y)
    y = _draw_list(c, "Target Users", concept_data.get("target_users", []), y)
    y = _draw_list(c, "Industries", concept_data.get("industries", []), y)
    y = _draw_list(c, "Use Cases", concept_data.get("use_cases", []), y)

    y = _draw_heading(c, "Engineering", y)
    y = _draw_label_value(c, "Modern Principle", concept_data.get("modern_principle", ""), y)
    y = _draw_list(c, "System Components", concept_data.get("system_components", []), y)
    y = _draw_list(c, "Materials", concept_data.get("materials", []), y)
    y = _draw_list(c, "Technical Requirements", concept_data.get("technical_requirements", []), y)
    y = _draw_label_value(c, "Modern Sketch Description", concept_data.get("modern_sketch_description", ""), y)

    if saved_images:
        leonardo_images = [img for img in saved_images if img[1] == "leonardo"]
        blueprint_images = [img for img in saved_images if img[1] == "blueprint"]

        if leonardo_images or blueprint_images:
            y = _draw_heading(c, "Generated Visual Assets", y)

        if leonardo_images:
            y = _draw_label_value(c, "Leonardo Sketch", leonardo_images[0][2] or "Generated image", y)
            y = _draw_image(c, leonardo_images[0][3], y)

        if blueprint_images:
            y = _draw_label_value(c, "Modern Blueprint", blueprint_images[0][2] or "Generated image", y)
            y = _draw_image(c, blueprint_images[0][3], y)

    y = _draw_heading(c, "Implementation Roadmap", y)
    roadmap = concept_data.get("implementation_roadmap", {})
    y = _draw_label_value(c, "Prototype", roadmap.get("prototype", ""), y)
    y = _draw_label_value(c, "MVP", roadmap.get("mvp", ""), y)
    y = _draw_label_value(c, "Pilot", roadmap.get("pilot", ""), y)
    y = _draw_label_value(c, "Production", roadmap.get("production", ""), y)
    y = _draw_label_value(c, "Deployment Strategy", concept_data.get("deployment_strategy", ""), y)

    y = _draw_heading(c, "Commercial Outlook", y)
    y = _draw_label_value(c, "Market Demand", concept_data.get("market_demand", ""), y)
    y = _draw_label_value(c, "Startup Cost", concept_data.get("startup_cost", ""), y)
    y = _draw_label_value(c, "ROI", concept_data.get("roi", ""), y)
    y = _draw_label_value(c, "Investor Summary", concept_data.get("investor_summary", ""), y)

    y = _draw_heading(c, "Delivery Metrics", y)
    y = _draw_label_value(c, "Concept Difficulty", concept_data.get("difficulty", ""), y)
    y = _draw_label_value(c, "Modern Difficulty", concept_data.get("modern_difficulty", ""), y)
    y = _draw_label_value(c, "Development Time", concept_data.get("dev_time", ""), y)

    c.save()