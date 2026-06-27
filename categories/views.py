from ninja import Router

from . import services
from .schemas import CategoryIn, CategoryOut, CategoryPatch

router = Router()


@router.get('/', response=list[CategoryOut], summary='카테고리 목록 조회')
def list_categories(request):
    """등록된 모든 카테고리를 반환합니다."""
    return services.list_categories()


@router.post('/', response={201: CategoryOut}, summary='카테고리 생성')
def create_category(request, payload: CategoryIn):
    """새 카테고리를 생성합니다."""
    return 201, services.create_category(payload)


@router.get('/{pk}', response=CategoryOut, summary='카테고리 단건 조회')
def get_category(request, pk: int):
    """`pk`에 해당하는 카테고리를 반환합니다. 없으면 404."""
    return services.get_category(pk)


@router.put('/{pk}', response=CategoryOut, summary='카테고리 수정')
def update_category(request, pk: int, payload: CategoryPatch):
    """전달된 필드만 부분 수정합니다."""
    return services.update_category(pk, payload)


@router.delete('/{pk}', response={204: None}, summary='카테고리 삭제')
def delete_category(request, pk: int):
    """`pk`에 해당하는 카테고리를 삭제합니다."""
    services.delete_category(pk)
    return 204, None
