from django.contrib import admin
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpRequest, HttpResponse
from django.urls import path
from ninja import NinjaAPI

from categories.views import router as categories_router
from common.storage import StorageError
from experiences.views import router as experiences_router
from reviews.views import router as reviews_router
from rooms.views import router as rooms_router
from users.views import router as users_router

api = NinjaAPI(
    version='1.0.0',
    title='Airbnb Clone API',
    description='노마드코더 에어비앤비 클론 백엔드 API 문서입니다.\n\nSwagger UI: `/api/v1/docs` · OpenAPI 스키마: `/api/v1/openapi.json`',
    docs_url='/docs',
)


# services는 HTTP 상태코드를 모른다는 규칙을 유지하기 위해, 서비스가 던지는 도메인 예외를
# 여기서 응답으로 변환한다. (get_object_or_404의 Http404 → 404는 Ninja가 이미 해준다)
@api.exception_handler(ValidationError)
def on_validation_error(request: HttpRequest, exc: ValidationError) -> HttpResponse:
    """입력값이 규칙에 안 맞음 — 클라이언트 잘못이므로 422."""
    return api.create_response(request, {'detail': exc.messages}, status=422)


@api.exception_handler(PermissionDenied)
def on_permission_denied(request: HttpRequest, exc: PermissionDenied) -> HttpResponse:
    """인증은 됐지만 권한이 없음 — 403. (인증 자체 실패는 Ninja가 401로 처리한다)"""
    return api.create_response(request, {'detail': str(exc) or 'Forbidden'}, status=403)


@api.exception_handler(StorageError)
def on_storage_error(request: HttpRequest, exc: StorageError) -> HttpResponse:
    """외부 스토리지 장애 — 우리 잘못도 클라이언트 잘못도 아니므로 502."""
    return api.create_response(request, {'detail': str(exc)}, status=502)


api.add_router('/users/', users_router, tags=['Users'])
api.add_router('/categories/', categories_router, tags=['Categories'])
api.add_router('/rooms/', rooms_router, tags=['Rooms'])
api.add_router('/experiences/', experiences_router, tags=['Experiences'])
api.add_router('/reviews/', reviews_router, tags=['Reviews'])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', api.urls),
]
