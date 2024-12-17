from sqlalchemy import Integer, String, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column
from flask import url_for
from app import db

from app.models.User import User
from app.models.Category import Category


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = db.paginate(query, page=page, per_page=per_page,
                                error_out=False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data

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


    