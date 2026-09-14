"""Canonical project-category taxonomy shared by every Leonardo surface."""

CATEGORY_KEYS = (
    "ai_software",
    "robotics_automation",
    "transport_mobility",
    "construction_architecture",
    "infrastructure",
    "manufacturing_industry",
    "energy",
    "climate_environment",
    "water",
    "health_biotech",
    "agriculture_food",
    "aerospace_space",
    "defense_security",
    "emergency_rescue",
    "materials_deeptech",
    "finance_commerce",
    "education",
    "consumer_lifestyle",
)

CATEGORY_TRANSLATIONS = {
    "en": (
        "AI & Software", "Robotics & Automation", "Transport & Mobility",
        "Construction & Architecture", "Infrastructure", "Manufacturing & Industry",
        "Energy", "Climate & Environment", "Water", "Health & Biotech",
        "Agriculture & Food", "Aerospace & Space", "Defense & Security",
        "Emergency & Rescue", "Materials & Deep Tech", "Finance & Commerce",
        "Education", "Consumer & Lifestyle",
    ),
    "es": (
        "IA y software", "Robótica y automatización", "Transporte y movilidad",
        "Construcción y arquitectura", "Infraestructura", "Manufactura e industria",
        "Energía", "Clima y medio ambiente", "Agua", "Salud y biotecnología",
        "Agricultura y alimentación", "Aeronáutica y espacio", "Defensa y seguridad",
        "Emergencias y rescate", "Materiales y tecnología avanzada", "Finanzas y comercio",
        "Educación", "Consumo y estilo de vida",
    ),
    "pt": (
        "IA e software", "Robótica e automação", "Transportes e mobilidade",
        "Construção e arquitetura", "Infraestruturas", "Manufatura e indústria",
        "Energia", "Clima e ambiente", "Água", "Saúde e biotecnologia",
        "Agricultura e alimentação", "Aeronáutica e espaço", "Defesa e segurança",
        "Emergência e salvamento", "Materiais e tecnologia avançada", "Finanças e comércio",
        "Educação", "Consumo e estilo de vida",
    ),
    "fr": (
        "IA et logiciels", "Robotique et automatisation", "Transport et mobilité",
        "Construction et architecture", "Infrastructures", "Production et industrie",
        "Énergie", "Climat et environnement", "Eau", "Santé et biotechnologies",
        "Agriculture et alimentation", "Aéronautique et espace", "Défense et sécurité",
        "Urgence et secours", "Matériaux et technologies de rupture", "Finance et commerce",
        "Éducation", "Consommation et mode de vie",
    ),
    "de": (
        "KI & Software", "Robotik & Automatisierung", "Transport & Mobilität",
        "Bauwesen & Architektur", "Infrastruktur", "Fertigung & Industrie",
        "Energie", "Klima & Umwelt", "Wasser", "Gesundheit & Biotechnologie",
        "Landwirtschaft & Ernährung", "Luft- & Raumfahrt", "Verteidigung & Sicherheit",
        "Notfall & Rettung", "Materialien & Spitzentechnologie", "Finanzen & Handel",
        "Bildung", "Konsum & Lebensstil",
    ),
    "it": (
        "IA e software", "Robotica e automazione", "Trasporti e mobilità",
        "Costruzioni e architettura", "Infrastrutture", "Produzione e industria",
        "Energia", "Clima e ambiente", "Acqua", "Salute e biotecnologie",
        "Agricoltura e alimentazione", "Aeronautica e spazio", "Difesa e sicurezza",
        "Emergenza e soccorso", "Materiali e tecnologie avanzate", "Finanza e commercio",
        "Istruzione", "Consumo e stile di vita",
    ),
    "ru": (
        "ИИ и программное обеспечение", "Робототехника и автоматизация", "Транспорт и мобильность",
        "Строительство и архитектура", "Инфраструктура", "Производство и промышленность",
        "Энергетика", "Климат и окружающая среда", "Водные технологии", "Здравоохранение и биотехнологии",
        "Сельское хозяйство и продовольствие", "Авиация и космос", "Оборона и безопасность",
        "Чрезвычайные ситуации и спасение", "Материалы и глубокие технологии", "Финансы и торговля",
        "Образование", "Потребительские решения и образ жизни",
    ),
    "sv": (
        "AI och programvara", "Robotik och automation", "Transport och mobilitet",
        "Byggande och arkitektur", "Infrastruktur", "Tillverkning och industri",
        "Energi", "Klimat och miljö", "Vatten", "Hälsa och bioteknik",
        "Jordbruk och livsmedel", "Flyg och rymd", "Försvar och säkerhet",
        "Nödläge och räddning", "Material och avancerad teknik", "Finans och handel",
        "Utbildning", "Konsument och livsstil",
    ),
    "fi": (
        "Tekoäly ja ohjelmistot", "Robotiikka ja automaatio", "Liikenne ja liikkuminen",
        "Rakentaminen ja arkkitehtuuri", "Infrastruktuuri", "Valmistus ja teollisuus",
        "Energia", "Ilmasto ja ympäristö", "Vesi", "Terveys ja bioteknologia",
        "Maatalous ja ruoka", "Ilmailu ja avaruus", "Puolustus ja turvallisuus",
        "Hätätilanteet ja pelastus", "Materiaalit ja syväteknologia", "Rahoitus ja kauppa",
        "Koulutus", "Kuluttajat ja elämäntapa",
    ),
    "pl": (
        "AI i oprogramowanie", "Robotyka i automatyzacja", "Transport i mobilność",
        "Budownictwo i architektura", "Infrastruktura", "Produkcja i przemysł",
        "Energia", "Klimat i środowisko", "Woda", "Zdrowie i biotechnologia",
        "Rolnictwo i żywność", "Lotnictwo i kosmos", "Obronność i bezpieczeństwo",
        "Ratownictwo i sytuacje kryzysowe", "Materiały i zaawansowane technologie", "Finanse i handel",
        "Edukacja", "Konsument i styl życia",
    ),
    "zh": (
        "人工智能与软件", "机器人与自动化", "交通与出行",
        "建筑与设计", "基础设施", "制造与工业",
        "能源", "气候与环境", "水务", "健康与生物科技",
        "农业与食品", "航空与航天", "国防与安全",
        "应急与救援", "材料与深度科技", "金融与商业",
        "教育", "消费与生活方式",
    ),
    "ja": (
        "AI・ソフトウェア", "ロボティクス・自動化", "交通・モビリティ",
        "建設・建築", "インフラ", "製造・産業",
        "エネルギー", "気候・環境", "水", "医療・バイオテクノロジー",
        "農業・食品", "航空・宇宙", "防衛・セキュリティ",
        "緊急対応・救助", "材料・ディープテック", "金融・商取引",
        "教育", "消費者・ライフスタイル",
    ),
    "ko": (
        "AI 및 소프트웨어", "로보틱스 및 자동화", "교통 및 모빌리티",
        "건설 및 건축", "인프라", "제조 및 산업",
        "에너지", "기후 및 환경", "물", "헬스케어 및 바이오테크",
        "농업 및 식품", "항공우주", "국방 및 보안",
        "재난 대응 및 구조", "소재 및 딥테크", "금융 및 상거래",
        "교육", "소비자 및 라이프스타일",
    ),
}

