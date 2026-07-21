import html


def pretty_label(value):
    return str(value).replace("_", " ").title()


def safe_text(value):
    return html.escape(str(value)) if value is not None else ""


def safe_list(items):
    if not items:
        return ""
    if isinstance(items, list):
        list_items = "".join(f"<li>{safe_text(item)}</li>" for item in items)
        return f'<ul class="result-list">{list_items}</ul>'
    return safe_text(items)
