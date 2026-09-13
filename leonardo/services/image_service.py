import base64
import binascii
import json
import os
import re
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


def _field_text(concept_data, key, limit=480):
    value = concept_data.get(key)
    if isinstance(value, dict):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if isinstance(value, (list, tuple)):
        return _compact_items(value, limit=5)
    return _compact_text(value, limit=limit) if value else "Not specified"


def _is_bridge_concept(concept_data, original_user_prompt=""):
    searchable = " ".join(
        str(value)
        for value in (
            concept_data.get("title", ""),
            concept_data.get("modern_product_name", ""),
            concept_data.get("leonardo_concept", ""),
            concept_data.get("executive_summary", ""),
            concept_data.get("modern_principle", ""),
            original_user_prompt,
        )
    ).casefold()
    bridge_terms = (
        r"\bbridge\b",
        r"\bpuente\b",
        r"\bponte\b",
        r"\bpont\b",
        r"\bbrücke\b",
        r"\bbro\b",
        r"\bsilta\b",
        r"\bmost\b",
        r"мост",
        r"桥",
        r"橋",
        r"다리",
    )
    return any(re.search(term, searchable) for term in bridge_terms)


def _primary_visual_subject(concept_data, original_user_prompt=""):
    if _is_bridge_concept(concept_data, original_user_prompt):
        return (
            "a complete modular emergency bridge system spanning or actively "
            "deploying across a damaged river crossing"
        )
    title = _compact_text(concept_data["title"], limit=140)
    product = _compact_text(concept_data.get("modern_product_name", ""), limit=140)
    if product and product.casefold() != title.casefold():
        return f'the complete physical concept "{title}" / product "{product}"'
    return f'the complete physical concept "{title}"'


def _build_visual_brief(concept_data, original_user_prompt=""):
    primary_subject = _primary_visual_subject(concept_data, original_user_prompt)
    brief = {
        "primary_visual_subject": primary_subject,
        "original_user_prompt": _compact_text(original_user_prompt, limit=1200)
        if original_user_prompt
        else "Not available",
        "title_and_product": _compact_text(
            f'{concept_data["title"]}; {concept_data.get("modern_product_name", "")}',
            limit=260,
        ),
        "concept_summary": _field_text(concept_data, "executive_summary", limit=700),
        "core_principle": _field_text(concept_data, "modern_principle", limit=600),
        "components": _field_text(concept_data, "system_components"),
        "materials": _field_text(concept_data, "materials"),
        "use_cases": _field_text(concept_data, "use_cases"),
        "sketch_and_blueprint_description": _compact_text(
            f'{concept_data.get("leonardo_sketch_description", "")} '
            f'{concept_data.get("modern_sketch_description", "")}',
            limit=1000,
        ),
    }
    if _is_bridge_concept(concept_data, original_user_prompt):
        brief["mandatory_bridge_anchors"] = (
            "modular bridge sections; rapid deployment after floods, earthquakes, "
            "or landslides; lightweight recyclable materials; robotic assembly "
            "modules; transport by standard trucks; adjustable span for different "
            "river widths and terrain; solar-powered structural sensors; AI-assisted "
            "monitoring; civilian rescue and remote-infrastructure use"
        )
    return brief


