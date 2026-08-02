from typing import Any

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import TestCase

from categories.models import Category
from users.models import User

from . import services
from .models import Amenity, Room
from .schemas import RoomIn, RoomKindChoices, RoomUpdateIn


def room_payload(**overrides: Any) -> RoomIn:
    # 값 타입이 섞여 있어 그대로 두면 pyright가 각 kwarg를 union으로 추론 → Any로 명시
    base: dict[str, Any] = dict(
        name='테스트 숙소',
        country='한국',
        city='서울',
        price=100000,
        rooms=2,
        toilets=1,
        description='설명',
        address='서울시 어딘가',
        pet_friendly=True,
        kind=RoomKindChoices.ENTIRE_PLACE,
        amenities=[],
        category=None,
    )
    base.update(overrides)
    return RoomIn(**base)


def room_update_payload(**overrides: Any) -> RoomUpdateIn:
    base: dict[str, Any] = dict(
        name='테스트 숙소',
        country='한국',
        city='서울',
        price=100000,
        rooms=2,
        toilets=1,
        description='설명',
        address='서울시 어딘가',
        pet_friendly=True,
        kind=RoomKindChoices.ENTIRE_PLACE,
        amenities=[],
        category=None,
    )
    base.update(overrides)
    return RoomUpdateIn(**base)


class RoomServiceTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='host', is_host=True)
        self.amenity = Amenity.objects.create(name='wifi')
        self.category = Category.objects.create(name='한옥', kind=Category.CategoryKindChoices.ROOMS)

    def test_create_room(self):
        room = services.create_room(
            room_payload(amenities=[self.amenity.pk], category=self.category.pk),
            user=self.owner,
        )
        self.assertIsNotNone(room.pk)
        self.assertEqual(room.category, self.category)
        self.assertEqual(list(room.amenities.all()), [self.amenity])

    def test_create_room_sets_owner_to_logged_in_user(self):
        # owner는 payload가 아니라 로그인 유저로 결정된다
        room = services.create_room(room_payload(), user=self.owner)
        self.assertEqual(room.owner, self.owner)

    def test_create_room_rejects_experiences_category(self):
        exp = Category.objects.create(name='체험', kind=Category.CategoryKindChoices.EXPERIENCES)
        with self.assertRaises(Http404):
            services.create_room(room_payload(category=exp.pk), user=self.owner)

    def test_update_room_replaces_fields_and_amenities(self):
        room = services.create_room(room_payload(amenities=[self.amenity.pk]), user=self.owner)
        parking = Amenity.objects.create(name='주차')
        updated = services.update_room(
            room.pk,
            room_update_payload(name='수정된 숙소', amenities=[parking.pk], category=self.category.pk),
            user=self.owner,
        )
        self.assertEqual(updated.name, '수정된 숙소')
        self.assertEqual(updated.category, self.category)
        self.assertEqual(list(updated.amenities.all()), [parking])

    def test_update_room_keeps_owner(self):
        # 소유권 이전은 지원하지 않는다
        room = services.create_room(room_payload(), user=self.owner)
        updated = services.update_room(room.pk, room_update_payload(), user=self.owner)
        self.assertEqual(updated.owner, self.owner)

    def test_delete_room(self):
        room = services.create_room(room_payload(), user=self.owner)
        services.delete_room(room.pk, user=self.owner)
        self.assertFalse(Room.objects.filter(pk=room.pk).exists())

    def test_delete_missing_room_raises_404(self):
        with self.assertRaises(Http404):
            services.delete_room(99999, user=self.owner)


class RoomPermissionTest(TestCase):
    """객체 수준 권한(IsOwner)이 services에서 걸리는지 확인한다."""

    def setUp(self):
        self.owner = User.objects.create_user(username='host', is_host=True)
        self.stranger = User.objects.create_user(username='stranger', is_host=True)
        self.room = services.create_room(room_payload(), user=self.owner)

    def test_stranger_cannot_update_room(self):
        with self.assertRaises(PermissionDenied):
            services.update_room(self.room.pk, room_update_payload(name='탈취'), user=self.stranger)
        self.room.refresh_from_db()
        self.assertEqual(self.room.name, '테스트 숙소')

    def test_stranger_cannot_delete_room(self):
        with self.assertRaises(PermissionDenied):
            services.delete_room(self.room.pk, user=self.stranger)
        self.assertTrue(Room.objects.filter(pk=self.room.pk).exists())

    def test_owner_can_update_room(self):
        updated = services.update_room(self.room.pk, room_update_payload(name='수정됨'), user=self.owner)
        self.assertEqual(updated.name, '수정됨')

    def test_missing_room_raises_404_before_permission_check(self):
        # 없는 숙소는 권한과 무관하게 404 (403으로 존재 여부를 흘리지 않는다)
        with self.assertRaises(Http404):
            services.update_room(99999, room_update_payload(), user=self.stranger)
