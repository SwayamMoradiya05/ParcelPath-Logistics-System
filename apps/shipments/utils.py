import random
import string


def generate_tracking_number():
    prefix = "PP"

    random_part = "".join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=10,
        )
    )

    return f"{prefix}{random_part}"


def calculate_shipping_cost(
    weight,
    distance,
    base_charge=50,
):
    weight_charge = float(weight) * 8

    distance_charge = float(distance) * 2

    total = (
        base_charge
        + weight_charge
        + distance_charge
    )

    return round(total, 2)


def volumetric_weight(
    length,
    width,
    height,
):
    return round(
        (length * width * height) / 5000,
        2,
    )


def chargeable_weight(
    actual_weight,
    volumetric,
):
    return max(
        actual_weight,
        volumetric,
    )

import base64
from io import BytesIO

import barcode
import qrcode
from barcode.writer import ImageWriter


def generate_qr_code(data):

    qr = qrcode.QRCode(
        version=1,
        box_size=8,
        border=2,
    )

    qr.add_data(data)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    buffer = BytesIO()

    image.save(buffer, format="PNG")

    return base64.b64encode(
        buffer.getvalue()
    ).decode()


def generate_barcode(data):

    code128 = barcode.get(
        "code128",
        data,
        writer=ImageWriter(),
    )

    buffer = BytesIO()

    code128.write(buffer)

    return base64.b64encode(
        buffer.getvalue()
    ).decode()