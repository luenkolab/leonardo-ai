import random


INVENTIONS = {
    "flight": [
        {
            "name": "Ornithopter",
            "leonardo_description": (
                "A flying machine with large mechanical wings inspired by birds."
            ),
            "mechanism": (
                "The machine uses pedals, gears, and levers to move articulated wings "
                "up and down, attempting to create lift through repeated flapping motion."
            ),
            "modern_version": "Autonomous reconnaissance drone",
            "modern_mechanism": (
                "The modern version replaces muscle power with electric motors and uses "
                "lightweight propellers, sensors, and control software to generate lift, "
                "maintain balance, and navigate through the air."
            ),
            "market_demand": "High",
            "roi": "Strong long-term potential",
            "difficulty": "High",
        },
        {
            "name": "Aerial Screw",
            "leonardo_description": (
                "A spiral-shaped flying device designed to rise into the air."
            ),
            "mechanism": (
                "The invention uses a rotating helical surface intended to compress air "
                "downward. Leonardo imagined that the spiral, when spun quickly enough, "
                "could lift the structure upward."
            ),
            "modern_version": "Vertical takeoff rescue helicopter",
            "modern_mechanism": (
                "The modern version uses powered rotor blades to generate lift by forcing "
                "air downward. Blade pitch, engine power, and stabilization systems allow "
                "vertical takeoff, hovering, and controlled movement."
            ),
            "market_demand": "High",
            "roi": "High in specialized sectors",
            "difficulty": "Very High",
        },
    ],
    "war": [
        {
            "name": "Armored Vehicle",
            "leonardo_description": (
                "A covered combat vehicle protected by a circular armored shell."
            ),
            "mechanism": (
                "The vehicle is driven by internal cranks connected to wheels, while "
                "sloped outer armor helps deflect enemy attacks. Weapons are placed "
                "around the perimeter for multi-direction defense."
            ),
            "modern_version": "Autonomous armored ground robot",
            "modern_mechanism": (
                "The modern version uses electric or hybrid drive systems, reinforced "
                "armor, onboard cameras, sensors, and software to move across terrain "
                "and support defense or reconnaissance operations."
            ),
            "market_demand": "Medium",
            "roi": "Moderate but strategic",
            "difficulty": "High",
        },
        {
            "name": "Rapid-Fire Crossbow Platform",
            "leonardo_description": (
                "A rotating launch platform designed to increase battlefield firing speed."
            ),
            "mechanism": (
                "The platform arranges several projectile launch points in sequence, "
                "allowing one section to be reloaded while another is aimed and fired, "
                "reducing downtime between shots."
            ),
            "modern_version": "Automated modular defense turret",
            "modern_mechanism": (
                "The modern version uses motorized targeting, a controlled firing system, "
                "and computer-assisted aiming to improve speed, precision, and response time."
            ),
            "market_demand": "Medium",
            "roi": "Sector-dependent",
            "difficulty": "Very High",
        },
    ],
    "water": [
        {
            "name": "Water Lifting Machine",
            "leonardo_description": (
                "A mechanical device created to move water upward for irrigation and labor."
            ),
            "mechanism": (
                "The machine uses rotating scoops or screw-like geometry to capture water "
                "and raise it from a lower level to a higher channel."
            ),
            "modern_version": "Smart solar irrigation pump",
            "modern_mechanism": (
                "The modern version uses solar energy, an electric pump, and automated "
                "flow control. Sensors can measure soil moisture and activate pumping "
                "only when watering is actually needed."
            ),
            "market_demand": "High",
            "roi": "Excellent in agriculture",
            "difficulty": "Medium",
        },
        {
            "name": "Canal Lock Assistant",
            "leonardo_description": (
                "A mechanism meant to improve navigation and water level control in canals."
            ),
            "mechanism": (
                "The design manages water flow through controlled gates and chamber logic, "
                "allowing vessels to rise or descend between different water levels."
            ),
            "modern_version": "Automated canal logistics control system",
            "modern_mechanism": (
                "The modern version uses hydraulic gates, digital monitoring, and "
                "synchronized control software to manage water levels and vessel traffic "
                "with higher efficiency and safety."
            ),
            "market_demand": "Medium",
            "roi": "Stable infrastructure return",
            "difficulty": "High",
        },
    ],
    "transport": [
        {
            "name": "Self-Propelled Cart",
            "leonardo_description": (
                "A cart capable of moving without being pushed by a person or animal."
            ),
            "mechanism": (
                "The cart stores mechanical energy in wound springs and releases it "
                "through gears, allowing the wheels to move forward in a controlled way."
            ),
            "modern_version": "Autonomous delivery robot",
            "modern_mechanism": (
                "The modern version uses batteries, electric motors, wheel control systems, "
                "and route-planning software to move goods independently through indoor "
                "or urban environments."
            ),
            "market_demand": "High",
            "roi": "High in logistics",
            "difficulty": "Medium",
        },
        {
            "name": "Portable Military Bridge",
            "leonardo_description": (
                "A quickly deployable bridge for crossing rivers and battlefield gaps."
            ),
            "mechanism": (
                "The structure uses folding sections, pivot joints, and balanced supports "
                "to allow fast transport and quick unfolding across obstacles."
            ),
            "modern_version": "Rapid emergency bridge deployment system",
            "modern_mechanism": (
                "The modern version uses lightweight composite materials, hydraulic "
                "unfolding systems, and locking mechanisms to create a safe temporary "
                "bridge within minutes."
            ),
            "market_demand": "High",
            "roi": "Strong in emergency engineering",
            "difficulty": "High",
        },
    ],
}


