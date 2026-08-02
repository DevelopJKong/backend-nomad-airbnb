"""AWS S3 스토리지 백엔드.

DB에는 영구적인 공개 URL을 저장하므로, 버킷이 공개 읽기를 허용해야 한다.
2023년 4월 이후 생성된 버킷은 ACL이 기본 비활성(Object Ownership = Bucket owner enforced)이라
객체마다 ACL을 거는 방식이 통하지 않는다. 그래서 기본값은 ACL을 보내지 않는 것이고,
공개 접근은 버킷 정책이나 CloudFront로 열어야 한다.
 - ACL이 활성화된 버킷이라면 AWS_S3_ACL='public-read'
 - CloudFront를 앞에 뒀다면 AWS_S3_CUSTOM_DOMAIN
"""

from urllib.parse import quote

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings

from .base import StorageError, UploadedFile

# 버킷 최상단에 파일이 흩어지지 않도록 접두사를 둔다
KEY_PREFIX = 'room-photos/'


def _client():
    if not settings.AWS_STORAGE_BUCKET_NAME:
        raise StorageError('AWS_STORAGE_BUCKET_NAME이 설정되지 않았습니다.')

    # 자격증명을 명시하지 않으면 boto3가 환경변수/IAM 역할 등 기본 체인을 따라간다.
    # 로컬 개발은 .env, 배포는 IAM 역할을 쓰는 흔한 구성을 둘 다 지원하기 위함.
    return boto3.client(
        's3',
        region_name=settings.AWS_S3_REGION_NAME or None,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
    )


def _public_url(key: str) -> str:
    if settings.AWS_S3_CUSTOM_DOMAIN:
        return f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/{quote(key)}'

    region = settings.AWS_S3_REGION_NAME
    host = f'{settings.AWS_STORAGE_BUCKET_NAME}.s3.{region}.amazonaws.com' if region else f'{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    return f'https://{host}/{quote(key)}'


def upload(*, content: bytes, name: str, content_type: str) -> UploadedFile:
    """파일 바이트를 S3에 올리고 접근 가능한 URL을 돌려준다."""
    key = f'{KEY_PREFIX}{name}'

    params = {
        'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
        'Key': key,
        'Body': content,
        # 지정하지 않으면 브라우저가 binary/octet-stream으로 받아 이미지를 렌더링하지 않는다
        'ContentType': content_type,
    }
    if settings.AWS_S3_ACL:
        params['ACL'] = settings.AWS_S3_ACL

    try:
        _client().put_object(**params)
    except (BotoCoreError, ClientError) as exc:
        raise StorageError(f'S3 업로드에 실패했습니다: {exc}') from exc

    return UploadedFile(key=key, url=_public_url(key), name=name, size=len(content))


def delete(key: str) -> None:
    """업로드된 파일을 S3에서 삭제한다."""
    try:
        _client().delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
    except (BotoCoreError, ClientError) as exc:
        raise StorageError(f'S3 파일 삭제에 실패했습니다: {exc}') from exc
