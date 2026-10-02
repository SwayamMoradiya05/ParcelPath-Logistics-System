from math import radians
from math import sin
from math import cos
from math import sqrt
from math import atan2


def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2,
):
    radius = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a),
    )

    return round(radius * c, 2)


def estimate_duration(
    distance,
    average_speed=45,
):
    if average_speed <= 0:
        return 0

    hours = distance / average_speed

    return round(hours * 60)


def optimize_stop_numbers(route):
    shipments = (
        route.route_shipments
        .order_by("stop_number")
    )

    for index, item in enumerate(shipments, start=1):
        if item.stop_number != index:
            item.stop_number = index
            item.save(update_fields=["stop_number"])