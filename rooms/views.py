from ninja import Router

from . import services
from .schemas import AmenityIn, AmenityOut

router = Router()


@router.get('/', response=list[AmenityOut], summary='시설 목록 조회')
def get_amenities_list(request):
    """등록된 모든 시설(amenity)을 반환합니다."""
    return services.list_amenities()


@router.post('/', response={201: AmenityOut}, summary='시설 생성')
def create_amenity(request, payload: AmenityIn):
    """새 시설을 생성합니다."""
    return 201, services.create_amenity(payload)


@router.get('/{amenity_id}', response=AmenityOut, summary='특정 시설 조회')
def get_amenity(request, amenity_id: int):
    """`amenity_id`에 해당하는 시설을 반환합니다. 없으면 404."""
    return services.get_amenity(amenity_id)


@router.put('/{amenity_id}', response=AmenityOut, summary='시설 수정')
def update_amenity(request, amenity_id: int, payload: AmenityIn):
    """전달된 필드로 시설을 수정합니다."""
    return services.update_amenity(amenity_id, payload)


@router.delete('/{amenity_id}', response={204: None}, summary='시설 삭제')
def delete_amenity(request, amenity_id: int):
    """`amenity_id`에 해당하는 시설을 삭제합니다."""
    services.delete_amenity(amenity_id)
    return 204, None
