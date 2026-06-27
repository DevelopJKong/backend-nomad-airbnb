from datetime import datetime
from enum import Enum

from ninja import Schema

from categories.schemas import CategoryOut


class OwnerOut(Schema):
    id: int
    username: str
    name: str
    is_host: bool


class RoomKindChoices(str, Enum):
    ENTIRE_PLACE = 'entire_place'
    PRIVATE_ROOM = 'private_room'
    SHARED_ROOM = 'shared_room'


class AmenityIn(Schema):
    name: str
    description: str | None = None


class AmenityOut(Schema):
    id: int
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class RoomIn(Schema):
    name: str
    country: str
    city: str
    price: int
    rooms: int
    toilets: int
    description: str
    address: str
    pet_friendly: bool
    kind: RoomKindChoices
    owner: int
    amenities: list[int]
    category: int | None = None


class RoomOut(Schema):
    id: int
    name: str
    country: str
    city: str
    price: int
    rooms: int
    toilets: int
    description: str
    address: str
    pet_friendly: bool
    kind: RoomKindChoices
    # depth=1: 관계를 ID가 아니라 한 단계 중첩된 객체로 직렬화
    owner: OwnerOut
    amenities: list[AmenityOut]
    category: CategoryOut | None = None
    created_at: datetime
    updated_at: datetime
