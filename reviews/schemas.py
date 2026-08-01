from datetime import datetime

from ninja import Field, Schema
from pydantic import model_validator


class ReviewOwnerOut(Schema):
    id: int
    username: str
    name: str
    is_host: bool


class ReviewTargetOut(Schema):
    """리뷰 대상(room / experience)을 depth=1로 노출할 때 쓰는 공통 최소 정보"""

    id: int
    name: str
    country: str
    city: str


class ReviewIn(Schema):
    text: str
    rating: int = Field(ge=1, le=5)
    owner: int
    room: int | None = None
    experience: int | None = None

    @model_validator(mode='after')
    def check_target(self):
        # 리뷰는 숙소 또는 체험 중 정확히 하나에만 달린다 (둘 다/둘 다 없음 모두 422)
        if (self.room is None) == (self.experience is None):
            raise ValueError('room과 experience 중 정확히 하나만 지정해야 합니다.')
        return self


class ReviewUpdateIn(Schema):
    text: str
    rating: int = Field(ge=1, le=5)
    # PUT에서 owner는 선택 — 보내면 변경, 생략하면 기존 작성자 유지
    owner: int | None = None
    room: int | None = None
    experience: int | None = None

    @model_validator(mode='after')
    def check_target(self):
        if (self.room is None) == (self.experience is None):
            raise ValueError('room과 experience 중 정확히 하나만 지정해야 합니다.')
        return self


class ReviewOut(Schema):
    id: int
    # alias: 모델 필드명(payload/user)에서 값을 읽되, 응답 키는 필드명(text/owner)으로 나간다
    text: str = Field(alias='payload')
    rating: int
    # depth=1: 관계를 ID가 아니라 한 단계 중첩된 객체로 직렬화
    owner: ReviewOwnerOut = Field(alias='user')
    room: ReviewTargetOut | None = None
    experience: ReviewTargetOut | None = None
    created_at: datetime
    updated_at: datetime
