---
name: django-ninja-crud
description: Scaffold or refactor a Django app as a Django Ninja CRUD endpoint using this project's layered convention (models → schemas → services → thin views) and register it on the versioned NinjaAPI with Swagger metadata. Use when adding a new API resource, converting plain Django views to Ninja, or splitting business logic out of views into a service layer.
---

# Django Ninja CRUD (layered: models → schemas → services → views)

This project uses **Django Ninja** with a NestJS-style layered architecture. Apply this
pattern for every new API resource and keep all existing apps consistent with it.

## Layer responsibilities

| Layer | File | Responsibility | Must NOT do |
|-------|------|----------------|-------------|
| Entity | `models.py` | DB fields + domain methods (e.g. `rating()`) | — |
| DTO | `schemas.py` | `ninja.Schema` in/out validation | hold business logic |
| Service | `services.py` | **all** business logic + ORM access | know about HTTP responses (status codes) |
| Controller | `views.py` | routing, HTTP status codes (201/204), delegate to `services.*` | touch the ORM / models directly |

**Hard rule:** `views.py` never imports models or calls `.objects`. It only imports
`schemas` and `services`. This keeps logic unit-testable without HTTP round-trips.

## File templates

`schemas.py` — base `CommonModel` adds `created_at` / `updated_at`:
```python
from datetime import datetime
from ninja import Schema

class ThingIn(Schema):
    name: str
    description: str | None = None

class ThingOut(Schema):
    id: int
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime
```

`services.py` — pure logic + data access. `get_object_or_404` is allowed (raises
Django `Http404`, which Ninja maps to 404):
```python
from django.shortcuts import get_object_or_404
from .models import Thing
from .schemas import ThingIn

def list_things():
    return Thing.objects.all()

def create_thing(payload: ThingIn) -> Thing:
    return Thing.objects.create(**payload.dict())

def get_thing(thing_id: int) -> Thing:
    return get_object_or_404(Thing, pk=thing_id)

def update_thing(thing_id: int, payload: ThingIn) -> Thing:
    thing: Thing = get_object_or_404(Thing, pk=thing_id)  # annotate: see Typing below
    thing.name = payload.name
    thing.description = payload.description
    thing.save()
    return thing

def delete_thing(thing_id: int) -> None:
    thing: Thing = get_object_or_404(Thing, pk=thing_id)
    thing.delete()
```

**Update style rule (user preference):** PUT full-replace services always spell out
every field explicitly (`thing.name = payload.name`, one line per field), even when
the model has many fields and it gets long. Do NOT use
`for attr, value in ...: setattr(thing, attr, value)` loops or `**dict` munging for
PUT — explicitness beats brevity here. Same for create: prefer explicit kwargs
(`Thing.objects.create(name=payload.name, ...)`) when the model has FK/M2M fields
that need per-field handling; `**payload.dict()` is fine only for flat schemas that
map 1:1 to model fields.

The `setattr` loop is reserved for PATCH-style partial updates ONLY, where the field
set is dynamic by nature (`*Patch` schema with all-optional fields):
```python
for attr, value in payload.dict(exclude_unset=True).items():
    setattr(thing, attr, value)
```

**No premature abstraction (user preference):** do NOT extract private service helpers
(e.g. `_get_x_relations`, `_validate_x`) for logic shared only between a resource's own
create/update pair — write the validation/lookup inline in each function, even though it
duplicates a few lines. Each service function should read top-to-bottom on its own.
Extract a helper only when the same logic is genuinely needed across many call sites and
the duplication is actively hurting.

`views.py` — thin controller. Every handler has a Korean `summary=` and a docstring
(both surface in Swagger). Status codes live here, not in services:
```python
from ninja import Router
from . import services
from .schemas import ThingIn, ThingOut

router = Router()

@router.get('/', response=list[ThingOut], summary='목록 조회')
def list_things(request):
    """등록된 모든 항목을 반환합니다."""
    return services.list_things()

@router.post('/', response={201: ThingOut}, summary='생성')
def create_thing(request, payload: ThingIn):
    """새 항목을 생성합니다."""
    return 201, services.create_thing(payload)

@router.get('/{thing_id}', response=ThingOut, summary='단건 조회')
def get_thing(request, thing_id: int):
    """`thing_id`에 해당하는 항목을 반환합니다. 없으면 404."""
    return services.get_thing(thing_id)

@router.put('/{thing_id}', response=ThingOut, summary='수정')
def update_thing(request, thing_id: int, payload: ThingIn):
    return services.update_thing(thing_id, payload)

@router.delete('/{thing_id}', response={204: None}, summary='삭제')
def delete_thing(request, thing_id: int):
    services.delete_thing(thing_id)
    return 204, None
```

## Register on the versioned API

Routers are registered on the single `NinjaAPI` in `config/urls.py` (NOT via Django
`include`). Add one line with a Swagger tag:
```python
from things.views import router as things_router
api.add_router('/things/', things_router, tags=['Things'])
```
All endpoints live under `path('api/v1/', api.urls)`. Swagger UI: `/api/v1/docs`,
schema: `/api/v1/openapi.json`. `admin/` stays separate (no version prefix).

### Nested routers (sub-resources)

For a sub-resource (e.g. amenities under rooms), do NOT hardcode the joined path
(`'/rooms/amenities/'`). Compose routers so the hierarchy is expressed in code:
```python
# rooms/views.py
router = Router()           # rooms top-level router
amenity_router = Router()   # amenities sub-router (handlers registered on this)
...
router.add_router('/amenities/', amenity_router, tags=['Amenities'])

# config/urls.py
api.add_router('/rooms/', rooms_router)   # -> /api/v1/rooms/amenities/...
```
Changing the `rooms` prefix is then a one-line edit and `config/urls.py` stays clean.

## Typing (ORM returns are not `Any`)

`get_object_or_404(Thing, ...)` returns `Any` (Django ships weak type info), so
`thing.save()` / field access also become `Any`. Two fixes:

- **Per-call (no dependency, default):** annotate the variable —
  `thing: Thing = get_object_or_404(Thing, pk=thing_id)`. Pure type hint, no runtime cost.
- **Project-wide (proper fix):** add `django-stubs` so all ORM calls infer correctly:
  ```bash
  uv add --dev django-stubs
  ```
  ```toml
  # pyproject.toml
  [tool.django-stubs]
  django_settings_module = "config.settings"
  ```
  Then `: Thing` annotations are no longer needed for ORM returns.

Use per-call annotations while small; adopt `django-stubs` once ORM type noise grows.

## Testing (the payoff)

Unit-test services directly — no TestClient, no HTTP:
```python
from django.test import TestCase
from things import services
from things.schemas import ThingIn

class ThingServiceTest(TestCase):
    def test_create(self):
        thing = services.create_thing(ThingIn(name='x'))
        self.assertIsNotNone(thing.pk)
```
Keep view-level tests thin — only assert wiring/status codes, not logic.

## Checklist when adding/refactoring a resource
1. `models.py` — model extends `common.models.CommonModel`.
2. `schemas.py` — `*In` / `*Out` (+ `*Patch` with optional fields for partial update).
3. `services.py` — all CRUD logic; no HTTP status codes.
4. `views.py` — thin handlers, `summary=` + docstring, delegate to `services`; no ORM.
5. `config/urls.py` — `api.add_router('/x/', router, tags=['X'])`.
6. Verify: `python manage.py check` and confirm endpoints in `/api/v1/openapi.json`.

> Note: `"request" is not accessed` from basedpyright on handlers is expected — Ninja
> requires `request` as the first param even when unused. Not a bug; do not "fix" it.
