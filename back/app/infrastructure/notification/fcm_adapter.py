import logging

logger = logging.getLogger(__name__)


class FCMAdapter:
    """Firebase Cloud Messaging Adapter. 프로덕션에서 firebase-admin 사용."""

    def __init__(self):
        self._app = None
        try:
            import firebase_admin
            from firebase_admin import credentials, messaging
            from app.core.config import settings
            cred = credentials.Certificate(settings.FCM_CREDENTIALS_PATH)
            self._app = firebase_admin.initialize_app(cred)
            self._messaging = messaging
        except Exception:
            logger.warning("FCM not configured — notifications disabled.")

    async def send(self, token: str, title: str, body: str, data: dict | None = None) -> None:
        if self._app is None:
            logger.debug("FCM disabled, skip send: %s", title)
            return
        from firebase_admin import messaging
        message = messaging.Message(
            token=token,
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
        )
        try:
            messaging.send(message)
        except Exception as e:
            logger.error("FCM send error: %s", e)
