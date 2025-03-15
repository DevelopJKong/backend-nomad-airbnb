# poetry 설치

https://python-poetry.org/docs/#installing-with-the-official-installer

```shell
curl -sSL https://install.python-poetry.org | python3 -
```

# 터미널 실행

```shell
# poetry 2.0.0 이하
poetry shell

# poetry 2.0.0 이후
poetry env activate
poetry env info
poetry env list
poetry env remove
poetry env use
```

# 장고 실행

```shell
poetry install
poetry install --no-root
poetry run python manage.py runserver
```

# 장고 마이그레이션 적용

```shell
poetry run python manage.py migrate
```

# 장고 마이그레이션

```shell
poetry run python manage.py makemigrations
```

# 장고 최고관리자 만들기

```shell
poetry run python manage.py createsuperuser
```

# 장고 startapp

```shell
poetry run python manage.py startapp houses
```

# 장고 유저 만들기

```shell
poetry run python manage.py startapp users
```
