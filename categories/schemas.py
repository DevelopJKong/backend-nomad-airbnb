from datetime import datetime
from enum import Enum

from ninja import Schema


class CategoryKind(str, Enum):
    ROOMS = 'rooms'
    EXPERIENCES = 'experiences'


class CategoryIn(Schema):
    name: str
    kind: CategoryKind


class CategoryOut(Schema):
    pk: int
    name: str
    kind: str
    created_at: datetime


class CategoryPatch(Schema):
    name: str | None = None
    kind: CategoryKind | None = None