def _concept_identity(concept_data):
    identity = {
        "primary_purpose": _compact_text(
            f'{concept_data["title"]}. {concept_data["leonardo_concept"]}'
        ),
        "main_physical_form": _compact_text(
            f'The complete physical form of {concept_data["title"]}, at the real-world scale implied by its purpose, '
            "users, environment, and use cases. Do not force it into a generic machine or cabinet geometry."
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


def build_design_blueprint(concept_data, original_user_prompt=""):
    identity = json.loads(_concept_identity(concept_data))
    machine_name = _compact_text(concept_data["title"], limit=120)
    operating_environment = identity["intended_operating_environment"]
    primary_function = identity["primary_purpose"]
    visual_brief = _build_visual_brief(concept_data, original_user_prompt)
    primary_subject = visual_brief["primary_visual_subject"]
    components = _field_text(concept_data, "system_components")
    materials = _field_text(concept_data, "materials")
    requirements = _field_text(concept_data, "technical_requirements")
    principle = _field_text(concept_data, "modern_principle", limit=600)
    sketch = _field_text(concept_data, "leonardo_sketch_description", limit=700)
    modern_sketch = _field_text(concept_data, "modern_sketch_description", limit=700)
    shared_lineage = {
        "visual_brief": visual_brief,
        "primary_visual_subject": primary_subject,
        "purpose": primary_function,
        "workflow": principle,
        "functional_architecture": components,
        "recognizable_identity": primary_subject,
        "primary_users": identity["primary_users"],
        "core_inputs": identity["core_inputs"],
        "core_outputs": identity["core_outputs"],
    }
    leonardo_blueprint = {
        "machine_name": f"{machine_name} — Leonardo-era engineering interpretation",
        "primary_function": primary_function,
        "overall_silhouette": (
            f"The complete primary subject remains unmistakably {primary_subject}. "
            f"Use this concept-specific sketch as the form reference: {sketch}"
        ),
        "approximate_proportions": (
            "Use the real-world scale, span, and proportions implied by the use cases "
            f"and requirements; never force the concept into a human-scale cabinet. {requirements}"
        ),
        "dominant_structural_features": list(concept_data.get("system_components", []))[:5]
        or [primary_subject],
        "distinctive_visual_signature": (
            f"A recognizable Leonardo-era ancestor of {primary_subject}, preserving "
            "the concept's modular structure and purpose rather than a generic machine."
        ),
        "frame_construction": (
            f"Historically plausible load-bearing construction derived from the actual "
            f"concept components ({components}), using joinery and mechanisms available around 1505."
        ),
        "primary_materials": (
            f"Historically plausible equivalents of the requested material functions ({materials}): "
            "timber, wrought iron, bronze, rope, leather, canvas, and stone only where structurally appropriate."
        ),
        "primary_mechanism": (
            f"A mechanically credible 1505 analogue of this concept-specific operating "
            f"principle: {principle}. Preserve function; replace only anachronistic technology."
        ),
        "input_location": "The starting point of the actual workflow described by the concept and use cases.",
        "output_location": "The useful real-world outcome of the actual workflow described by the concept and use cases.",
        "power_source": (
            "Only context-appropriate human, animal, gravity, water, wind, spring, "
            "counterweight, or pulley power; use no electricity."
        ),
        "visible_moving_components": list(concept_data.get("system_components", []))[:5]
        or ["Concept-specific mechanical linkages"],
        "operator_position": (
            f"Operators from the intended user groups work at physically credible access "
            f"points without obscuring the primary subject: {identity['primary_users']}"
        ),
        "typical_environment": (
            f"A dry, working High Renaissance installation suited to: {operating_environment}"
        ),
        "characteristic_color_palette": "Dark timber, aged bronze, wrought iron, rope, leather, stone, and natural canvas.",
        "key_recognizable_details": list(concept_data.get("technical_requirements", []))[:5]
        or [primary_subject],
    }
    modern_blueprint = {
        "machine_name": f"{machine_name} — Modern implementation",
        "primary_function": primary_function,
        "overall_silhouette": (
            f"The complete primary subject is unmistakably {primary_subject}. "
            f"Follow the actual modern sketch description: {modern_sketch}"
        ),
        "approximate_proportions": (
            f"Real-world scale and proportions appropriate to the stated environment, "
            f"use cases, deployment, and requirements; never default to a cabinet. {requirements}"
        ),
        "dominant_structural_features": list(concept_data.get("system_components", []))[:5]
        or [primary_subject],
        "distinctive_visual_signature": (
            f"The product is recognized first as {primary_subject}; component placement "
            "must express the source idea, not a reusable factory-machine template."
        ),
        "frame_construction": (
            f"A buildable, maintainable contemporary structure derived from these "
            f"concept-specific components and requirements: {components}; {requirements}"
        ),
        "primary_materials": materials,
        "primary_mechanism": principle,
        "input_location": "The real starting point of the concept-specific deployment or operating workflow.",
        "output_location": "The intended real-world result and service delivered by the concept.",
        "power_source": (
            "Use only power sources explicitly stated or credibly implied by the source idea and components."
        ),
        "visible_moving_components": list(concept_data.get("system_components", []))[:5]
        or ["Concept-specific moving or deployable components"],
        "operator_position": (
            f"Real users interact only at plausible deployment, control, maintenance, "
            f"loading, or access points: {identity['primary_users']}"
        ),
        "typical_environment": (
            f"A clean present-day installation appropriate to: {operating_environment}"
        ),
        "characteristic_color_palette": "Material-authentic contemporary engineering finishes with restrained safety markings.",
        "key_recognizable_details": list(concept_data.get("technical_requirements", []))[:5]
        or [primary_subject],
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

    lineage = design_blueprint["shared_invention_lineage"]
    visual_brief = lineage["visual_brief"]
    era_brief = {
        "name": blueprint["machine_name"],
        "overall_form_and_scale": (
            f'{blueprint["overall_silhouette"]} {blueprint["approximate_proportions"]}'
        ),
        "structural_features": blueprint["dominant_structural_features"],
        "construction_and_materials": (
            f'{blueprint["frame_construction"]} {blueprint["primary_materials"]}'
        ),
        "operating_principle": blueprint["primary_mechanism"],
        "environment_and_users": (
            f'{blueprint["typical_environment"]} {blueprint["operator_position"]}'
        ),
        "recognizable_details": blueprint["key_recognizable_details"],
    }
    return (
        f'PRIMARY VISUAL SUBJECT: {lineage["primary_visual_subject"]}\n\n'
        "CONCEPT-SPECIFIC VISUAL BRIEF:\n"
        + json.dumps(visual_brief, ensure_ascii=False, indent=2)
        + "\n\nERA IMPLEMENTATION BRIEF:\n"
        + json.dumps(era_brief, ensure_ascii=False, indent=2)
    )


def _assemble_concept_image_prompt(blueprint, primary_subject, role, sections):
    identity_lock = f"""
This image must depict exactly the same primary subject described below: {primary_subject}.

The primary subject must be immediately recognizable, complete enough to understand, and visually dominant. Preserve its real-world scale and category. Never replace it with a generic processing machine, cabinet, kiosk, or unrelated apparatus.

Do not redesign the product.

Do not invent a new geometry.

Only change camera position, activity, environment and human interaction.

The Design Blueprint has higher priority than every role-specific instruction. The role may change only viewpoint, process state, surrounding scene, and human activity. It must not replace or contradict concept-defining components in the blueprint.

Do not depict a standalone factory machine, printer, crusher, vending-machine-like enclosure, or unrelated industrial cabinet as the primary subject.
"""
    ordered_sections = (
        ("1. Design Blueprint — highest priority", blueprint),
        ("2. Primary subject identity lock", identity_lock),
        ("3. Exact image role", role),
        *sections,
    )
    return "\n\n".join(
        f"{heading}\n{body.strip()}" for heading, body in ordered_sections
    )


def build_leonardo_concept_image_prompts(concept_data, design_blueprint):
    blueprint = _serialize_era_blueprint(design_blueprint, "leonardo_blueprint")
    primary_subject = design_blueprint["shared_invention_lineage"][
        "primary_visual_subject"
    ]
    era_interpretation = """
Priority instruction: create a genuine historical reconstruction of how Leonardo da Vinci or a skilled High Renaissance engineer might have attempted this purpose around the year 1505. Redesign the invention from first principles using only knowledge, energy sources, tools, manufacturing methods, and mechanisms historically plausible in 1505. This must be a pre-industrial mechanical interpretation, not a modern product placed in a Renaissance room.

If the purpose depends on technology impossible in 1505, replace it with an ingenious functional analogue: balances, floats, lenses, sieves, resonance, pressure plates, or manual inspection for sensing; gears, cams, encoded drums, rotating discs, or trained operators for computation; clockwork, gravity, water, wind, springs, animal power, or human power for autonomous motion; and historically plausible sorting by size, weight, density, magnetism, shape, or manual selection.

Render a photorealistic cinematic physical scene. Do not render a sketch, blueprint, diagram, sepia illustration, manuscript page, or modern cutaway infographic.
"""
    historical_materials = """
Use only function-appropriate materials and mechanisms plausible around 1505: oak, walnut, carved timber, bronze, brass, copper, wrought iron, hand-forged steel tools, leather belts, rope drives, wooden or bronze gears, pulleys, cams, cranks, flywheels, counterweights, springs, water power, human power, animal power, wind power, gravity-fed mechanisms, glass lenses, parchment, hand-painted markings, rivets, pins, pegs, and mechanical linkages.

The invention must visibly rely on a function-appropriate carved timber load-bearing structure, exposed bronze or brass motion-transfer components where useful, and one distinctive dominant mechanical feature appropriate to the concept—such as a wheel, gear train, pulley cluster, counterweight assembly, or lens mechanism.
"""
    historical_prohibitions = """
Strictly prohibit visibly modern technology and settings: electricity, electric motors, batteries, wires, LEDs, illuminated digital screens, LCD or OLED displays, touchscreens, digital interfaces, computer-vision cameras, modern optical sensors, microchips, circuit boards, artificial-intelligence interfaces, contemporary robotic arms, modern industrial robot joints, plastics, aluminium extrusions, carbon fibre, injection-moulded parts, stainless-steel appliance housings, contemporary industrial housings, modern bins with printed recycling icons, modern factories, contemporary branding, modern apartments, modern clothing, and modern typography.

Also prohibit logos, product names printed on the invention, interface paragraphs, signs, labels, watermarks, recycling symbols, random letters, and pseudo-text. Never depict a modern product merely decorated with wood, brass, warm lighting, or Renaissance ornament.
"""
    historical_continuity = """
Within the Leonardo set, preserve the same broad proportions and recognizable historical invention identity in all three images. Repeat the same load-bearing construction, the same bronze or brass drive system where functionally appropriate, and the same selected dominant mechanical feature. Keep the concept-specific workflow and structural layout consistent. Change camera position and human activity, not the invention's identity.

Across eras, preserve the purpose and functional lineage from the shared identity, but do not copy a modern casing, robotic arm, sensor array, interface, or manufacturing design. The Renaissance invention must be an era-appropriate mechanical ancestor, not the same object with different styling.
"""
    square_readability = """
Square image composed for a compact slot: one clearly readable primary invention, strong silhouette, important structure and mechanism away from the edges, no split screen, no collage, no multiple panels, no excessive empty space, and no malformed text. Keep the invention visually dominant even when people are present.
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
    if "bridge" in primary_subject.casefold():
        roles = (
            (
                "leonardo_concept_1",
                "Historical overview of the complete modular emergency bridge. Show the bridge spanning a damaged river crossing as the dominant subject, with its full deck, modular sections, supports, adjustable span, and both riverbanks readable.",
                "Elevated three-quarter wide overview after a flood or landslide. The complete Leonardo-era bridge occupies approximately 65–80% of the frame and visibly connects the broken route across the river. Show repeated timber-and-wrought-iron modular spans and compact transportable sections staged near one bank. No close-up, no isolated mechanism, and no workshop-bound machine.",
                "Reveal the full load path, modular deck and truss sections, bank anchoring, adjustable-span joints, ropes, pulleys, winches, counterweights, and rapid-deployment logic. Solar sensors, AI monitoring, and robotic assembly from the source concept must appear only as historically plausible mechanical observation and assisted-assembly analogues, never as modern electronics.",
            ),
            (
                "leonardo_concept_2",
                "Engineering detail of the same modular emergency bridge. Explain how bridge sections connect and how the span is deployed without losing the identity of a bridge across a damaged river crossing.",
                "Closer oblique technical view from riverbank level, different from Image 1. Keep enough of the deck and opposite bank visible to prove this is a bridge, while foregrounding one modular joint, lifting frame, adjustable support, and rope-and-winch assembly. Do not crop into an ambiguous standalone machine.",
                "Show a clear cause-and-effect deployment mechanism: interchangeable bridge modules being aligned and locked, timber or metal pins and braces taking load, pulleys and counterweights extending the span, and repairable recyclable-era materials. The mechanism belongs to the bridge structure; it is not a factory device.",
            ),
            (
                "leonardo_concept_3",
                "Historical deployment scene of the same modular emergency bridge during civilian rescue. Show rapid field assembly and immediate practical use after a disaster.",
                "Wider river-crossing scene with a clearly different camera position and one to three historically dressed engineers, builders, or rescuers deploying modular bridge sections from carts at a flood-damaged route. Keep the large bridge and the crossing dominant; people provide scale and workflow rather than becoming the subject.",
                "Show transportable modules arriving by period carts, mechanical assisted assembly, adjustable span fitting the river width and terrain, rescuers securing the structure, and civilians or essential supplies beginning to cross. Preserve the modern concept's disaster-response and remote-infrastructure purpose through historically plausible means.",
            ),
        )

    return {
        image_type: _assemble_concept_image_prompt(
            blueprint,
            primary_subject,
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
    primary_subject = design_blueprint["shared_invention_lineage"][
        "primary_visual_subject"
    ]
    era_interpretation = """
Priority instruction: create a realistic present-day engineering implementation of the shared purpose. Translate the function into a commercially plausible product, service system, vehicle, structure, or piece of infrastructure using contemporary manufacturing and safety practices. The result must look buildable, maintainable, usable, and appropriate for the stated users and operating environment.

Use modern technology only when it serves the concept: industrial design, electric actuators, computer vision, modern sensors, robotics, contemporary safety systems, and practical controls. This is the evolutionary descendant of the Renaissance interpretation, not the same historical object in cooler lighting and not an unexplained science-fiction device.

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

Across eras, preserve the shared purpose, scale, and functional lineage, but do not retain identical casing, robotic arms, interfaces, joints, manufacturing design, or materials from the Leonardo-era invention. The modern result should feel like a practical technological descendant rather than the same object in another room.
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
    if "bridge" in primary_subject.casefold():
        roles = (
            (
                "modern_concept_1",
                "Deployed-system overview. Show the complete present-day modular emergency bridge already spanning a flood-damaged river crossing as the dominant primary subject.",
                "Clean elevated three-quarter wide view showing both riverbanks, the interrupted road, and the full adjustable bridge span. The bridge occupies approximately 65–80% of the frame. Its repeated lightweight modular deck and truss sections, approach ramps, supports, and integrated solar sensor nodes are plainly visible. No isolated product cabinet and no close-up.",
                "Show a credible truck-transportable bridge system in service: recyclable alloy and composite modules, adjustable span matched to the river width and terrain, structural monitoring sensors powered by compact solar panels, safe barriers, load-bearing joints, and a restored route after flood, earthquake, or landslide damage.",
            ),
            (
                "modern_concept_2",
                "Truck transport and robotic assembly. Show the same modular emergency bridge actively extending across the damaged river crossing during rapid deployment.",
                "Operational riverbank view, lower and closer than Image 1, with standard trucks delivering bridge modules and robotic assembly units lifting, aligning, and locking a span section into the bridge. Keep the growing bridge, river gap, and opposite-bank destination visible so the equipment cannot be mistaken for a standalone factory machine.",
                "Make the deployment sequence visually explicit: modules unload from standard trucks, robotic assembly mechanisms position recyclable lightweight sections, adjustable connectors lock the span, and solar-powered sensors begin structural checks through an AI-assisted monitoring system. Show credible outriggers, rigging, safety zones, and terrain adaptation.",
            ),
            (
                "modern_concept_3",
                "Civilian rescue and remote-infrastructure use. Show the same completed modular emergency bridge restoring access through a disaster area.",
                "Wider human-context scene from a third viewpoint: emergency crews supervise the monitored crossing while rescue vehicles, civilians, or infrastructure supplies use the bridge over a damaged river route. The complete bridge remains large, unobscured, and visually dominant; users demonstrate scale and value.",
                "Show a believable operational outcome: rapid emergency access, safe traffic flow, adjustable modular structure, solar sensor nodes, AI-assisted structural monitoring at a restrained field control point, and standard trucks or robotic modules parked after assembly. The scene must communicate civilian rescue and remote-infrastructure readiness.",
            ),
        )

    return {
        image_type: _assemble_concept_image_prompt(
            blueprint,
            primary_subject,
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
