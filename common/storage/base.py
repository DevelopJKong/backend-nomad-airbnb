"""스토리지 백엔드가 공유하는 타입.

백엔드 모듈(uploadthing, s3)과 디스패처(__init__)가 서로를 import하면 순환이 되므로
공통 타입만 여기에 따로 둔다.
"""

from dataclasses import dataclass


class StorageError(Exception):
    """스토리지 연동 실패. config/urls.py의 예외 핸들러가 502로 변환한다.

    어느 백엔드를 쓰든 서비스 계층은 이 예외 하나만 알면 된다.
    """


@dataclass(frozen=True)
class UploadedFile:
    """업로드 완료된 파일.

    key는 백엔드마다 형식이 다르지만(UploadThing은 서명 키, S3는 오브젝트 키)
    삭제할 때 그대로 되돌려주면 되므로 호출부는 내용을 해석하지 않는다.
    """

    key: str
    url: str
    name: str
    size: int
