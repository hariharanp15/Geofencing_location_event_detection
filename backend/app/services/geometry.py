import math

EARTH_RADIUS_METERS = 6_371_000


def distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_METERS * math.asin(math.sqrt(a))


def point_in_polygon(latitude: float, longitude: float, points: list[tuple[float, float]]) -> bool:
    """Ray casting: points on a practical map boundary count as inside."""
    inside = False
    j = len(points) - 1
    for i, (yi, xi) in enumerate(points):
        yj, xj = points[j]
        crosses = (xi > longitude) != (xj > longitude)
        if crosses and latitude < (yj - yi) * (longitude - xi) / (xj - xi) + yi:
            inside = not inside
        j = i
    return inside