def main():
    print("Leonardo AI")
    print("Renaissance invention generator with modern engineering analysis.")
    print()

    try:
        category = choose_category(
            input("Choose category (flight, war, water, transport): ")
        )
    except ValueError:
        print("Invalid category")
        return

    invention = generate_invention(category)
    report = build_report(invention)
    print(report)


def choose_category(user_input):
    category = user_input.strip().lower()
    if category not in INVENTIONS:
        raise ValueError("Invalid category")
    return category


def generate_invention(category):
    return random.choice(INVENTIONS[category])


def calculate_score(invention):
    demand_scores = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
    }

    roi_scores = {
        "Limited": 1,
        "Sector-dependent": 2,
        "Stable infrastructure return": 2,
        "Moderate but strategic": 2,
        "Strong long-term potential": 3,
        "High in specialized sectors": 3,
        "Excellent in agriculture": 3,
        "High in logistics": 3,
        "Strong in emergency engineering": 3,
    }

    difficulty_scores = {
        "Medium": 1,
        "High": 2,
        "Very High": 3,
    }

    demand = demand_scores[invention["market_demand"]]
    roi = roi_scores[invention["roi"]]
    difficulty = difficulty_scores[invention["difficulty"]]

    total = demand + roi - difficulty

    if total >= 4:
        return "Excellent project potential"
    if total >= 2:
        return "Promising with realistic challenges"
    return "Ambitious but difficult to scale"


def build_report(invention):
    score = calculate_score(invention)

    return (
        f"\nGenerated Invention: {invention['name']}\n"
        f"\nLeonardo Concept:\n"
        f"{invention['leonardo_description']}\n"
        f"\nHow It Works:\n"
        f"{invention['mechanism']}\n"
        f"\nModern Realization:\n"
        f"{invention['modern_version']}\n"
        f"\nHow the Modern Version Works:\n"
        f"{invention['modern_mechanism']}\n"
        f"\nMarket Demand: {invention['market_demand']}\n"
        f"Return Potential: {invention['roi']}\n"
        f"Engineering Difficulty: {invention['difficulty']}\n"
        f"\nProject Evaluation: {score}\n"
    )


if __name__ == "__main__":
    main()