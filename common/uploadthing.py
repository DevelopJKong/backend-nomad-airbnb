"""UploadThing REST API 클라이언트.

UploadThing은 공식 Python SDK가 없어서 REST API를 직접 호출한다.
https://docs.uploadthing.com/api-reference/openapi-spec

서버 경유 업로드는 2단계다:
  1. POST /v6/uploadFiles  → 프리사인 URL + 폼 필드 + 파일 key 발급
  2. POST {프리사인 URL}    → 발급받은 필드 + 실제 바이트를 multipart로 전송

이 모듈은 HTTP 프로토콜 처리만 담당하고 도메인 로직(어떤 Room에 붙일지 등)은 모른다.
"""

import base64
import json
from dataclasses import dataclass

import httpx
from django.conf import settings

API_BASE = 'https://api.uploadthing.com'

# 네트워크가 죽었을 때 요청 스레드가 무한정 잡혀 있지 않도록 상한을 둔다.
# connect는 짧게, read/write는 파일 전송을 감안해 길게.
TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=60.0, pool=5.0)


class UploadThingError(Exception):
    """UploadThing 호출 실패. 서비스 계층에서 502로 변환된다."""


@dataclass(frozen=True)
class UploadedFile:
    """업로드 완료된 파일. key는 나중에 UploadThing에서 삭제할 때 필요하다."""

    key: str
    url: str
    name: str
    size: int


def _api_key() -> str:
    """UPLOADTHING_TOKEN(base64 JSON)에서 REST 호출용 apiKey를 꺼낸다.

    v7 토큰 형식: base64({"apiKey": "sk_live_...", "appId": "...", "regions": [...]})
    """
    token: str = settings.UPLOADTHING_TOKEN
    if not token:
        raise UploadThingError('UPLOADTHING_TOKEN이 설정되지 않았습니다.')

    try:
        # base64 표준 디코딩은 패딩이 맞아야 해서, 잘려 있을 경우를 대비해 채워준다
        decoded = base64.b64decode(token + '=' * (-len(token) % 4))
        api_key = json.loads(decoded)['apiKey']
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        raise UploadThingError('UPLOADTHING_TOKEN 형식이 올바르지 않습니다.') from exc

    return api_key


def upload(*, content: bytes, name: str, content_type: str) -> UploadedFile:
    """파일 바이트를 UploadThing에 올리고 접근 가능한 URL을 돌려준다."""
    headers = {'x-uploadthing-api-key': _api_key()}

    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            # 1단계: 프리사인 URL 발급
            presign = client.post(
                f'{API_BASE}/v6/uploadFiles',
                headers=headers,
                json={
                    'files': [{'name': name, 'size': len(content), 'type': content_type}],
                    'acl': 'public-read',
                    'contentDisposition': 'inline',
                },
            )
            presign.raise_for_status()

            data = presign.json().get('data') or []
            if not data:
                raise UploadThingError('UploadThing이 프리사인 URL을 반환하지 않았습니다.')
            slot = data[0]

            # 2단계: 발급받은 필드를 그대로 실어 실제 바이트 전송.
            # 프리사인 POST는 S3 규약상 file 필드가 마지막에 와야 하므로 fields를 먼저 넣는다.
            upload_response = client.post(
                slot['url'],
                data=slot['fields'],
                files={'file': (name, content, content_type)},
            )
            upload_response.raise_for_status()
    except httpx.HTTPError as exc:
        raise UploadThingError(f'UploadThing 업로드에 실패했습니다: {exc}') from exc

    return UploadedFile(key=slot['key'], url=slot['fileUrl'], name=name, size=len(content))


def delete(key: str) -> None:
    """업로드된 파일을 UploadThing에서 삭제한다. Photo 삭제 시 고아 파일을 남기지 않기 위함."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(
                f'{API_BASE}/v6/deleteFiles',
                headers={'x-uploadthing-api-key': _api_key()},
                json={'fileKeys': [key]},
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise UploadThingError(f'UploadThing 파일 삭제에 실패했습니다: {exc}') from exc
