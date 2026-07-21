import base64
import binascii
import json
import os
import struct
import time
import zlib

from openai import OpenAI


CONCEPT_IMAGE_MODEL = "gpt-image-2"
CONCEPT_IMAGE_SIZE = "1024x1024"
CONCEPT_IMAGE_TIMEOUT_SECONDS = 120.0
CONCEPT_IMAGE_MAX_ATTEMPTS = 3
CONCEPT_IMAGE_MAX_BACKOFF_SECONDS = 8.0
DESIGN_BLUEPRINT_FIELDS = (
    "machine_name",
    "primary_function",
    "overall_silhouette",
    "approximate_proportions",
    "dominant_structural_features",
    "distinctive_visual_signature",
    "frame_construction",
    "primary_materials",
    "primary_mechanism",
    "input_location",
    "output_location",
    "power_source",
    "visible_moving_components",
    "operator_position",
    "typical_environment",
    "characteristic_color_palette",
    "key_recognizable_details",
)


def _compact_text(value, limit=320):
    normalized = " ".join(str(value).split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def _compact_items(values, limit=3):
    selected = [_compact_text(value, limit=160) for value in values[:limit]]
    return "; ".join(selected) if selected else "Not specified"


def _concept_identity(concept_data):
    identity = {
        "primary_purpose": _compact_text(
            f'{concept_data["title"]}. {concept_data["leonardo_concept"]}'
        ),
        "main_physical_form": _compact_text(
            f'A purpose-built {concept_data["modern_category"]} physical apparatus or installed system that carries out '
            f'{concept_data["title"]}. Its geometry and construction must be appropriate to the selected era.'
        ),
        "core_inputs": _compact_text(
            "Objects, materials, forces, signals, or human actions implied by these use cases: "
            + _compact_items(concept_data["use_cases"])
        ),
        "core_outputs": _compact_text(
            f'The visible practical result that fulfils the purpose of {concept_data["title"]} in these use contexts: '
            + _compact_items(concept_data["use_cases"])
        ),
        "primary_users": _compact_items(concept_data["target_users"]),
        "intended_operating_environment": _compact_text(
            "Relevant sectors and settings: "
            + _compact_items(concept_data["industries"])
            + ". Use contexts: "
            + _compact_items(concept_data["use_cases"])
        ),
    }
    return json.dumps(identity, ensure_ascii=False, sort_keys=True, indent=2)


def build_design_blueprint(concept_data):
    identity = json.loads(_concept_identity(concept_data))
    machine_name = _compact_text(concept_data["title"], limit=120)
    operating_environment = identity["intended_operating_environment"]
    primary_function = identity["primary_purpose"]
    shared_lineage = {
        "purpose": primary_function,
        "workflow": (
            "Input enters through a dedicated upper-left intake, passes through a "
            "central sensing and processing zone, and leaves through a separate "
            "lower-right output without reversing direction."
        ),
        "functional_architecture": (
            "Three fixed functional zones: intake and preparation on the left, "
            "controlled processing in the center, and collection or delivery on "
            "the lower right."
        ),
        "recognizable_identity": (
            "A single human-scale machine with a taller left intake tower, one "
            "visually dominant central processing chamber, and a clearly separated "
            "lower-right output bank."
        ),
        "primary_users": identity["primary_users"],
        "core_inputs": identity["core_inputs"],
        "core_outputs": identity["core_outputs"],
    }
    leonardo_blueprint = {
        "machine_name": f"{machine_name} — Leonardo Mechanical Apparatus",
        "primary_function": primary_function,
        "overall_silhouette": (
            "An open, asymmetric three-bay oak apparatus: a tall narrow intake "
            "tower on the left, a broad exposed mechanism bay in the center, and "
            "a low receiving bench on the right."
        ),
        "approximate_proportions": (
            "Approximately 2.6 metres long, 1.4 metres deep, and 2.2 metres high; "
            "the left tower occupies one quarter of the length, the central bay "
            "one half, and the right output bench one quarter."
        ),
        "dominant_structural_features": [
            "Four pegged oak corner posts joined by two horizontal walnut rails",
            "A left gravity-fed hopper with a steep V-shaped throat",
            "A central cylindrical processing drum held between two timber A-frames",
            "A lower-right three-compartment receiving chest",
        ],
        "distinctive_visual_signature": (
            "One large six-spoke bronze-rimmed flywheel mounted outside the right "
            "face of the central bay, aligned with the processing drum axle."
        ),
        "frame_construction": (
            "Dark pegged-oak post-and-beam frame with diagonal walnut braces, "
            "hand-cut mortise-and-tenon joints, visible wooden pins, and no closed casing."
        ),
        "primary_materials": (
            "Oiled oak and walnut structure; bronze gears, bearings, cams, and "
            "flywheel rim; wrought-iron shafts; leather belts; hemp rope; linen "
            "screens; stone counterweights."
        ),
        "primary_mechanism": (
            "A fixed three-stage gear train: a small bronze drive pinion at lower "
            "left engages a central 24-tooth wheel, which engages a smaller upper "
            "gear on the drum shaft. A crossed leather belt runs from the large "
            "right-side flywheel to a rear camshaft; a straight lower belt returns "
            "from that camshaft to the intake gate."
        ),
        "input_location": (
            "One V-shaped wooden hopper at shoulder height on the upper-left face, "
            "feeding downward through a single bronze shutter into the central drum."
        ),
        "output_location": (
            "Three open-topped removable wooden receiving trays arranged left to "
            "right beneath the low bench at the lower-right face."
        ),
        "power_source": (
            "Primary drive from a narrow undershot water wheel coupled at the rear-left; "
            "a hand-wound spring barrel and two stone gravity counterweights inside "
            "the left tower maintain motion when water power pauses."
        ),
        "visible_moving_components": [
            "The same external six-spoke flywheel on the central bay's right face",
            "Three intermeshing bronze gears in a vertical diagonal train",
            "One crossed upper leather belt and one straight lower return belt",
            "Twin stone counterweights travelling in parallel guides",
            "The central slatted drum and its rear camshaft",
        ],
        "operator_position": (
            "The operator stands at the front-left beside two waist-height wooden "
            "control levers and one floor treadle, clear of the flywheel and output trays."
        ),
        "typical_environment": (
            f"A dry, working High Renaissance installation suited to: {operating_environment}"
        ),
        "characteristic_color_palette": (
            "Dark honey oak, near-black walnut, aged bronze, muted brass, wrought-iron "
            "charcoal, natural leather brown, and unbleached linen."
        ),
        "key_recognizable_details": [
            "Tall left hopper with one bronze shutter",
            "Exactly one large six-spoke flywheel on the central-right exterior",
            "Three exposed bronze gears in the same diagonal arrangement",
            "Twin counterweights visible inside the left tower",
            "Two front-left levers and one treadle",
            "Exactly three lower-right wooden output trays",
        ],
    }
    modern_blueprint = {
        "machine_name": f"{machine_name} — Modern Integrated System",
        "primary_function": primary_function,
        "overall_silhouette": (
            "A sealed, softly rectangular graphite cabinet with a slightly taller "
            "left intake tower, a wide central panoramic process window, and a low "
            "right-hand output bank integrated into one continuous enclosure."
        ),
        "approximate_proportions": (
            "Approximately 2.2 metres wide, 1.05 metres deep, and 2.0 metres high; "
            "the left intake module occupies 25 percent of the facade, the central "
            "windowed process module 50 percent, and the right service/output module "
            "25 percent."
        ),
        "dominant_structural_features": [
            "A flush graphite aluminium outer cabinet on a recessed black plinth",
            "A left waist-to-shoulder-height intake drawer beneath a slim sensor hood",
            "A single panoramic safety-glass window across the central half",
            "Three pull-out collection bins across the lower-right facade",
        ],
        "distinctive_visual_signature": (
            "One uninterrupted smoke-tinted central window framing two compact "
            "mirrored robotic arms around a matte-black rotating process drum."
        ),
        "frame_construction": (
            "Welded structural-steel chassis beneath modular powder-coated aluminium "
            "panels, with a recessed plinth, rounded 35-millimetre cabinet corners, "
            "flush fasteners, and sealed removable service panels."
        ),
        "primary_materials": (
            "Graphite powder-coated aluminium panels, black structural steel, "
            "smoke-tinted safety glass, dark durable polymer trims, stainless-steel "
            "contact surfaces, and restrained cool-blue status lighting."
        ),
        "primary_mechanism": (
            "Two mirrored compact six-axis robotic arms manipulate the input around "
            "one central horizontal rotating drum while an overhead sensor bar and "
            "two fixed side cameras inspect the process; guarded conveyors route the "
            "result to three lower-right bins."
        ),
        "input_location": (
            "One wide pull-out intake drawer on the left facade at waist height, "
            "directly below a full-width matte-black sensor hood."
        ),
        "output_location": (
            "Exactly three equal pull-out bins in one horizontal row across the "
            "lower-right facade, each with the same recessed dark handle."
        ),
        "power_source": (
            "Mains electric power through the rear plinth, driving enclosed servo "
            "motors, the drum motor, conveyors, sensors, and control electronics."
        ),
        "visible_moving_components": [
            "Two mirrored robotic arms mounted to the inner left and right walls",
            "One matte-black horizontal rotating drum at the window centre",
            "One guarded lower conveyor running toward the three output bins",
            "The left intake drawer and three lower-right bin drawers",
        ],
        "operator_position": (
            "The operator stands at the front-right beside one 12-inch landscape "
            "touchscreen mounted above the output bank; maintenance access is from "
            "the split rear doors and one narrow flush door on the right side."
        ),
        "typical_environment": (
            f"A clean present-day installation appropriate to: {operating_environment}"
        ),
        "characteristic_color_palette": (
            "Matte graphite body, deep navy recessed panels, smoke-black window, "
            "brushed stainless contact surfaces, and minimal cool-blue status accents."
        ),
        "key_recognizable_details": [
            "Slightly taller left module with one intake drawer and overhead sensor bar",
            "Single wide smoke-tinted central window",
            "Exactly two mirrored internal robotic arms around one black drum",
            "One 12-inch landscape screen above the lower-right output bank",
            "Exactly three equal lower-right collection bins",
            "Split rear service doors plus one narrow right-side service door",
        ],
    }
    return {
        "shared_invention_lineage": shared_lineage,
        "leonardo_blueprint": leonardo_blueprint,
        "modern_blueprint": modern_blueprint,
    }


def _serialize_era_blueprint(design_blueprint, blueprint_key):
    blueprint = design_blueprint[blueprint_key]
    missing_fields = [field for field in DESIGN_BLUEPRINT_FIELDS if field not in blueprint]
    if missing_fields:
        raise ValueError(
            "Design blueprint is missing required fields: " + ", ".join(missing_fields)
        )

    return json.dumps(
        {
            "shared_invention_lineage": design_blueprint["shared_invention_lineage"],
            "machine_blueprint": blueprint,
        },
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    )


def _assemble_concept_image_prompt(blueprint, role, sections):
    identity_lock = """
This image must depict exactly the same machine described below.

Do not redesign the product.

Do not invent a new geometry.

Only change camera position, activity, environment and human interaction.

The Design Blueprint has higher priority than every role-specific instruction. The role may change only viewpoint, process state, surrounding scene, and human activity. It must not add, remove, relocate, resize, or restyle any machine component defined by the blueprint.
"""
    ordered_sections = (
        ("1. Design Blueprint — highest priority", blueprint),
        ("2. Machine identity lock", identity_lock),
        ("3. Exact image role", role),
        *sections,
    )
    return "\n\n".join(
        f"{heading}\n{body.strip()}" for heading, body in ordered_sections
    )


def build_leonardo_concept_image_prompts(concept_data, design_blueprint):
    blueprint = _serialize_era_blueprint(design_blueprint, "leonardo_blueprint")
    era_interpretation = """
Priority instruction: create a genuine historical reconstruction of how Leonardo da Vinci or a skilled High Renaissance engineer might have attempted this purpose around the year 1505. Redesign the invention from first principles using only knowledge, energy sources, tools, manufacturing methods, and mechanisms historically plausible in 1505. This must be a pre-industrial mechanical interpretation, not a modern product placed in a Renaissance room.

If the purpose depends on technology impossible in 1505, replace it with an ingenious functional analogue: balances, floats, lenses, sieves, resonance, pressure plates, or manual inspection for sensing; gears, cams, encoded drums, rotating discs, or trained operators for computation; clockwork, gravity, water, wind, springs, animal power, or human power for autonomous motion; and historically plausible sorting by size, weight, density, magnetism, shape, or manual selection.

Render a photorealistic cinematic physical scene. Do not render a sketch, blueprint, diagram, sepia illustration, manuscript page, or modern cutaway infographic.
"""
    historical_materials = """
Use only function-appropriate materials and mechanisms plausible around 1505: oak, walnut, carved timber, bronze, brass, copper, wrought iron, hand-forged steel tools, leather belts, rope drives, wooden or bronze gears, pulleys, cams, cranks, flywheels, counterweights, springs, water power, human power, animal power, wind power, gravity-fed mechanisms, glass lenses, parchment, hand-painted markings, rivets, pins, pegs, and mechanical linkages.

The machine must visibly rely on a carved timber structural frame, exposed bronze or brass motion-transfer components, and one distinctive dominant mechanical feature appropriate to the concept—such as a wheel, drum, gear train, pulley cluster, counterweight assembly, or lens mechanism.
"""
    historical_prohibitions = """
Strictly prohibit visibly modern technology and settings: electricity, electric motors, batteries, wires, LEDs, illuminated digital screens, LCD or OLED displays, touchscreens, digital interfaces, computer-vision cameras, modern optical sensors, microchips, circuit boards, artificial-intelligence interfaces, contemporary robotic arms, modern industrial robot joints, plastics, aluminium extrusions, carbon fibre, injection-moulded parts, stainless-steel appliance housings, contemporary industrial housings, modern bins with printed recycling icons, modern factories, contemporary branding, modern apartments, modern clothing, and modern typography.

Also prohibit logos, product names printed on the machine, interface paragraphs, signs, labels, watermarks, recycling symbols, random letters, and pseudo-text. Never depict modern machinery merely decorated with wood, brass, warm lighting, or Renaissance ornament.
"""
    historical_continuity = """
Within the Leonardo set, preserve the same broad proportions and recognizable historical machine identity in all three images. Repeat the same carved timber frame, the same bronze or brass drive system, and the same selected dominant mechanical feature. Keep intake, process, and output locations consistent. Change camera position and human activity, not the invention's identity.

Across eras, preserve the purpose and functional input-process-output lineage from the shared identity, but do not copy a modern casing, robotic arm, sensor array, interface, or manufacturing design. The Renaissance machine must be an era-appropriate mechanical ancestor, not the same object with different styling.
"""
    square_readability = """
Square image composed for a compact slot: one clearly readable primary machine, strong silhouette, important mechanism away from the edges, no split screen, no collage, no multiple panels, no excessive empty space, and no malformed text. Keep the machine visually dominant even when people are present.
"""

    roles = (
        (
            "leonardo_concept_1",
            "Historical hero overview. Show the complete finished Renaissance invention and establish its overall form, construction, scale, and environment.",
            "Three-quarter wide view in a concept-appropriate Renaissance workshop, civic facility, courtyard, mill, laboratory, harbour, or farm. The full apparatus is visible, occupies approximately 65–80% of the frame, and has a clear silhouette. No close-up, no cutaway, no active crowd, and no catalogue-style frontal view. This camera must be wider and more elevated than Image 2 and less human-centered than Image 3.",
            "Show the overall load-bearing structure and all major mechanical subsystems in their correct spatial relationship. The intake, mechanism, power source, controls, and output area should be identifiable through physical form without labels. The machine is complete and at rest or only gently active; overall architecture has priority over detail.",
        ),
        (
            "leonardo_concept_2",
            "Mechanical operation and internal function. Clearly demonstrate cause and effect inside the historical mechanism while the machine actively performs its purpose.",
            "Medium-close technical cinematic view from a different side, lower height, or oblique angle than Image 1. Use an open frame, exposed mechanism, naturally visible machinery, or removable wooden panel. Do not repeat the wide hero view. Do not use an exploded diagram, modern cutaway infographic, written labels, or a posed operator portrait.",
            "Show relevant gears, leather belts, rope drives, pulleys, cams, cranks, levers, sieves, channels, rotating drums, flywheels, springs, or counterweights transferring motion. When appropriate, show physical input moving through the apparatus and a visible output emerging. Prioritize motion transfer, cause and effect, and mechanical ingenuity.",
        ),
        (
            "leonardo_concept_3",
            "Human use in historical context. Show the practical workflow and social value of the same Renaissance invention.",
            "Wider contextual scene with a clearly different viewpoint, environment framing, and action from Images 1 and 2. Include one to three historically dressed artisans, workers, scholars, farmers, physicians, merchants, sailors, or civic operators. They actively load, control, maintain, observe, or receive output from the machine. Use historically accurate clothing and surroundings; do not pose people beside an idle product.",
            "Keep the complete machine visible and recognizable while human actions explain its scale and use case. Show a logical sequence of input, operator action, and useful result. Human activity supports the machine's purpose but must not obscure its distinctive frame, drive system, or dominant mechanical feature.",
        ),
    )

    return {
        image_type: _assemble_concept_image_prompt(
            blueprint,
            role,
            (
                ("4. Required scene and camera composition", composition),
                ("5. Required functional elements", functional_elements),
                ("6. Era and engineering interpretation", era_interpretation),
                ("7. Required materials and mechanisms", historical_materials),
                ("8. Explicit prohibited elements", historical_prohibitions),
                ("9. Continuity requirements", historical_continuity),
                ("10. Square-image readability requirements", square_readability),
            ),
        )
        for image_type, role, composition, functional_elements in roles
    }


def build_modern_concept_image_prompts(concept_data, design_blueprint):
    blueprint = _serialize_era_blueprint(design_blueprint, "modern_blueprint")
    era_interpretation = """
Priority instruction: create a realistic present-day engineering implementation of the shared purpose. Translate the function into a commercially plausible product, installed machine, service system, or piece of infrastructure using contemporary manufacturing and safety practices. The result must look buildable, maintainable, usable, and appropriate for the stated users and operating environment.

Use modern technology only when it serves the concept: industrial design, electric actuators, computer vision, modern sensors, robotics, contemporary safety systems, and practical controls. This is the evolutionary descendant of the Renaissance mechanism, not the same wooden machine in cooler lighting and not an unexplained science-fiction device.

Render a photorealistic present-day scene, not a CAD drawing, blueprint, diagram, technical board, or concept-art illustration.
"""
    modern_materials = """
Use function-appropriate contemporary materials and construction: aluminium, painted or stainless steel where appropriate, structural steel, safety glass, durable polymers, realistic seals and fasteners, commercial motors and actuators, guarded moving parts, accessible service panels, credible sensor housings, and practical user controls.

Preserve a consistent modern product language across the set: the same broad geometry and proportions, the same restrained material palette, the same intake and output openings, and the same distinctive control, sensor, safety, or processing modules selected for this concept.
"""
    modern_prohibitions = """
Prohibit generic science-fiction styling: impossible holograms, glowing fantasy interfaces, excessive neon, spaceship interiors, unexplained futuristic technology, decorative light strips, and random humanoid robots unless a humanoid form is essential to the concept. Do not copy Renaissance timber framing, exposed historical gear trains, parchment styling, or antique ornament into the modern product.

Also prohibit logos, product names printed on the device, interface paragraphs, large signs, labels, watermarks, recycling symbols unless essential and reliably rendered, random letters, and pseudo-text. Avoid three catalogue photographs, repeated frontal views, repeated poses, and repeated lighting setups.
"""
    modern_continuity = """
Within the Modern set, preserve the same product geometry, proportions, material palette, intake and output locations, controls, sensors, safety guards, modules, and other distinctive features across all three images. Change viewpoint, process state, and user activity, not the product identity.

Across eras, preserve the shared purpose, scale, and functional input-process-output lineage, but do not retain identical casing, robotic arms, interfaces, joints, manufacturing design, or materials from the Leonardo machine. The modern result should feel like a practical technological descendant rather than the same object in another room.
"""
    square_readability = """
Square image composed for a compact slot: one clearly readable primary system, strong silhouette, important functional areas away from the edges, no split screen, no collage, no multiple panels, no excessive empty space, and no malformed text. Keep the product or system visually dominant even when users are present.
"""

    roles = (
        (
            "modern_concept_1",
            "Product or system overview. Show the complete present-day implementation and establish its industrial design, installation, scale, and commercial plausibility.",
            "Clean three-quarter wide product or architectural view in the authentic operating environment. The complete device or system is visible, occupies approximately 65–80% of the frame, and has a clear silhouette. No person touches the product, no close-up, no action blur, and no frontal catalogue view. Use a viewing side, camera height, environment, and cool neutral lighting clearly different from the Leonardo hero image and from Modern Images 2 and 3.",
            "Show the complete enclosure or structural system, installation points, guarded functional zones, input and output areas, service access, controls, sensors, and safety provisions relevant to the concept. Present a credible manufactured object rather than a posed speculative sculpture.",
        ),
        (
            "modern_concept_2",
            "Active operation. Show the same modern system physically performing its main function and producing an observable result.",
            "Medium-close operational view from a different side, lower or higher camera position, and tighter framing than Image 1. Show active movement or transformation; do not repeat the hero product shot. Avoid a person standing in front of the machine unless human presence is strictly required to reveal operation.",
            "Show input entering and output leaving where relevant. Make moving parts, robotic manipulation, sensing, processing, transport, treatment, or transformation visibly understandable. Include believable guarding, actuators, sensors, controls, and material flow. Prioritize function, movement, real technology, and observable result over styling.",
        ),
        (
            "modern_concept_3",
            "Real-world user interaction and deployment. Show practical usability, workflow, scale, and value for the specified target audience.",
            "Wider human-context scene with a clearly different viewpoint, camera distance, environment framing, and action from Images 1 and 2. Include one or more authentic present-day users from the stated target audience actively interacting with, supervising, maintaining, loading, unloading, or benefiting from the system. Do not pose a person beside an idle product.",
            "Keep the system clearly visible and recognizable while interaction demonstrates a logical workflow. Show controls, access points, loading or unloading areas, safety behavior, and the useful outcome where relevant. Human activity must make practical operational sense and must not hide the product's distinctive geometry or modules.",
        ),
    )

    return {
        image_type: _assemble_concept_image_prompt(
            blueprint,
            role,
            (
                ("4. Required scene and camera composition", composition),
                ("5. Required functional elements", functional_elements),
                ("6. Era and engineering interpretation", era_interpretation),
                ("7. Required materials and mechanisms", modern_materials),
                ("8. Explicit prohibited elements", modern_prohibitions),
                ("9. Continuity requirements", modern_continuity),
                ("10. Square-image readability requirements", square_readability),
            ),
        )
        for image_type, role, composition, functional_elements in roles
    }


def _get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key)


