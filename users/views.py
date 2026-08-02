from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from ninja import Router
from ninja.errors import AuthenticationError
from ninja.security import django_auth

from . import services
from .schemas import CsrfOut, LogInIn, SignUpIn, UserOut

router = Router()


@router.get('/csrf', response=CsrfOut, summary='CSRF 토큰 발급')
def get_csrf_token(request):
    """csrftoken 쿠키를 심고 토큰 값을 돌려줍니다.

    세션 인증은 쿠키 기반이라 쓰기 요청(POST/PUT/DELETE)에 CSRF 토큰이 필요합니다.
    받은 값을 `X-CSRFToken` 헤더에 넣어 보내세요.
    """
    # get_token()이 쿠키 갱신 플래그를 세우고, CsrfViewMiddleware가 응답에 쿠키를 심는다
    return {'csrftoken': get_token(request)}


@router.post('/', response={201: UserOut}, summary='회원가입')
def sign_up(
    request,  # pyright: ignore[reportUnusedParameter]
    payload: SignUpIn,
):
    """새 계정을 만듭니다. 아이디가 중복이면 422."""
    return 201, services.create_user(payload)


@router.post('/login', response=UserOut, summary='로그인')
def log_in(request, payload: LogInIn):
    """세션에 로그인하고 sessionid 쿠키를 내려줍니다. 자격증명이 틀리면 401."""
    user = services.authenticate_user(payload.username, payload.password)
    if user is None:
        # 아이디가 없는 건지 비밀번호가 틀린 건지 구분해주지 않는다 (계정 존재 여부 노출 방지)
        raise AuthenticationError(message='아이디 또는 비밀번호가 올바르지 않습니다.')

    login(request, user)
    return user


@router.post('/logout', auth=django_auth, response={204: None}, summary='로그아웃')
def log_out(request):
    """세션을 파기합니다."""
    logout(request)
    return 204, None


@router.get('/me', auth=django_auth, response=UserOut, summary='내 정보 조회')
def me(request):
    """현재 로그인한 유저를 반환합니다. 비로그인이면 401."""
    # auth=django_auth가 인증에 성공하면 request.auth에 User가 들어온다
    return request.auth
