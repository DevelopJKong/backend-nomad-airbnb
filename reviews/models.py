from django.db import models

from common.models import CommonModel

# Create your models here.


class Review(CommonModel):
    """Review Model Definition"""

    payload = models.TextField()
    rating = models.PositiveIntegerField()

    # 관계 설정
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews')
    room = models.ForeignKey('rooms.Room', on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    experience = models.ForeignKey('experiences.Experience', on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')

    def __str__(self):
        return f'{self.room} / {self.rating}'
