from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from app.core.exceptions import CouponNotFoundError, ProductNotFoundError, UserNotFoundError, ValidationError
from app.domain.cart.repository import CartRepository
from app.domain.coupon.repository import UserCouponRepository
from app.domain.order.entities import Order, OrderItem, OrderStatus
from app.domain.order.repository import OrderRepository
from app.domain.payment.entities import Payment, PaymentStatus
from app.domain.payment.repository import PaymentRepository
from app.domain.product.repository import ProductRepository
from app.domain.user.repository import UserAddressRepository, UserRepository


@dataclass
class PreparePaymentCommand:
    user_id: int
    address_id: int
    coupon_id: int | None
    point_use: int
    memo: str | None


@dataclass
class PreparePaymentResult:
    order_no: str
    amount: int
    order_name: str


SHIPPING_FEE = 3000
FREE_SHIPPING_THRESHOLD = 30000


class PreparePaymentUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        address_repo: UserAddressRepository,
        product_repo: ProductRepository,
        cart_repo: CartRepository,
        order_repo: OrderRepository,
        payment_repo: PaymentRepository,
        user_coupon_repo: UserCouponRepository,
    ):
        self._user_repo = user_repo
        self._address_repo = address_repo
        self._product_repo = product_repo
        self._cart_repo = cart_repo
        self._order_repo = order_repo
        self._payment_repo = payment_repo
        self._user_coupon_repo = user_coupon_repo

    async def execute(self, cmd: PreparePaymentCommand) -> PreparePaymentResult:
        user = await self._user_repo.get_by_id(cmd.user_id)
        if not user:
            raise UserNotFoundError()

        address = await self._address_repo.get_by_id(cmd.address_id)
        if not address or address.user_id != cmd.user_id:
            raise UserNotFoundError()

        cart = await self._cart_repo.get(cmd.user_id)
        if not cart.items:
            raise ValidationError("장바구니가 비어있습니다.")

        # 배치 조회 대신 개별 조회 (N+1 — 추후 get_by_ids로 개선 가능)
        items = []
        total_amount = 0
        for ci in cart.items:
            product = await self._product_repo.get_by_id(ci.product_id)
            if not product or not product.is_active:
                raise ProductNotFoundError()
            price = product.effective_price()
            subtotal = price * ci.quantity
            total_amount += subtotal
            items.append(OrderItem(
                id=None, order_id=None, product_id=product.id,
                product_name=product.name, price=price, quantity=ci.quantity, subtotal=subtotal,
            ))

        # 쿠폰 할인 — 검증 시점에 미사용 확인
        discount_amount = 0
        user_coupon = None
        if cmd.coupon_id:
            user_coupon = await self._user_coupon_repo.get(cmd.user_id, cmd.coupon_id)
            if not user_coupon or user_coupon.is_used or not user_coupon.coupon:
                raise CouponNotFoundError()
            if not user_coupon.coupon.is_valid():
                from app.core.exceptions import CouponExpiredError
                raise CouponExpiredError()
            discount_amount = user_coupon.coupon.calculate_discount(total_amount)

        # 포인트 차감 (도메인 검증 후 DB 반영)
        if cmd.point_use > 0:
            user.deduct_point(cmd.point_use)
            discount_amount += cmd.point_use

        # 배송비
        shipping_fee = 0 if total_amount >= FREE_SHIPPING_THRESHOLD else SHIPPING_FEE
        final_amount = max(0, total_amount - discount_amount + shipping_fee)

        # order_no: 날짜 + UUID4 전체 (8자리 잘라내지 않음)
        order_no = f"{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:12].upper()}"
        now = datetime.now(timezone.utc)

        order = Order(
            id=None, order_no=order_no, user_id=cmd.user_id,
            status=OrderStatus.PENDING, items=items,
            total_amount=total_amount, discount_amount=discount_amount,
            shipping_fee=shipping_fee, final_amount=final_amount,
            coupon_id=cmd.coupon_id, point_used=cmd.point_use,
            receiver_name=address.receiver, receiver_phone=address.phone,
            zipcode=address.zipcode, address1=address.address1, address2=address.address2,
            memo=cmd.memo, created_at=now,
        )
        saved_order = await self._order_repo.save(order)

        # 쿠폰 사용 처리 — 주문 생성 후 즉시 마킹 (동일 쿠폰 중복 사용 방지)
        if user_coupon and cmd.coupon_id:
            await self._user_coupon_repo.mark_used(user_coupon.id, saved_order.id)

        # 포인트 차감 DB 반영
        if cmd.point_use > 0:
            await self._user_repo.update(user)

        payment = Payment(
            id=None, order_id=saved_order.id, order_no=order_no,
            payment_key=None, method=None, status=PaymentStatus.READY,
            amount=final_amount, approved_at=None, cancelled_at=None,
            cancel_reason=None, raw_response=None, created_at=now,
        )
        await self._payment_repo.save(payment)

        order_name = items[0].product_name
        if len(items) > 1:
            order_name += f" 외 {len(items) - 1}건"

        return PreparePaymentResult(order_no=order_no, amount=final_amount, order_name=order_name)
