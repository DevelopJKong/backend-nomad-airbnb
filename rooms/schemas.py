from datetime import datetime

from ninja import Schema


class AmenityIn(Schema):
    name: str
    description: str | None = None


class AmenityOut(Schema):
    id: int
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime
