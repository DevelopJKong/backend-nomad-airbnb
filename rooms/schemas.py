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


class RoomUpdateIn(Schema):
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
    # PUT에서 owner는 선택 — 보내면 변경, 생략하면 기존 owner 유지
    owner: int | None = None
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


class PagedRoomOut(Schema):
    """숙소 목록의 페이지 응답. 클라이언트가 다음 페이지 존재 여부를 계산할 수 있도록
    요청 조건(page/page_size)을 그대로 되돌려준다."""

    items: list[RoomOut]
    count: int  # 페이지가 아니라 전체 숙소 개수
    page: int
    page_size: int


class ReviewOut(Schema):
    id: int
    created_at: datetime
    updated_at: datetime
    payload: str
    rating: int
    user: OwnerOut
    room: RoomOut
    experience: str | None = None
