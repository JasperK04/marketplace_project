import re
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.mixin import PaginatedAPIMixin


class Category(PaginatedAPIMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)

    def to_dict(self):
        data: dict[str, str | int] = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }
        return data

    def from_dict(self, data: dict[str, str]):
        for field in ["name", "description"]:
            if field in data:
                setattr(self, field, data[field])
        return self

    @staticmethod
    def normalize_name(name: str):
        return name.replace("_", " ").title()

    @staticmethod
    def normalize_description(description: str):
        return description.capitalize()

    @staticmethod
    def valid_name(name: str):
        return re.match(r"[a-zA-Z ]{3,}", name) is not None
