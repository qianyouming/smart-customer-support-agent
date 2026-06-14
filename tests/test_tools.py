from app.tools.calculator import run as calculate
from app.tools.search import run as search


def test_calculator() -> None:
    assert calculate("2 + 3 * 4") == "14"


def test_search() -> None:
    assert "3-5" in search("退款周期")

