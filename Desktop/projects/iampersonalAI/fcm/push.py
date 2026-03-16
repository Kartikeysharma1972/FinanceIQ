"""Firebase Cloud Messaging service for push notifications."""

import structlog
from typing import Optional, Dict

logger = structlog.get_logger(__name__)

# Firebase Admin SDK initialization happens once
_firebase_initialized = False


def _init_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return
    try:
        import firebase_admin
        from firebase_admin import credentials

        # Use service account key file
        cred = credentials.Certificate("firebase-service-account.json")
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        logger.info("firebase_initialized")
    except Exception as e:
        logger.warning("firebase_init_skipped", error=str(e))


class FCMService:
    """Handles sending push notifications via Firebase Cloud Messaging."""

    def __init__(self):
        _init_firebase()

    async def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        priority: str = "normal",
    ) -> bool:
        """Send a notification message to a device."""
        try:
            from firebase_admin import messaging

            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=token,
                android=messaging.AndroidConfig(
                    priority="high" if priority in ("high", "urgent") else "normal",
                    notification=messaging.AndroidNotification(
                        channel_id="claw_assistant_channel",
                        icon="ic_notification",
                        sound="default" if priority != "urgent" else "alarm",
                    ),
                ),
            )

            response = messaging.send(message)
            logger.info("fcm_sent", response=response, title=title)
            return True
        except Exception as e:
            logger.error("fcm_send_failed", error=str(e))
            return False

    async def send_data_message(
        self,
        token: str,
        data: Dict[str, str],
    ) -> bool:
        """Send a data-only message (for alarms, silent updates)."""
        try:
            from firebase_admin import messaging

            message = messaging.Message(
                data={k: str(v) for k, v in data.items()},
                token=token,
                android=messaging.AndroidConfig(priority="high"),
            )

            response = messaging.send(message)
            logger.info("fcm_data_sent", response=response, type=data.get("type"))
            return True
        except Exception as e:
            logger.error("fcm_data_failed", error=str(e))
            return False
