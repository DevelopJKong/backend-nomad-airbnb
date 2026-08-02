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
    # owner는 payload로 받지 않는다 — 로그인한 유저가 곧 소유자다
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
    # 소유권 이전은 지원하지 않는다 — owner는 생성 시점에 고정된다
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


class RoomPhotoOut(Schema):
    """숙소 사진. 파일 실체는 UploadThing에 있으므로 url만 노출하고,
    삭제용 key는 내부 식별자라 응답에 담지 않는다."""

    id: int
    url: str
    caption: str
    # depth=1: 사진이 어느 숙소 것인지 중첩 객체로 함께 내려준다
    room: RoomOut
    created_at: datetime
    updated_at: datetime


class ReviewOut(Schema):
    id: int
    created_at: datetime
    updated_at: datetime
    payload: str
    rating: int
    user: OwnerOut
    room: RoomOut
    experience: str | None = None
