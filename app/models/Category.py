from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app import db

from .mixin import PaginatedAPIMixin


class Category(PaginatedAPIMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name
        }
        return data

    def from_dict(self, data):
        for field in ['name']:
            if field in data:
                setattr(self, field, data[field])
        return self
