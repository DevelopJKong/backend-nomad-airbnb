from django.db import models

from common.models import CommonModel


class Photo(CommonModel):
    """Photo Model Definition"""

    # 파일 실체는 UploadThing에 있고 DB에는 접근 URL과 삭제용 key만 둔다.
    # key는 UploadThing의 /v6/deleteFiles 호출에 필요하며, 없으면 고아 파일이 남는다.
    url = models.URLField(max_length=500)
    key = models.CharField(max_length=300, unique=True)
    caption = models.CharField(max_length=140)
    # 관계 설정
    room = models.ForeignKey('rooms.Room', on_delete=models.CASCADE, null=True, blank=True, related_name='photos')
    experience = models.ForeignKey('experiences.Experience', on_delete=models.CASCADE, null=True, blank=True, related_name='photos')

    def __str__(self):
        return 'Photo File'


class Video(CommonModel):
    """Video Model Definition"""

    file = models.FileField()
    # 관계 설정
    experience = models.OneToOneField('experiences.Experience', on_delete=models.CASCADE, related_name='videos')

    def __str__(self):
        return 'Video File'
