"""UploadThing 파일 스토리지 클라이언트.

UploadThing은 공식 Python SDK가 없어 프로토콜을 직접 구현한다.
v7부터 REST의 /v6/uploadFiles는 폐기됐고("Unsupported operation"), 업로드는 이렇게 동작한다:

  1. appId를 Sqids로 인코딩한 접두사 + 랜덤 시드로 파일 키를 만든다
  2. {region}.ingest.uploadthing.com/{키} 에 메타데이터를 쿼리스트링으로 붙인다
  3. 그 URL 전체를 apiKey로 HMAC-SHA256 서명해 signature 파라미터로 덧붙인다
  4. 서명된 URL로 파일을 multipart PUT 한다

삭제는 아직 REST(/v6/deleteFiles)가 살아 있어 그대로 쓴다.
https://docs.uploadthing.com/uploading-files

이 모듈은 스토리지 연동만 책임지고 도메인 로직(어떤 Room에 붙일지 등)은 모른다.
실패는 공통 StorageError로 통일해 서비스 계층이 백엔드를 구분하지 않아도 되게 한다.
"""

import base64
import hashlib
import hmac
import json
import math
import time
import uuid
from dataclasses import dataclass
from urllib.parse import urlencode

import httpx
from django.conf import settings
from sqids import Sqids
from sqids.constants import DEFAULT_ALPHABET

from .base import StorageError, UploadedFile

API_BASE = 'https://api.uploadthing.com'

# 네트워크가 죽었을 때 요청 스레드가 무한정 잡혀 있지 않도록 상한을 둔다.
TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=60.0, pool=5.0)

# 프리사인 URL 유효 시간 (ms). 서버가 즉시 사용하므로 짧아도 충분하다.
PRESIGNED_TTL_MS = 60 * 1000


@dataclass(frozen=True)
class _Credentials:
    api_key: str
    app_id: str
    region: str


def _credentials() -> _Credentials:
    """UPLOADTHING_TOKEN(base64 JSON)에서 apiKey/appId/region을 꺼낸다."""
    token: str = settings.UPLOADTHING_TOKEN
    if not token:
        raise StorageError('UPLOADTHING_TOKEN이 설정되지 않았습니다.')

    try:
        # base64 표준 디코딩은 패딩이 맞아야 해서, 잘려 있을 경우를 대비해 채워준다
        decoded = json.loads(base64.b64decode(token + '=' * (-len(token) % 4)))
        return _Credentials(api_key=decoded['apiKey'], app_id=decoded['appId'], region=decoded['regions'][0])
    except (ValueError, KeyError, IndexError) as exc:
        # 대시보드가 주는 "UPLOADTHING_TOKEN='eyJ...'" 줄을 통째로 값에 넣는 실수가 잦다.
        raise StorageError(
            "UPLOADTHING_TOKEN 형식이 올바르지 않습니다. .env에는 'eyJ'로 시작하는 base64 토큰 값만 넣어야 합니다 "
            '(UPLOADTHING_TOKEN= 접두사나 따옴표가 값 안에 포함되지 않았는지 확인하세요).'
        ) from exc


def _to_int32(n: int) -> int:
    """JS의 비트 연산은 값을 32비트 부호 있는 정수로 변환한다. 파이썬 정수는 무한 정밀도라 직접 맞춰준다."""
    n &= 0xFFFFFFFF
    return n - 0x100000000 if n >= 0x80000000 else n


def _djb2(value: str) -> int:
    """UploadThing이 알파벳 셔플과 앱 ID 인코딩에 쓰는 DJB2 변형. JS 참조 구현을 그대로 옮긴 것."""
    h = 5381
    i = len(value)
    while i:
        i -= 1
        h = _to_int32(_to_int32(h * 33) ^ ord(value[i]))
    # JS: (h & 0xbfffffff) | ((h >>> 1) & 0x40000000) — >>> 는 부호 없는 시프트
    return _to_int32(_to_int32(h & 0xBFFFFFFF) | ((h & 0xFFFFFFFF) >> 1 & 0x40000000))


