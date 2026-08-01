from django.db import migrations, models


class Migration(migrations.Migration):
    """Photo의 파일 저장을 로컬 ImageField에서 UploadThing(원격 URL + key)으로 전환.

    medias_photo가 비어 있는 상태에서 작성했으므로 데이터 이관 없이 필드를 교체한다.
    기존 행이 있는 DB에 적용하려면 url/key를 채우는 데이터 마이그레이션이 먼저 필요하다.
    """

    dependencies = [
        ('medias', '0002_alter_photo_experience_alter_photo_room_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='file',
        ),
        migrations.AddField(
            model_name='photo',
            name='url',
            field=models.URLField(default='', max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photo',
            name='key',
            field=models.CharField(default='', max_length=300, unique=True),
            preserve_default=False,
        ),
    ]
