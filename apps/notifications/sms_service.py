import logging

from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client
except Exception:
    Client = None


class SMSService:
    """
    Safe SMS Service.

    If anything fails,
    ParcelPath continues working normally.
    """

    @staticmethod
    def send(phone_number, message):

        if not Client:
            logger.warning("Twilio SDK not installed.")
            return False

        sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
        token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
        sender = getattr(settings, "TWILIO_PHONE_NUMBER", None)

        if not sid or not token or not sender:
            logger.warning("Twilio credentials not configured.")
            return False

        try:

            phone_number = phone_number.strip()

            if not phone_number.startswith("+"):
                phone_number = "+91" + phone_number

            client = Client(sid, token)

            print("Sending SMS...")
            print(f"To: {phone_number}")

            response = client.messages.create(
                body=message,
                from_=sender,
                to=phone_number,
            )

            print("Twilio SID:", response.sid)

            logger.info(
                "SMS Sent Successfully %s",
                response.sid,
            )

            return True

        except Exception as e:
            print("=" * 60)
            print("TWILIO ERROR")
            print(type(e))
            print(e)
            print("=" * 60)

            logger.exception("SMS Failed: %s", e)

            return False