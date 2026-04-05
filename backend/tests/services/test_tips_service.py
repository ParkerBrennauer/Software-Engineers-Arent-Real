import pytest
from src.services.tips_service import TipService


def test_calculate_tip_percent():
    result = TipService.calculate_tip(100, tip_percent=10)
    assert result == 10.0

def test_calculate_tip_fixed():
    result = TipService.calculate_tip(100, tip_amount=15)
    assert result == 15.0

def test_calculate_tip_both_provided():
    with pytest.raises(ValueError):
        TipService.calculate_tip(100, tip_percent=10, tip_amount=5)

def test_calculate_tip_negative_percent():
    with pytest.raises(ValueError):
        TipService.calculate_tip(100, tip_percent=-5)

def test_calculate_tip_negative_amount():
    with pytest.raises(ValueError):
        TipService.calculate_tip(100, tip_amount=-10)

def test_calculate_tip_missing_inputs():
    with pytest.raises(ValueError):
        TipService.calculate_tip(100)
