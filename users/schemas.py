from datetime import datetime

from ninja import Field, Schema


class UserOut(Schema):
    """비밀번호 관련 필드는 절대 노출하지 않는다."""

    id: int
    username: str
    name: str
    email: str
    is_host: bool
    gender: str
    language: str
    currency: str
    date_joined: datetime


class SignUpIn(Schema):
    username: str = Field(max_length=150)
    password: str = Field(min_length=8)
    name: str = Field(max_length=150)
    email: str = ''


class LogInIn(Schema):
    username: str
    password: str


class CsrfOut(Schema):
    """세션 인증은 쿠키를 쓰므로 쓰기 요청에 CSRF 토큰이 필요하다."""

    csrftoken: str
