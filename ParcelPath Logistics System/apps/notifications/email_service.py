from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone


class EmailService:

    @staticmethod
    def send_delivery_confirmation(shipment):
        """
        Send a delivery confirmation email to the registered
        customer immediately after successful delivery.
        """

        try:
            customer_user = shipment.customer.user

            recipient_email = customer_user.email

            if not recipient_email:
                return False

            customer_name = (
                customer_user.full_name
                or customer_user.get_full_name()
                or recipient_email
            )

            driver_name = "Not Assigned"
            driver_phone = ""
            vehicle_number = ""

            if shipment.driver:
                driver_user = shipment.driver.user

                driver_name = (
                    driver_user.full_name
                    or driver_user.get_full_name()
                    or driver_user.email
                )

                driver_phone = (
                    getattr(
                        driver_user,
                        "phone",
                        "",
                    )
                    or ""
                )

                vehicle_number = (
                    getattr(
                        shipment.driver,
                        "vehicle_number",
                        "",
                    )
                    or ""
                )

            delivered_at = (
                shipment.delivered_at
                or timezone.now()
            )

            context = {
                "shipment": shipment,
                "customer_name": customer_name,
                "driver_name": driver_name,
                "driver_phone": driver_phone,
                "vehicle_number": vehicle_number,
                "delivered_at": delivered_at,
                "tracking_url": (
                    f"{getattr(settings, 'SITE_URL', '').rstrip('/')}"
                    f"/shipments/track/"
                    f"{shipment.tracking_number}/"
                ),
                "company_name": getattr(
                    settings,
                    "COMPANY_NAME",
                    "ParcelPath Logistics",
                ),
                "support_email": getattr(
                    settings,
                    "SUPPORT_EMAIL",
                    "",
                ),
            }

            subject = (
                f"ParcelPath | Shipment "
                f"{shipment.tracking_number} "
                f"Delivered Successfully"
            )

            text_content = render_to_string(
                "emails/delivery_confirmation.txt",
                context,
            )

            html_content = render_to_string(
                "emails/delivery_confirmation.html",
                context,
            )

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=getattr(
                    settings,
                    "DEFAULT_FROM_EMAIL",
                    settings.EMAIL_HOST_USER,
                ),
                to=[recipient_email],
            )

            email.attach_alternative(
                html_content,
                "text/html",
            )

            # ----------------------------------------------------
            # Attach Proof of Delivery
            # ----------------------------------------------------

            if shipment.proof_of_delivery:

                try:
                    proof_file = shipment.proof_of_delivery.open(
                        "rb"
                    )

                    email.attach(
                        shipment.proof_of_delivery.name.split("/")[-1],
                        proof_file.read(),
                        (
                            shipment.proof_of_delivery.file
                            .content_type
                        ),
                    )

                    proof_file.close()

                except Exception:
                    # Email should still be sent even if
                    # the proof attachment cannot be loaded.
                    pass

            email.send(
                fail_silently=False
            )

            return True

        except Exception:
            return False