def _get_concept_image_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key, max_retries=0)


def _generate_image(prompt_text, size="1024x1024"):
    client = _get_client()

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt_text,
        size=size,
    )

    image_base64 = result.data[0].b64_json

    return {
        "prompt": prompt_text,
        "image_bytes": base64.b64decode(image_base64),
    }


def _validate_png(image_bytes):
    if not image_bytes or not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Image payload is not a PNG image")

    offset = 8
    width = height = None
    compressed_data = []
    found_iend = False

    while offset + 12 <= len(image_bytes):
        chunk_length = struct.unpack(">I", image_bytes[offset : offset + 4])[0]
        chunk_type = image_bytes[offset + 4 : offset + 8]
        chunk_start = offset + 8
        chunk_end = chunk_start + chunk_length
        crc_end = chunk_end + 4

        if crc_end > len(image_bytes):
            raise ValueError("PNG chunk is truncated")

        chunk_data = image_bytes[chunk_start:chunk_end]
        expected_crc = struct.unpack(">I", image_bytes[chunk_end:crc_end])[0]
        actual_crc = binascii.crc32(chunk_type)
        actual_crc = binascii.crc32(chunk_data, actual_crc) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise ValueError("PNG chunk checksum is invalid")

        if chunk_type == b"IHDR":
            if chunk_length != 13:
                raise ValueError("PNG header is invalid")
            width, height = struct.unpack(">II", chunk_data[:8])
        elif chunk_type == b"IDAT":
            compressed_data.append(chunk_data)
        elif chunk_type == b"IEND":
            found_iend = True
            break

        offset = crc_end

    if not width or not height or not compressed_data or not found_iend:
        raise ValueError("PNG image is incomplete")

    try:
        decoded_pixels = zlib.decompress(b"".join(compressed_data))
    except zlib.error as exc:
        raise ValueError("PNG pixel data is unreadable") from exc

    if not decoded_pixels:
        raise ValueError("PNG pixel data is empty")


