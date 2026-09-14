VALID_PAGES = ("app", "gallery", "marketplace")


def render_current_page(
    current_page,
    *,
    app_renderer,
    gallery_renderer,
    marketplace_renderer,
):
    renderers = {
        "app": app_renderer,
        "gallery": gallery_renderer,
        "marketplace": marketplace_renderer,
    }
    try:
        renderer = renderers[current_page]
    except KeyError as error:
        raise ValueError(f"Unsupported page: {current_page}") from error
    return renderer()
