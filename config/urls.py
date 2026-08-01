from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.urls import path
from ninja import NinjaAPI

from categories.views import router as categories_router
from common.uploadthing import UploadThingError
from experiences.views import router as experiences_router
from reviews.views import router as reviews_router
from rooms.views import router as rooms_router

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


@api.exception_handler(UploadThingError)
def on_uploadthing_error(request: HttpRequest, exc: UploadThingError) -> HttpResponse:
    """외부 스토리지 장애 — 우리 잘못도 클라이언트 잘못도 아니므로 502."""
    return api.create_response(request, {'detail': str(exc)}, status=502)


api.add_router('/categories/', categories_router, tags=['Categories'])
api.add_router('/rooms/', rooms_router, tags=['Rooms'])
api.add_router('/experiences/', experiences_router, tags=['Experiences'])
api.add_router('/reviews/', reviews_router, tags=['Reviews'])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', api.urls),
]
