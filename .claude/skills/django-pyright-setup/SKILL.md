---
name: django-pyright-setup
description: Configure basedpyright/pyright type checking for a Django + Django Ninja project — install django-stubs, tune severity in pyproject.toml, and type reverse relations. Use when the editor floods with Django-related type errors (e.g. "str cannot be assigned to CharField", "Cannot access attribute X for class Model", Meta override errors, hundreds of reportUnknown* warnings) or when adding type annotations to ORM code.
---

# basedpyright / pyright setup for Django + Ninja

Plain pyright/basedpyright does not understand Django's descriptor/ORM magic, so a
Django project lights up with false positives. Fix it in two moves: install `django-stubs`
(real type info) and tune severities in `pyproject.toml` (silence the noise).

## 1. Install django-stubs

```bash
uv add --dev django-stubs
```
This is what makes `model.name` typed as `str` instead of `CharField`, so
`thing.name = payload.name` and `get_object_or_404(Thing, ...)` annotations type-check.
basedpyright/pyright auto-discover the stubs once installed in the venv — no plugin needed
(the mypy plugin / `[tool.django-stubs]` block is mypy-only; not required for pyright).

## 2. Configure pyproject.toml

```toml
[tool.basedpyright]
# basedpyright defaults to a very strict mode (recommended) that floods Django code
# with noise. Drop to plain-pyright "standard" to keep only meaningful diagnostics.
typeCheckingMode = "standard"
# Surface unused params as a yellow warning. NOTE: ninja's mandatory `request` will
# always trigger this (it can't be renamed/removed — see gotcha below). Set to "none"
# instead if those warnings are unwanted.
reportUnusedParameter = "warning"
# pyright misreads Django model Meta inheritance as an incompatible override — disable.
reportIncompatibleVariableOverride = "none"
```

Severity values: `"error"` (red) · `"warning"` (yellow) · `"information"` · `"hint"`
(grey, basedpyright default for many rules) · `"none"` (off).

`typeCheckingMode` options, mild → strict: `"off"` · `"basic"` · `"standard"`
(recommended for Django) · `"strict"` · `"recommended"`/`"all"` (basedpyright default —
too strict for Django, causes the reportUnknown* / reportImplicitOverride flood).

After editing, reload the language server (VS Code: "Python: Restart Language Server" or
reload window) so the new config is read.

## 3. Type reverse relations (related_name)

django-stubs (without the mypy plugin) cannot infer reverse accessors, so
`self.reviews` on a model errors with `Cannot access attribute "reviews"`. Declare the
reverse manager under `TYPE_CHECKING` (runtime untouched — Django still provides it):

```python
from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from reviews.models import Review

class Room(CommonModel):
    # Review.room has related_name='reviews' -> Room.reviews reverse manager
    if TYPE_CHECKING:
        reviews: models.Manager['Review']
```
Use `models.Manager['X']` (always importable). Do NOT import `RelatedManager` from
`django.db.models.manager` — it is not an importable symbol in current django-stubs and
errors with "unknown import symbol".

## 4. Typing ORM return values

`get_object_or_404(Thing, ...)` returns `Any`; annotate the variable so `.save()` /
field access are typed:
```python
thing: Thing = get_object_or_404(Thing, pk=thing_id)
```
With django-stubs installed this is the only annotation usually needed.

## Gotcha: the ninja `request` param must be named exactly `request`

Ninja identifies the request parameter ONLY by `name == "request"`
(`ninja/signature/details.py`), and at call time always passes it positionally
(`view_func(request, **values)` in `operation.py`). Consequences, all verified:

- **`_request` crashes at import** — ninja treats any non-`request` param as a
  body/query field and builds a Pydantic model from it; Pydantic rejects leading
  underscores: `NameError: Fields must not use names with leading underscores`.
- **Omitting the param crashes at call time** — request is still passed positionally and
  collides: `TypeError: handler() got multiple values for argument '...'` (HTTP 500).
- There is no type-based detection and no config to rename it. Making `_request` work
  would require monkeypatching ninja's `ViewSignature` — fragile, not worth it.

So the param must stay literally `request`, and it is usually unused — the Python
convention of marking unused params with a `_` prefix does NOT apply here. Choose how to
treat the resulting `reportUnusedParameter` diagnostic:

- **Keep the rule globally `"warning"` (recommended) and suppress only `request`
  per handler** — append `# pyright: ignore[reportUnusedParameter]` to each handler's
  `def` line. The rule stays active everywhere else, so genuinely unused params (in admin
  methods, helpers, etc.) still warn yellow; only the ninja `request` is silenced.
  ```python
  @router.get('/', response=list[ThingOut])
  def list_things(request):  # pyright: ignore[reportUnusedParameter]
      return services.list_things()
  ```
  Caveat: an inline `ignore` suppresses ALL `reportUnusedParameter` on that one line, so a
  second unused param on the same `def` line would also be hidden (rare — other params are
  normally used).
- **Or set `reportUnusedParameter = "none"`** to silence project-wide (also drops
  genuinely unused params elsewhere).

Never try to "fix" the request warning by renaming or removing the param.

## Verify

```bash
python manage.py check          # app still imports/boots
uvx basedpyright <apps...>      # 0 errors expected; remaining warnings are unused `request`
```
