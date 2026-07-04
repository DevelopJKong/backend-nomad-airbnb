from typing import Any

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
        owner=0,
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
        self.owner = User.objects.create_user(username='host')
        self.amenity = Amenity.objects.create(name='wifi')
        self.category = Category.objects.create(name='한옥', kind=Category.CategoryKindChoices.ROOMS)

    def test_create_room(self):
        room = services.create_room(room_payload(owner=self.owner.pk, amenities=[self.amenity.pk], category=self.category.pk))
        self.assertIsNotNone(room.pk)
        self.assertEqual(room.owner, self.owner)
        self.assertEqual(room.category, self.category)
        self.assertEqual(list(room.amenities.all()), [self.amenity])

    def test_create_room_rejects_experiences_category(self):
        exp = Category.objects.create(name='체험', kind=Category.CategoryKindChoices.EXPERIENCES)
        with self.assertRaises(Http404):
            services.create_room(room_payload(owner=self.owner.pk, category=exp.pk))

    def test_create_room_rejects_unknown_owner(self):
        with self.assertRaises(Http404):
            services.create_room(room_payload(owner=99999))

    def test_update_room_replaces_fields_and_amenities(self):
        room = services.create_room(room_payload(owner=self.owner.pk, amenities=[self.amenity.pk]))
        parking = Amenity.objects.create(name='주차')
        updated = services.update_room(
            room.pk,
            room_update_payload(name='수정된 숙소', amenities=[parking.pk], category=self.category.pk),
        )
        self.assertEqual(updated.name, '수정된 숙소')
        self.assertEqual(updated.category, self.category)
        self.assertEqual(list(updated.amenities.all()), [parking])

    def test_update_room_without_owner_keeps_existing_owner(self):
        room = services.create_room(room_payload(owner=self.owner.pk))
        updated = services.update_room(room.pk, room_update_payload())
        self.assertEqual(updated.owner, self.owner)

    def test_update_room_with_owner_changes_owner(self):
        room = services.create_room(room_payload(owner=self.owner.pk))
        new_owner = User.objects.create_user(username='new-host')
        updated = services.update_room(room.pk, room_update_payload(owner=new_owner.pk))
        self.assertEqual(updated.owner, new_owner)

    def test_delete_room(self):
        room = services.create_room(room_payload(owner=self.owner.pk))
        services.delete_room(room.pk)
        self.assertFalse(Room.objects.filter(pk=room.pk).exists())

    def test_delete_missing_room_raises_404(self):
        with self.assertRaises(Http404):
            services.delete_room(99999)
