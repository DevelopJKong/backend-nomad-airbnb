from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from PIL import Image, UnidentifiedImageError

from categories.models import Category
from common import uploadthing
from medias.models import Photo
from users.models import User

from .models import Amenity, Room
from .schemas import AmenityIn, RoomIn, RoomUpdateIn


def get_rooms_list(*, page: int = 1, page_size: int = 10):
    # depth=1 중첩 직렬화의 N+1 방지: FK는 select_related, M2M는 prefetch_related
    # 정렬 없이 페이지를 자르면 DB가 매번 다른 순서를 줄 수 있어(같은 row가 1p/2p에 중복 노출) 최신순으로 고정.
    # created_at 동률에 대비해 pk를 tie-breaker로 둔다.
    rooms = Room.objects.select_related('owner', 'category').prefetch_related('amenities').order_by('-created_at', '-pk')

    # QuerySet은 지연 평가라 아직 DB에 안 간 상태 — 슬라이싱이 SQL의 LIMIT/OFFSET으로 컴파일되어
    # 전체를 읽은 뒤 자르는 게 아니라 애초에 한 페이지만 조회한다.
    offset = (page - 1) * page_size
    return {
        'items': rooms[offset : offset + page_size],
        'count': rooms.count(),  # 페이지가 아닌 전체 개수 (COUNT 쿼리 1회 추가)
        'page': page,
        'page_size': page_size,
    }


def get_room(room_id: int) -> Room:
    return get_object_or_404(
        Room.objects.select_related('owner', 'category').prefetch_related('amenities'),
        pk=room_id,
    )


def get_room_reviews(room_id: int, page: int = 1, page_size: int = 10):
    reviews = Room.objects.get(pk=room_id).reviews.all()
    offset = (page - 1) * page_size
    return {
        'items': reviews[offset : offset + page_size],
        'count': reviews.count(),
        'page': page,
        'page_size': page_size,
    }


def create_room_photo(room_id: int, *, file: UploadedFile, caption: str) -> Photo:
    """업로드된 이미지를 UploadThing에 올리고 숙소에 연결한다."""
    # 응답 스키마(RoomPhotoOut.room)가 room을 depth=1로 직렬화하므로,
    # 직렬화 중 추가 쿼리가 나가지 않도록 관계를 미리 로드해둔다.
    room: Room = get_object_or_404(
        Room.objects.select_related('owner', 'category').prefetch_related('amenities'),
        pk=room_id,
    )

    # UploadThing에 보낼 때 어차피 전체 바이트가 필요하므로 한 번에 읽는다.
    # 상한(기본 5MB)이 있어 메모리에 올려도 안전한 크기다.
    content = file.read()
    max_size: int = settings.UPLOADTHING_MAX_FILE_SIZE
    if len(content) > max_size:
        raise ValidationError(f'파일이 너무 큽니다. 최대 {max_size // (1024 * 1024)}MB까지 업로드할 수 있습니다.')

    # Photo.objects.create()는 full_clean()을 부르지 않아 필드 검증이 자동으로 걸리지 않는다.
    # 확장자와 Content-Type은 클라이언트가 위조할 수 있으므로 실제로 디코딩되는 이미지인지 확인한다.
    try:
        Image.open(BytesIO(content)).verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError('이미지 파일이 아닙니다.') from exc

    uploaded = uploadthing.upload(
        content=content,
        name=file.name or 'upload',
        content_type=file.content_type or 'application/octet-stream',
    )

    return Photo.objects.create(url=uploaded.url, key=uploaded.key, caption=caption, room=room)


def create_room(payload: RoomIn) -> Room:
    # pyright는 런타임 attname(owner_id 등)을 모르므로 인스턴스를 조회해 FK에 직접 대입 (없으면 404)
    owner: User = get_object_or_404(User, pk=payload.owner)
    category: Category | None = None
    if payload.category is not None:
        # experiences 카테고리는 숙소에 붙일 수 없다 → kind 조건까지 걸어 404
        category = get_object_or_404(Category, pk=payload.category, kind=Category.CategoryKindChoices.ROOMS)

    # room 생성과 amenities 연결을 하나의 트랜잭션으로 묶어, 중간에 실패해도 room만 남지 않게 함
    with transaction.atomic():
        room = Room.objects.create(
            name=payload.name,
            country=payload.country,
            city=payload.city,
            price=payload.price,
            rooms=payload.rooms,
            toilets=payload.toilets,
            description=payload.description,
            address=payload.address,
            pet_friendly=payload.pet_friendly,
            kind=payload.kind,
            owner=owner,
            category=category,
        )
        # 존재하지 않는 id를 set()에 넘기면 IntegrityError — 실제 존재하는 것만 연결
        room.amenities.set(Amenity.objects.filter(pk__in=payload.amenities))

    return room


def update_room(room_id: int, payload: RoomUpdateIn) -> Room:
    room: Room = get_object_or_404(Room, pk=room_id)

    # owner는 선택 — 보냈을 때만 검증 후 변경, 생략(None)하면 기존 owner 유지
    owner: User | None = None
    if payload.owner is not None:
        owner = get_object_or_404(User, pk=payload.owner)

    category: Category | None = None
    if payload.category is not None:
        category = get_object_or_404(Category, pk=payload.category, kind=Category.CategoryKindChoices.ROOMS)

    if owner is not None:
        room.owner = owner

    room.name = payload.name
    room.country = payload.country
    room.city = payload.city
    room.price = payload.price
    room.rooms = payload.rooms
    room.toilets = payload.toilets
    room.description = payload.description
    room.address = payload.address
    room.pet_friendly = payload.pet_friendly
    room.kind = payload.kind
    room.category = category

    # room 저장과 amenities 재설정을 하나의 트랜잭션으로 묶어, 중간에 실패해도 절반만 반영되지 않게 함
    with transaction.atomic():
        room.save()
        room.amenities.set(Amenity.objects.filter(pk__in=payload.amenities))

    return room


def delete_room(room_id: int) -> None:
    room: Room = get_object_or_404(Room, pk=room_id)
    room.delete()


def list_amenities():
    return Amenity.objects.all()


def create_amenity(payload: AmenityIn) -> Amenity:
    return Amenity.objects.create(**payload.dict())


def get_amenity(amenity_id: int) -> Amenity:
    return get_object_or_404(Amenity, pk=amenity_id)


def update_amenity(amenity_id: int, payload: AmenityIn) -> Amenity:
    amenity: Amenity = get_object_or_404(Amenity, pk=amenity_id)

    # setattr 사용
    # for attr, value in payload.dict().items():
    # setattr(amenity, attr, value)

    amenity.name = payload.name
    amenity.description = payload.description
    amenity.save()
    return amenity


def delete_amenity(amenity_id: int) -> None:
    amenity: Amenity = get_object_or_404(Amenity, pk=amenity_id)
    amenity.delete()
