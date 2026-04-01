import base64

import httpx

from app.core.config import settings
from app.core.exceptions import PaymentFailedError

TOSS_API_BASE = "https://api.tosspayments.com/v1/payments"


class TossPaymentAdapter:
    """토스페이먼츠 API Adapter."""

    def _auth_header(self) -> dict:
        encoded = base64.b64encode(f"{settings.TOSS_SECRET_KEY}:".encode()).decode()
        return {"Authorization": f"Basic {encoded}", "Content-Type": "application/json"}

    async def confirm(self, payment_key: str, order_no: str, amount: int) -> dict:
        """결제 승인 API 호출."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{TOSS_API_BASE}/{payment_key}",
                headers=self._auth_header(),
                json={"paymentKey": payment_key, "orderId": order_no, "amount": amount},
                timeout=10.0,
            )
        if resp.status_code != 200:
            data = resp.json()
            raise PaymentFailedError(data.get("message", "토스페이먼츠 결제 승인 실패"))
        return resp.json()

    async def cancel(self, payment_key: str, cancel_reason: str, cancel_amount: int | None = None) -> dict:
        """결제 취소 API 호출."""
        body: dict = {"cancelReason": cancel_reason}
        if cancel_amount is not None:
            body["cancelAmount"] = cancel_amount
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{TOSS_API_BASE}/{payment_key}/cancel",
                headers=self._auth_header(),
                json=body,
                timeout=10.0,
            )
        if resp.status_code != 200:
            data = resp.json()
            raise PaymentFailedError(data.get("message", "토스페이먼츠 결제 취소 실패"))
        return resp.json()
