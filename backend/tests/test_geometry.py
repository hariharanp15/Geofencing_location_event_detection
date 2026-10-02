from app.services.geometry import distance_meters, point_in_polygon


def test_distance_at_same_coordinate_is_zero():
    assert distance_meters(12.9716, 77.5946, 12.9716, 77.5946) == 0


def test_distance_is_about_one_degree_latitude():
    assert 111_000 < distance_meters(0, 0, 1, 0) < 112_000


def test_point_in_polygon_includes_interior_and_excludes_exterior():
    square = [(0, 0), (0, 1), (1, 1), (1, 0)]
    assert point_in_polygon(0.5, 0.5, square)
    assert not point_in_polygon(1.5, 0.5, square)
