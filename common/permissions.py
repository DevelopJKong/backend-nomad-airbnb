"""DRF의 permission_classes에 대응하는 권한 규칙.

DRF와 마찬가지로 두 층으로 나뉜다:

    has_permission(user)            객체 없이 판단 (로그인 여부, 호스트 여부)
    has_object_permission(user, obj) 객체를 봐야 판단 (소유자 여부)

적용 위치가 층마다 다르다:
  - 객체와 무관한 검사는 views의 @permission_classes 데코레이터가 처리한다.
  - 객체 수준 검사는 services에서 한다. 이 프로젝트는 views가 ORM을 만지지 않으므로
    대상 객체를 조회하는 곳이 services뿐이기 때문이다.

services가 HTTP를 모르는 상태를 유지하려고 request가 아니라 user만 받고,
거부는 상태코드가 아니라 Django의 PermissionDenied로 알린다.
(config/urls.py의 예외 핸들러가 403으로 변환한다)
"""

from functools import wraps

from django.core.exceptions import PermissionDenied


class BasePermission:
    """규칙 하나. 필요한 쪽 메서드만 재정의하면 나머지는 통과시킨다."""

    message = '이 작업을 수행할 권한이 없습니다.'

    # 기본은 통과 — 하위 클래스가 필요한 쪽만 재정의한다
    def has_permission(self, user) -> bool:  # pyright: ignore[reportUnusedParameter]
        return True

    def has_object_permission(self, user, obj) -> bool:  # pyright: ignore[reportUnusedParameter]
        return True

    def check(self, user) -> None:
        if not self.has_permission(user):
            raise PermissionDenied(self.message)

    def check_object(self, user, obj) -> None:
        if not self.has_object_permission(user, obj):
            raise PermissionDenied(self.message)


class IsAuthenticated(BasePermission):
    message = '로그인이 필요합니다.'

    def has_permission(self, user) -> bool:
        return bool(user and user.is_authenticated)


class IsHost(BasePermission):
    message = '호스트만 할 수 있습니다.'

    def has_permission(self, user) -> bool:
        return bool(user and user.is_authenticated and user.is_host)


class IsOwner(BasePermission):
    """객체의 소유자가 본인인지 본다. 객체 수준 전용이라 has_permission은 통과시킨다.

    소유자 필드명은 모델마다 다르다 (Room.owner, Review.user). owner_field로 지정한다.

        IsOwner().check_object(user, room)                        # room.owner_id
        IsOwner('user_id', '내 리뷰만...').check_object(user, review)  # review.user_id
    """

    message = '본인 소유의 리소스만 다룰 수 있습니다.'

    def __init__(self, owner_field: str = 'owner_id', message: str | None = None) -> None:
        self.owner_field = owner_field
        if message:
            self.message = message

    def has_object_permission(self, user, obj) -> bool:
        # _id로 비교하면 소유자를 다시 조회하는 쿼리가 나가지 않는다
        return bool(user and user.is_authenticated and getattr(obj, self.owner_field) == user.pk)


def permission_classes(*permissions: BasePermission):
    """핸들러 진입 시 객체와 무관한 권한을 검사한다. DRF의 permission_classes와 같은 역할.

    @router.post(...) 아래에 붙여야 한다 (라우터 등록이 가장 바깥).

        @router.post('/', auth=django_auth, response={201: RoomOut})
        @permission_classes(IsHost())
        def create_room(request, payload: RoomIn): ...
    """

    def decorator(func):
        @wraps(func)  # Ninja가 __wrapped__를 따라 원래 시그니처를 읽으므로 파라미터가 그대로 유지된다
        def wrapper(request, *args, **kwargs):
            # auth=...가 걸린 핸들러는 request.auth에 인증된 유저가 들어온다.
            # auth 없이 이 데코레이터만 쓴 경우를 위해 request.user로 폴백한다.
            user = getattr(request, 'auth', None) or getattr(request, 'user', None)
            for permission in permissions:
                permission.check(user)
            return func(request, *args, **kwargs)

        return wrapper

    return decorator
