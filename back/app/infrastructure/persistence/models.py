from datetime import datetime

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    BigInteger,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.infrastructure.persistence.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    role = Column(Enum("user", "admin"), nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=True)
    point = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    addresses = relationship("UserAddressModel", back_populates="user", lazy="select")


class UserAddressModel(Base):
    __tablename__ = "user_addresses"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    receiver = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    zipcode = Column(String(10), nullable=False)
    address1 = Column(String(255), nullable=False)
    address2 = Column(String(255))
    is_default = Column(Boolean, nullable=False, default=False)

    user = relationship("UserModel", back_populates="addresses")


class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String(100), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Integer, nullable=False)
    sale_price = Column(Integer)
    stock = Column(Integer, nullable=False, default=0)
    thumbnail_url = Column(String(500))
    is_active = Column(Boolean, nullable=False, default=True)
    is_time_sale = Column(Boolean, nullable=False, default=False)
    time_sale_start = Column(TIMESTAMP)
    time_sale_end = Column(TIMESTAMP)
    time_sale_price = Column(Integer)
    time_sale_stock = Column(Integer)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    images = relationship("ProductImageModel", back_populates="product", lazy="select", cascade="all, delete-orphan")


class ProductImageModel(Base):
    __tablename__ = "product_images"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(500), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    product = relationship("ProductModel", back_populates="images")


class BannerModel(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    image_url = Column(String(500), nullable=False)
    link_url = Column(String(500))
    sort_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    started_at = Column(TIMESTAMP)
    ended_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class CouponModel(Base):
    __tablename__ = "coupons"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum("fixed", "percent"), nullable=False)
    discount_value = Column(Integer, nullable=False)
    min_order_amount = Column(Integer, nullable=False, default=0)
    max_discount = Column(Integer)
    total_stock = Column(Integer, nullable=False)
    issued_count = Column(Integer, nullable=False, default=0)
    started_at = Column(TIMESTAMP, nullable=False)
    expired_at = Column(TIMESTAMP, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class UserCouponModel(Base):
    __tablename__ = "user_coupons"
    __table_args__ = (UniqueConstraint("user_id", "coupon_id", name="uq_user_coupon"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    coupon_id = Column(BigInteger, ForeignKey("coupons.id"), nullable=False)
    is_used = Column(Boolean, nullable=False, default=False)
    used_at = Column(TIMESTAMP)
    order_id = Column(BigInteger)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    coupon = relationship("CouponModel", lazy="joined")


class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_no = Column(String(50), nullable=False, unique=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    status = Column(
        Enum(
            "pending", "paid", "preparing", "shipping", "delivered",
            "confirmed", "cancelled", "exchange_requested", "return_requested",
        ),
        nullable=False,
        default="pending",
    )
    total_amount = Column(Integer, nullable=False)
    discount_amount = Column(Integer, nullable=False, default=0)
    shipping_fee = Column(Integer, nullable=False, default=0)
    final_amount = Column(Integer, nullable=False)
    coupon_id = Column(BigInteger)
    point_used = Column(Integer, nullable=False, default=0)
    receiver_name = Column(String(100), nullable=False)
    receiver_phone = Column(String(20), nullable=False)
    zipcode = Column(String(10), nullable=False)
    address1 = Column(String(255), nullable=False)
    address2 = Column(String(255))
    memo = Column(String(500))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    items = relationship("OrderItemModel", back_populates="order", lazy="select", cascade="all, delete-orphan")


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Integer, nullable=False)

    order = relationship("OrderModel", back_populates="items")


class PaymentModel(Base):
    __tablename__ = "payments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False, unique=True)
    order_no = Column(String(50), nullable=False)
    payment_key = Column(String(200))
    method = Column(String(50))
    status = Column(Enum("ready", "done", "cancelled", "failed"), nullable=False, default="ready")
    amount = Column(Integer, nullable=False)
    approved_at = Column(TIMESTAMP)
    cancelled_at = Column(TIMESTAMP)
    cancel_reason = Column(String(500))
    raw_response = Column(JSON)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class ReviewModel(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("order_id", "product_id", name="uq_order_product_review"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False)
    rating = Column(SmallInteger, nullable=False)
    content = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class FaqModel(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class NoticeModel(Base):
    __tablename__ = "notices"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_pinned = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class InquiryModel(Base):
    __tablename__ = "inquiries"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    order_id = Column(BigInteger)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum("pending", "answered"), nullable=False, default="pending")
    answer = Column(Text)
    answered_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(BigInteger)
    before_data = Column(JSON)
    after_data = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
