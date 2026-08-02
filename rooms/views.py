from ninja import File, FormEx, P, QueryEx, Router, UploadedFile

from . import services
from .schemas import AmenityIn, AmenityOut, PagedRoomOut, ReviewOut, RoomIn, RoomOut, RoomPhotoOut, RoomUpdateIn

router = Router()  # rooms 최상위 라우터
amenity_router = Router()  # amenities 하위 라우터


@router.get('/', response=PagedRoomOut, summary='숙소 목록 조회')
def get_rooms_list(
    request,  # pyright: ignore[reportUnusedParameter]
    # 페이지 파라미터를 시그니처에 그대로 노출 — 검증(ge/le)까지 여기서 끝난다.
    # le=50 위반은 조용히 깎지 않고 422로 거절한다.
    page: QueryEx[int, P(ge=1, description='1부터 시작하는 페이지 번호')] = 1,
    page_size: QueryEx[int, P(ge=1, le=50, description='한 페이지 개수 (최대 50)')] = 10,
):
    """등록된 숙소를 페이지 단위로 반환합니다.

    `{"items": [...], "count": 전체 개수, "page": ..., "page_size": ...}` 형태로 응답합니다.
    """
    return services.get_rooms_list(page=page, page_size=page_size)


@router.get('/{room_id}/reviews', response=list[ReviewOut], summary='')
def get_room_reviews(
    request,  # pyright: ignore[reportUnusedParameter]
    room_id: int,
    page: QueryEx[int, P(ge=1, description='1부터 시작하는 페이지 번호')] = 1,
    page_size: QueryEx[int, P(ge=1, le=50, description='한 페이지 개수 (최대 50)')] = 10,
):
    """`room_id`에 해당하는 숙소 리뷰를 반환합니다."""
    return services.get_room_reviews(room_id, page=page, page_size=page_size)


@router.post('/', response={201: RoomOut}, summary='숙소 생성')
def create_room(
    request,  # pyright: ignore[reportUnusedParameter]
    payload: RoomIn,
):
    """새 숙소를 생성합니다. owner/category가 없거나 category가 rooms 종류가 아니면 404."""
    return 201, services.create_room(payload)


@router.post('/{room_id}/photos', response={201: RoomPhotoOut}, summary='숙소 사진 등록')
def create_room_photo(
    request,  # pyright: ignore[reportUnusedParameter]
    room_id: int,
    # multipart/form-data — 파일은 File, 나머지 필드는 Form으로 받는다
    file: File[UploadedFile],
    caption: FormEx[str, P(max_length=140)] = '',
):
    """이미지를 스토리지에 업로드하고 `room_id` 숙소에 연결합니다.

    숙소가 없으면 404, 이미지가 아니거나 용량을 초과하면 422,
    스토리지 호출이 실패하면 502를 반환합니다.
    """
    return 201, services.create_room_photo(room_id, file=file, caption=caption)


@router.delete('/{room_id}/photos/{photo_id}', response={204: None}, summary='숙소 사진 삭제')
def delete_room_photo(
    request,  # pyright: ignore[reportUnusedParameter]
    room_id: int,
    photo_id: int,
):
    """사진을 DB와 스토리지 양쪽에서 삭제합니다.

    해당 숙소의 사진이 아니면 404. 스토리지 파일 삭제가 실패해도
    사진은 이미 사라졌으므로 204를 반환하고 서버 로그에만 남깁니다.
    """
    services.delete_room_photo(room_id, photo_id)
    return 204, None


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
