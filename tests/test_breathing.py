"""Tests für Atemschutz-Service."""
from app.services.breathing_service import calc_withdraw_pressure, get_warning_level
from app.models.breathing import BreathingTroop


def test_withdraw_pressure_calculation():
    assert calc_withdraw_pressure(300, 0.5, 10) == 160.0
    assert calc_withdraw_pressure(200, 0.5, 10) == 110.0


def test_warning_level_ok():
    troop = BreathingTroop()
    troop.start_press_avg = 300
    troop.withdraw_press_calc = 160
    troop.pressure_logs = []
    assert get_warning_level(troop) == "ok"  # no logs → ok


def test_warning_level_yellow():
    from app.models.breathing import PressureLog
    troop = BreathingTroop()
    troop.start_press_avg = 300
    troop.withdraw_press_calc = 160
    log = PressureLog()
    log.pressure_bar = 220  # 300 * 0.75 = 225, below threshold → yellow
    troop.pressure_logs = [log]
    assert get_warning_level(troop) == "yellow"


def test_warning_level_red():
    from app.models.breathing import PressureLog
    troop = BreathingTroop()
    troop.start_press_avg = 300
    troop.withdraw_press_calc = 160
    log = PressureLog()
    log.pressure_bar = 155  # below 160 → red
    troop.pressure_logs = [log]
    assert get_warning_level(troop) == "red"