def _shuffle(alphabet: str, seed: str) -> str:
    """앱마다 Sqids 알파벳을 다르게 섞는다. 순서가 1글자라도 다르면 서버가 키를 인식하지 못한다."""
    chars = list(alphabet)
    seed_num = _djb2(seed)
    for i in range(len(chars)):
        # JS의 %는 나머지 부호가 피제수를 따르므로(파이썬은 제수를 따름) fmod로 맞춘다
        j = (int(math.fmod(seed_num, i + 1)) + i) % len(chars)
        chars[i], chars[j] = chars[j], chars[i]
    return ''.join(chars)


def _generate_file_key(app_id: str, file_seed: str) -> str:
    """파일 키 = (앱 ID를 Sqids로 인코딩한 접두사) + (base64 인코딩한 시드).

    서버는 접두사만 보고 어느 앱의 파일인지 판별하므로 이 형식을 지켜야 한다.
    """
    encoded_app_id = Sqids(alphabet=_shuffle(DEFAULT_ALPHABET, app_id), min_length=12).encode([abs(_djb2(app_id))])
    encoded_seed = base64.urlsafe_b64encode(file_seed.encode()).decode().rstrip('=')
    return f'{encoded_app_id}{encoded_seed}'


def _presigned_url(creds: _Credentials, *, file_key: str, name: str, size: int, content_type: str) -> str:
    """업로드용 서명 URL을 만든다. 서버 측 업로드라 x-ut-slug(파일 라우트)는 필요 없다."""
    params = {
        'expires': str(int(time.time() * 1000) + PRESIGNED_TTL_MS),
        'x-ut-identifier': creds.app_id,
        'x-ut-file-name': name,
        'x-ut-file-size': str(size),
        'x-ut-file-type': content_type,
        'x-ut-content-disposition': 'inline',
        'x-ut-acl': 'public-read',
    }
    url = f'https://{creds.region}.ingest.uploadthing.com/{file_key}?{urlencode(params)}'

    # 서명 대상은 signature를 붙이기 전의 URL 전체(쿼리스트링 포함)다
    digest = hmac.new(creds.api_key.encode(), url.encode(), hashlib.sha256).hexdigest()
    return f'{url}&{urlencode({"signature": f"hmac-sha256={digest}"})}'


def upload(*, content: bytes, name: str, content_type: str) -> UploadedFile:
    """파일 바이트를 UploadThing에 올리고 접근 가능한 URL을 돌려준다."""
    creds = _credentials()
    file_key = _generate_file_key(creds.app_id, uuid.uuid4().hex)
    url = _presigned_url(creds, file_key=file_key, name=name, size=len(content), content_type=content_type)

    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.put(url, files={'file': (name, content, content_type)})
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPError as exc:
        raise StorageError(f'UploadThing 업로드에 실패했습니다: {exc}') from exc
    except ValueError as exc:
        raise StorageError('UploadThing 응답을 해석할 수 없습니다.') from exc

    # ufsUrl이 현재 정식 도메인({appId}.ufs.sh)이고 url(utfs.io)은 레거시다
    file_url = body.get('ufsUrl') or body.get('url')
    if not file_url:
        raise StorageError('UploadThing이 파일 URL을 반환하지 않았습니다.')

    return UploadedFile(key=file_key, url=file_url, name=name, size=len(content))


def delete(key: str) -> None:
    """업로드된 파일을 UploadThing에서 삭제한다. Photo 삭제 시 고아 파일을 남기지 않기 위함."""
    creds = _credentials()

    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(
                f'{API_BASE}/v6/deleteFiles',
                headers={'x-uploadthing-api-key': creds.api_key},
                json={'fileKeys': [key]},
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise StorageError(f'UploadThing 파일 삭제에 실패했습니다: {exc}') from exc
