from datetime import datetime

from ninja import Schema


class PerkIn(Schema):
    name: str
    explanation: str
    details: str = ''


class PerkOut(Schema):
    id: int
    name: str
    details: str
    explanation: str
    created_at: datetime
    updated_at: datetime
