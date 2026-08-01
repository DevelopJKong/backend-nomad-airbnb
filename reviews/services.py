from django.shortcuts import get_object_or_404

from experiences.models import Experience
from rooms.models import Room
from users.models import User

from .models import Review
from .schemas import ReviewIn, ReviewUpdateIn


def list_reviews():
    # depth=1 중첩 직렬화의 N+1 방지: FK는 select_related로 한 번에 조인
    return Review.objects.select_related('user', 'room', 'experience').all()


def get_review(review_id: int) -> Review:
    return get_object_or_404(
        Review.objects.select_related('user', 'room', 'experience'),
        pk=review_id,
    )


def create_review(payload: ReviewIn) -> Review:
    # pyright는 런타임 attname(user_id 등)을 모르므로 인스턴스를 조회해 FK에 직접 대입 (없으면 404)
    owner: User = get_object_or_404(User, pk=payload.owner)

    # room / experience 중 하나만 온다는 보장은 스키마 validator가 이미 해줌
    room: Room | None = None
    if payload.room is not None:
        room = get_object_or_404(Room, pk=payload.room)

    experience: Experience | None = None
    if payload.experience is not None:
        experience = get_object_or_404(Experience, pk=payload.experience)

    # API의 text/owner ↔ 모델의 payload/user 매핑은 이 레이어에서 끝낸다
    return Review.objects.create(
        payload=payload.text,
        rating=payload.rating,
        user=owner,
        room=room,
        experience=experience,
    )


def update_review(review_id: int, payload: ReviewUpdateIn) -> Review:
    review: Review = get_object_or_404(Review, pk=review_id)

    # owner는 선택 — 보냈을 때만 검증 후 변경, 생략(None)하면 기존 작성자 유지
    owner: User | None = None
    if payload.owner is not None:
        owner = get_object_or_404(User, pk=payload.owner)

    room: Room | None = None
    if payload.room is not None:
        room = get_object_or_404(Room, pk=payload.room)

    experience: Experience | None = None
    if payload.experience is not None:
        experience = get_object_or_404(Experience, pk=payload.experience)

    if owner is not None:
        review.user = owner

    review.payload = payload.text
    review.rating = payload.rating
    # 대상은 전체 교체(PUT) — room으로 바꾸면 experience는 비워진다
    review.room = room
    review.experience = experience
    review.save()

    return review


def delete_review(review_id: int) -> None:
    review: Review = get_object_or_404(Review, pk=review_id)
    review.delete()
