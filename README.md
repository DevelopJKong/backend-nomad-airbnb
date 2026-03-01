# uv 설치

https://docs.astral.sh/uv/getting-started/installation/

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

# 가상환경 & 의존성 설치

```shell
uv sync
```

# 가상환경 활성화

```shell
source .venv/bin/activate
```

# 장고 프로젝트 만들기

```shell
uv run django-admin startproject config .
```

# djlint 설치

```shell
uv add djlint
```

# djlint 실행

```shell
djLint 포맷: uv run djlint --reformat <파일.html>
djLint 린트: uv run djlint --lint <파일.html>
Prettier: VSCode에서 Prettier 확장 설치 후 JS/CSS 파일에 자동 적용
```

# ruff

```shell
uv add ruff
```

# ruff 실행

```shell
uv run ruff format .    # 전체 프로젝트 포맷
uv run ruff check .     # 린트 체크
uv run ruff check --fix .  # 자동 수정 가능한 린트 이슈 수정
```

# 장고 실행

```shell
uv run python manage.py runserver
```

# 장고 마이그레이션 적용

```shell
uv run python manage.py migrate
```

# 장고 마이그레이션

```shell
uv run python manage.py makemigrations
```

# 장고 최고관리자 만들기

```shell
uv run python manage.py createsuperuser
```

# 장고 startapp

```shell
uv run python manage.py startapp houses
```

# 장고 유저 만들기

```shell
uv run python manage.py startapp users
```