def _is_retryable_image_error(exc):
    status_code = getattr(exc, "status_code", None)
    if status_code == 429 or (isinstance(status_code, int) and status_code >= 500):
        return True

    return exc.__class__.__name__ in {
        "APIConnectionError",
        "APITimeoutError",
        "InternalServerError",
        "RateLimitError",
    }


def _retry_delay(exc, attempt):
    retry_after = None
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if headers:
        retry_after = headers.get("retry-after")

    try:
        requested_delay = float(retry_after)
    except (TypeError, ValueError):
        requested_delay = 2 ** (attempt - 1)

    return min(max(requested_delay, 0.0), CONCEPT_IMAGE_MAX_BACKOFF_SECONDS)


def generate_concept_image(prompt_text):
    for attempt in range(1, CONCEPT_IMAGE_MAX_ATTEMPTS + 1):
        try:
            result = _get_concept_image_client().images.generate(
                model=CONCEPT_IMAGE_MODEL,
                prompt=prompt_text,
                size=CONCEPT_IMAGE_SIZE,
                quality="medium",
                output_format="png",
                timeout=CONCEPT_IMAGE_TIMEOUT_SECONDS,
            )

            if not result.data:
                raise ValueError("Image generation returned no data")

            image_base64 = result.data[0].b64_json
            if not image_base64:
                raise ValueError("Image generation returned no image payload")

            try:
                image_bytes = base64.b64decode(image_base64, validate=True)
            except (ValueError, binascii.Error) as exc:
                raise ValueError("Image payload is not valid base64") from exc

            if not image_bytes:
                raise ValueError("Decoded image payload is empty")

            _validate_png(image_bytes)
            return {
                "prompt": prompt_text,
                "image_bytes": image_bytes,
            }
        except Exception as exc:
            if attempt >= CONCEPT_IMAGE_MAX_ATTEMPTS or not _is_retryable_image_error(exc):
                raise
            time.sleep(_retry_delay(exc, attempt))


def generate_leonardo_image_prompt(prompt_text):
    return _generate_image(prompt_text, size="1024x1024")


def generate_blueprint_image_prompt(prompt_text):
    enhanced_prompt = f"""
    Create a clean modern engineering blueprint based on this concept:

    {prompt_text}

    Required visual style:
    - modern technical blueprint
    - CAD presentation board
    - clean white or light background
    - precise thin linework
    - orthographic views
    - front view, side view, top view
    - labeled modules and engineering subsystems
    - arrows, dimensions, technical annotations
    - product design documentation layout

    Strictly avoid:
    - sepia tone
    - hand-drawn sketch style
    - Renaissance notebook style
    - artistic rendering
    - vintage paper texture
    - painterly shading
    """

    return _generate_image(enhanced_prompt, size="1024x1024")
