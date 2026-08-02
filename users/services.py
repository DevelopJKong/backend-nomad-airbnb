from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from .models import User
from .schemas import SignUpIn


def create_user(payload: SignUpIn) -> User:
    """회원가입. 비밀번호는 set_password로 해시해서 저장한다."""
    if User.objects.filter(username=payload.username).exists():
        raise ValidationError('이미 사용 중인 아이디입니다.')

    user = User(
        username=payload.username,
        name=payload.name,
        email=payload.email,
    )
    # User.objects.create(password=...)로 넣으면 평문이 그대로 저장된다
    user.set_password(payload.password)
    user.save()
    return user


def authenticate_user(username: str, password: str) -> User | None:
    """아이디/비밀번호를 검증하고 유저를 돌려준다. 틀리면 None.

    세션을 실제로 붙이는 login()은 request가 필요한 HTTP 관심사라 views에 남긴다.
    """
    user = authenticate(username=username, password=password)
    # authenticate()의 선언 반환형은 AbstractBaseUser라 실제 모델로 좁혀준다
    return user if isinstance(user, User) else None
