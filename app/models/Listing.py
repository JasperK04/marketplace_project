from sqlalchemy import Integer, String, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column
from app import db
from .mixin import PaginatedAPIMixin

from app.models.User import User
from app.models.Category import Category


class Listing(PaginatedAPIMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    userID: Mapped[int] = mapped_column(ForeignKey("user.id"))
    categoryID: Mapped[int] = mapped_column(ForeignKey("category.id"))
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    sold: Mapped[bool] = mapped_column(nullable=False, insert_default=True)

    def to_dict(self):
        data = {
            'id': self.id,
            'seller': {
                "id": self.userID,
                "name": db.session.scalar(select(User.name).where(User.id == self.userID))
            },
            "title": self.title,
            "price": self.price,
            "description": self.description,
            "category": {
                "id": self.categoryID,
                "name": db.session.scalar(select(Category.name).where(Category.id == self.categoryID))
            },
            "sold": self.sold
        }
        return data
    
    def from_dict(self, data, sold=False):
        for field in ['id', 'userID', 'categoryID', 'title', 'price', 'description']:
            if field in data:
                setattr(self, field, data[field])
        setattr(self, "sold", sold)
        return self


    