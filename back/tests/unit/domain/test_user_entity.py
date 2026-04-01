import pytest
from datetime import datetime

from app.domain.user.entities import User, UserRole
from app.domain.user.exceptions import InsufficientPointException


def _make_user(point: int = 1000) -> User:
    return User(
        id=1, email="test@example.com", password="hashed", name="테스트",
        phone=None, role=UserRole.USER, is_active=True, point=point, created_at=datetime.utcnow(),
    )


def test_deduct_point_success():
    user = _make_user(1000)
    user.deduct_point(500)
    assert user.point == 500


def test_deduct_point_all():
    user = _make_user(1000)
    user.deduct_point(1000)
    assert user.point == 0


def test_deduct_point_insufficient():
    user = _make_user(500)
    with pytest.raises(InsufficientPointException):
        user.deduct_point(501)


def test_earn_point():
    user = _make_user(100)
    user.earn_point(200)
    assert user.point == 300


def test_is_admin():
    admin = User(
        id=1, email="admin@example.com", password="hashed", name="관리자",
        phone=None, role=UserRole.ADMIN, is_active=True, point=0, created_at=datetime.utcnow(),
    )
    assert admin.is_admin() is True
    user = _make_user()
    assert user.is_admin() is False
