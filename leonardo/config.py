from categories import CATEGORY_KEYS


DIFFICULTY = {category: "High" for category in CATEGORY_KEYS}
DIFFICULTY.update({
    "ai_software": "Medium",
    "transport_mobility": "Medium",
    "manufacturing_industry": "Medium",
    "agriculture_food": "Medium",
    "finance_commerce": "Medium",
    "education": "Medium",
    "consumer_lifestyle": "Medium",
    "robotics_automation": "Extreme",
    "aerospace_space": "Extreme",
    "defense_security": "Extreme",
    "health_biotech": "Extreme",
    "materials_deeptech": "Extreme",
})


MATERIALS = {
    "ai_software": ["application runtime", "data interfaces", "model evaluation tools", "secure hosting"],
    "robotics_automation": ["robotic joints", "camera module", "control board", "precision actuators"],
    "transport_mobility": ["electric motor", "battery pack", "control system", "lightweight chassis"],
    "construction_architecture": ["structural frame", "modular joints", "lifting actuators", "composite panels"],
    "infrastructure": ["structural modules", "monitoring sensors", "control equipment", "protective enclosures"],
    "manufacturing_industry": ["industrial frame", "control unit", "precision actuators", "protective casing"],
    "energy": ["battery cells", "grid controller", "thermal insulation", "power conversion module"],
    "climate_environment": ["environmental sensors", "sampling equipment", "control unit", "weatherproof housing"],
    "water": ["sealed pressure shell", "fluid handling system", "waterproof sensors", "composite tubing"],
    "health_biotech": ["biocompatible housing", "diagnostic sensors", "microcontroller", "sterile casing"],
    "agriculture_food": ["soil sensors", "mechanical cultivator", "irrigation unit", "navigation controller"],
    "aerospace_space": ["lightweight composite", "guidance sensors", "autonomous control unit", "sealed energy module"],
    "defense_security": ["reinforced enclosure", "shock-resistant frame", "remote navigation system", "secure control module"],
    "emergency_rescue": ["lightweight rescue frame", "thermal sensors", "stabilization module", "safety harness"],
    "materials_deeptech": ["experimental material samples", "fabrication tooling", "measurement sensors", "test fixtures"],
    "finance_commerce": ["secure application runtime", "transaction interfaces", "audit storage", "analytics tools"],
    "education": ["learning interface", "content modules", "assessment tools", "accessible devices"],
    "consumer_lifestyle": ["user interface", "replaceable components", "control electronics", "durable housing"],
}


USE_CASES = {
    "ai_software": ["workflow automation", "decision support", "data analysis", "software services"],
    "robotics_automation": ["industrial automation", "inspection", "research", "assisted operations"],
    "transport_mobility": ["urban delivery", "smart mobility", "industrial logistics", "campus transport"],
    "construction_architecture": ["modular structures", "adaptive buildings", "civil engineering", "rapid construction"],
    "infrastructure": ["public works", "network resilience", "asset monitoring", "emergency restoration"],
    "manufacturing_industry": ["factory automation", "inspection workflows", "industrial maintenance", "production control"],
    "energy": ["smart power systems", "energy storage", "remote energy delivery", "industrial optimization"],
    "climate_environment": ["environmental monitoring", "emissions reduction", "ecosystem restoration", "climate resilience"],
    "water": ["water treatment", "underwater inspection", "water distribution", "environmental research"],
    "health_biotech": ["diagnostics", "remote monitoring", "clinical support", "biotechnology research"],
    "agriculture_food": ["precision farming", "soil monitoring", "food production", "automated harvesting"],
    "aerospace_space": ["aerial mapping", "orbital maintenance", "scientific observation", "space logistics"],
    "defense_security": ["protective engineering", "secure operations", "remote inspection", "resilience planning"],
    "emergency_rescue": ["fire evacuation", "mountain rescue", "disaster response", "rapid deployment"],
    "materials_deeptech": ["material validation", "advanced manufacturing", "performance testing", "research tooling"],
    "finance_commerce": ["financial operations", "commerce automation", "risk analysis", "transaction services"],
    "education": ["classroom learning", "technical training", "remote education", "skills assessment"],
    "consumer_lifestyle": ["home use", "personal productivity", "recreation", "daily-life assistance"],
}
