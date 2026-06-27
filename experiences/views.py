from ninja import Router

from . import services
from .schemas import PerkIn, PerkOut

router = Router()  # experiences 최상위 라우터
perk_router = Router()  # perks 하위 라우터


@perk_router.get('/', response=list[PerkOut], summary='퍼크 목록 조회')
def get_perks_list(
    request,  # pyright: ignore[reportUnusedParameter]
):
    """등록된 모든 퍼크(perk)를 반환합니다."""
    return services.list_perks()


@perk_router.post('/', response={201: PerkOut}, summary='퍼크 생성')
def create_perk(
    request,  # pyright: ignore[reportUnusedParameter]
    payload: PerkIn,
):
    """새 퍼크를 생성합니다."""
    return 201, services.create_perk(payload)


@perk_router.get('/{perk_id}', response=PerkOut, summary='특정 퍼크 조회')
def get_perk(
    request,  # pyright: ignore[reportUnusedParameter]
    perk_id: int,
):
    """`perk_id`에 해당하는 퍼크를 반환합니다. 없으면 404."""
    return services.get_perk(perk_id)


@perk_router.put('/{perk_id}', response=PerkOut, summary='퍼크 수정')
def update_perk(
    request,  # pyright: ignore[reportUnusedParameter]
    perk_id: int,
    payload: PerkIn,
):
    """전달된 필드로 퍼크를 수정합니다."""
    return services.update_perk(perk_id, payload)


@perk_router.delete('/{perk_id}', response={204: None}, summary='퍼크 삭제')
def delete_perk(
    request,  # pyright: ignore[reportUnusedParameter]
    perk_id: int,
):
    """`perk_id`에 해당하는 퍼크를 삭제합니다."""
    services.delete_perk(perk_id)
    return 204, None


# experiences 라우터 아래에 perks 라우터를 중첩 → /experiences/perks/...
router.add_router('/perks/', perk_router, tags=['Perks'])
