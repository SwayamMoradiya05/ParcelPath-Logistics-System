from math import atan2
from math import cos
from math import radians
from math import sin
from math import sqrt


def haversine_distance(
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


def estimate_eta(
    distance_km,
    average_speed=40,
):
    if average_speed <= 0:
        return 0

    return round(
        distance_km / average_speed,
        2,
    )


def current_status_color(status):
    colors = {
        "CREATED": "secondary",
        "PICKUP_ASSIGNED": "info",
        "PICKED_UP": "primary",
        "IN_TRANSIT": "warning",
        "ARRIVED_AT_HUB": "dark",
        "OUT_FOR_DELIVERY": "info",
        "DELIVERED": "success",
        "RETURNED": "danger",
        "CANCELLED": "danger",
    }

    return colors.get(
        status,
        "secondary",
    )