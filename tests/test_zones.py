from parking_monitor.zones import Zone, occupied_zone_names

SPOT = Zone("spot_1", [[0, 0], [100, 0], [100, 100], [0, 100]])


def test_box_whose_bottom_center_is_in_zone_is_counted():
    assert occupied_zone_names([(40, 10, 60, 90)], [SPOT]) == {"spot_1"}


def test_box_outside_zone_is_not_counted():
    assert occupied_zone_names([(150, 10, 190, 90)], [SPOT]) == set()


def test_box_whose_center_is_in_zone_but_bottom_is_outside_is_not_counted():
    # Center is (50, 50) inside the zone, but the bottom edge (y=150) is outside.
    assert occupied_zone_names([(40, 0, 60, 150)], [SPOT]) == set()
