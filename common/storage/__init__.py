"""파일 스토리지 진입점.

settings.UPLOAD_SERVER 값에 따라 백엔드를 고른다. 서비스 계층은 어느 백엔드가 쓰이는지
알 필요 없이 storage.upload() / storage.delete() 와 StorageError만 알면 된다.

    UPLOAD_SERVER=UPLOADTHING   → UploadThing (기본값)
    UPLOAD_SERVER=AWS           → AWS S3

주의: Photo.key/url에는 업로드 당시 백엔드가 만든 값이 그대로 남는다. 운영 중 백엔드를
바꾸면 기존 파일은 예전 백엔드에 남아 있으므로, 이전 데이터의 삭제는 동작하지 않는다.
"""

from django.conf import settings

from . import s3, uploadthing
from .base import StorageError, UploadedFile

__all__ = ['StorageError', 'UploadedFile', 'delete', 'upload']

_BACKENDS = {
    'UPLOADTHING': uploadthing,
    'AWS': s3,
}


def _backend():
    # settings.py가 부팅 시점에 값을 검증하므로 여기까지 잘못된 값이 오는 건 이례적이다.
    # 테스트에서 override_settings로 바꾸는 경우를 대비해 방어적으로 확인한다.
    try:
        return _BACKENDS[settings.UPLOAD_SERVER]
    except KeyError as exc:
        raise StorageError(f'UPLOAD_SERVER 값이 올바르지 않습니다: {settings.UPLOAD_SERVER!r} (가능한 값: {", ".join(sorted(_BACKENDS))})') from exc


def upload(*, content: bytes, name: str, content_type: str) -> UploadedFile:
    """파일 바이트를 현재 설정된 스토리지에 올리고 접근 가능한 URL을 돌려준다."""
    return _backend().upload(content=content, name=name, content_type=content_type)


def delete(key: str) -> None:
    """업로드된 파일을 현재 설정된 스토리지에서 삭제한다."""
    _backend().delete(key)
