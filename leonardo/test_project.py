import pytest
from project import choose_category, generate_invention, calculate_score, build_report


def test_choose_category_valid():
    assert choose_category("flight") == "flight"
    assert choose_category(" WATER ") == "water"
    assert choose_category("Transport") == "transport"


def test_choose_category_invalid():
    with pytest.raises(ValueError):
        choose_category("music")


def test_generate_invention():
    invention = generate_invention("transport")
    assert "name" in invention
    assert "mechanism" in invention
    assert "modern_version" in invention
    assert "modern_mechanism" in invention
    assert "market_demand" in invention
    assert "roi" in invention
    assert "difficulty" in invention


def test_calculate_score_excellent():
    invention = {
        "market_demand": "High",
        "roi": "High in logistics",
        "difficulty": "Medium",
    }
    assert calculate_score(invention) == "Excellent project potential"


def test_calculate_score_promising():
    invention = {
        "market_demand": "Medium",
        "roi": "Moderate but strategic",
        "difficulty": "High",
    }
    assert calculate_score(invention) == "Promising with realistic challenges"


def test_build_report():
    invention = {
        "name": "Test Machine",
        "leonardo_description": "A Renaissance concept machine.",
        "mechanism": "Uses gears and springs.",
        "modern_version": "Modern robotic system",
        "modern_mechanism": "Uses motors and sensors.",
        "market_demand": "Medium",
        "roi": "Moderate but strategic",
        "difficulty": "High",
    }

    report = build_report(invention)

    assert "Generated Invention: Test Machine" in report
    assert "Modern Realization:" in report
    assert "How the Modern Version Works:" in report
    assert "Uses motors and sensors." in report
    assert "Project Evaluation:" in report