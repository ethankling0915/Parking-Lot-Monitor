from parking_monitor.occupancy import ZoneState


def test_change_is_reported_once_it_holds_for_the_debounce_period():
    state = ZoneState("spot_1", debounce_seconds=5)
    assert state.update(0, True) is None
    assert state.update(3, True) is None
    assert state.update(5, True) == "occupied"
    assert state.occupied


def test_brief_blip_is_ignored():
    state = ZoneState("spot_1", debounce_seconds=5)
    state.update(0, True)
    state.update(2, False)  # the blip ends before the debounce period
    assert state.update(10, True) is None  # timing restarts at 10
    assert not state.occupied


def test_vacant_is_reported_after_occupied():
    state = ZoneState("spot_1", debounce_seconds=5)
    state.update(0, True)
    assert state.update(5, True) == "occupied"
    state.update(10, False)
    assert state.update(15, False) == "vacant"
