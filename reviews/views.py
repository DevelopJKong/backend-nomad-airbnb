from ninja import Router

from . import services
from .schemas import ReviewIn, ReviewOut, ReviewUpdateIn

router = Router()  # reviews 최상위 라우터


@router.get('/', response=list[ReviewOut], summary='리뷰 목록 조회')
def get_reviews_list(
    request,  # pyright: ignore[reportUnusedParameter]
):
    """등록된 모든 리뷰를 반환합니다."""
    return services.list_reviews()


@router.post('/', response={201: ReviewOut}, summary='리뷰 생성')
def create_review(
    request,  # pyright: ignore[reportUnusedParameter]
    payload: ReviewIn,
):
    """새 리뷰를 생성합니다. room/experience 중 정확히 하나만 지정해야 하며, 대상이나 owner가 없으면 404."""
    return 201, services.create_review(payload)


@router.get('/{review_id}', response=ReviewOut, summary='리뷰 상세 조회')
def get_review(
    request,  # pyright: ignore[reportUnusedParameter]
    review_id: int,
):
    """`review_id`에 해당하는 리뷰를 반환합니다. 없으면 404."""
    return services.get_review(review_id)


@router.put('/{review_id}', response=ReviewOut, summary='리뷰 수정')
def update_review(
    request,  # pyright: ignore[reportUnusedParameter]
    review_id: int,
    payload: ReviewUpdateIn,
):
    """전달된 필드로 리뷰 전체를 교체합니다(PUT). owner는 생략 시 기존 값 유지. 없으면 404."""
    return services.update_review(review_id, payload)


@router.delete('/{review_id}', response={204: None}, summary='리뷰 삭제')
def delete_review(
    request,  # pyright: ignore[reportUnusedParameter]
    review_id: int,
):
    """`review_id`에 해당하는 리뷰를 삭제합니다."""
    services.delete_review(review_id)
    return 204, None
