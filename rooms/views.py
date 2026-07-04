from ninja import Router

from . import services
from .schemas import AmenityIn, AmenityOut, RoomIn, RoomOut, RoomUpdateIn

router = Router()  # rooms 최상위 라우터
amenity_router = Router()  # amenities 하위 라우터


@router.get('/', response=list[RoomOut], summary='숙소 목록 조회')
def get_rooms_list(
    request,  # pyright: ignore[reportUnusedParameter]
):
    """등록된 모든 숙소를 반환합니다."""
    return services.list_rooms()


@router.post('/', response={201: RoomOut}, summary='숙소 생성')
def create_room(
    request,  # pyright: ignore[reportUnusedParameter]
    payload: RoomIn,
):
    """새 숙소를 생성합니다. owner/category가 없거나 category가 rooms 종류가 아니면 404."""
    return 201, services.create_room(payload)


@router.get('/{room_id}', response=RoomOut, summary='숙소 상세 조회')
def get_room(
    request,  # pyright: ignore[reportUnusedParameter]
    room_id: int,
):
    """`room_id`에 해당하는 숙소를 반환합니다. 없으면 404."""
    return services.get_room(room_id)


@router.put('/{room_id}', response=RoomOut, summary='숙소 수정')
def update_room(
    request,  # pyright: ignore[reportUnusedParameter]
    room_id: int,
    payload: RoomUpdateIn,
):
    """전달된 필드로 숙소 전체를 교체합니다(PUT). owner는 생략 시 기존 값 유지. 없으면 404."""
    return services.update_room(room_id, payload)


@router.delete('/{room_id}', response={204: None}, summary='숙소 삭제')
def delete_room(
    request,  # pyright: ignore[reportUnusedParameter]
    room_id: int,
):
    """`room_id`에 해당하는 숙소를 삭제합니다."""
    services.delete_room(room_id)
    return 204, None


@amenity_router.get('/', response=list[AmenityOut], summary='시설 목록 조회')
def get_amenities_list(
    request,  # pyright: ignore[reportUnusedParameter]
):
    """등록된 모든 시설(amenity)을 반환합니다."""
    return services.list_amenities()


@amenity_router.post('/', response={201: AmenityOut}, summary='시설 생성')
def create_amenity(
    request,  # pyright: ignore[reportUnusedParameter]
    payload: AmenityIn,
):
    """새 시설을 생성합니다."""
    return 201, services.create_amenity(payload)


@amenity_router.get('/{amenity_id}', response=AmenityOut, summary='특정 시설 조회')
def get_amenity(
    request,  # pyright: ignore[reportUnusedParameter]
    amenity_id: int,
):
    """`amenity_id`에 해당하는 시설을 반환합니다. 없으면 404."""
    return services.get_amenity(amenity_id)


@amenity_router.put('/{amenity_id}', response=AmenityOut, summary='시설 수정')
def update_amenity(
    request,  # pyright: ignore[reportUnusedParameter]
    amenity_id: int,
    payload: AmenityIn,
):
    """전달된 필드로 시설을 수정합니다."""
    return services.update_amenity(amenity_id, payload)


@amenity_router.delete('/{amenity_id}', response={204: None}, summary='시설 삭제')
def delete_amenity(
    request,  # pyright: ignore[reportUnusedParameter]
    amenity_id: int,
):
    """`amenity_id`에 해당하는 시설을 삭제합니다."""
    services.delete_amenity(amenity_id)
    return 204, None


# rooms 라우터 아래에 amenities 라우터를 중첩 → /rooms/amenities/...
router.add_router('/amenities/', amenity_router, tags=['Amenities'])