LEGACY_CATEGORY_MAP = {
    "transport": "transport_mobility",
    "construction": "construction_architecture",
    "architecture": "construction_architecture",
    "rescue": "emergency_rescue",
    "military": "defense_security",
    "industrial": "manufacturing_industry",
    "mechanical": "manufacturing_industry",
    "energy": "energy",
    "water": "water",
    "flight": "aerospace_space",
    "space": "aerospace_space",
    "agriculture": "agriculture_food",
    "medicine": "health_biotech",
    "robotics": "robotics_automation",
    "technology": "ai_software",
    "health": "health_biotech",
    "infrastructure": "infrastructure",
    "environment": "climate_environment",
    "ai": "ai_software",
}

_ENGLISH_NAME_TO_KEY = {
    name.casefold(): key
    for key, name in zip(CATEGORY_KEYS, CATEGORY_TRANSLATIONS["en"])
}


def category_translation_key(category_key: str) -> str:
    """Return the shared i18n key for a canonical category."""
    if category_key not in CATEGORY_KEYS:
        raise ValueError(f"Unsupported project category: {category_key}")
    return f"category.{category_key}"


def normalize_category(value) -> str | None:
    """Normalize canonical and explicitly mapped legacy identifiers."""
    normalized = " ".join(str(value or "").split()).casefold()
    if normalized in CATEGORY_KEYS:
        return normalized
    return LEGACY_CATEGORY_MAP.get(normalized) or _ENGLISH_NAME_TO_KEY.get(normalized)


def require_category_key(value) -> str:
    """Return a canonical category key or reject arbitrary values."""
    category_key = normalize_category(value)
    if category_key is None:
        raise ValueError(f"Unsupported project category: {value}")
    return category_key

