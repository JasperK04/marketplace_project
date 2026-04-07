import re
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, func, select
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.Category import Category
from app.models.mixin import PaginatedAPIMixin
from app.models.User import User


class ListingCondition(str, Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    GOOD = "good"
    FAIR = "fair"


class Listing(PaginatedAPIMixin, db.Model):
    CONDITION_LABELS = {
        ListingCondition.NEW.value: "New",
        ListingCondition.LIKE_NEW.value: "Like New",
        ListingCondition.GOOD.value: "Good",
        ListingCondition.FAIR.value: "Fair",
    }
    CONDITION_CHOICES = [(key, label) for key, label in CONDITION_LABELS.items()]
    DEFAULT_CONDITION = ListingCondition.GOOD.value

    id: Mapped[int] = mapped_column(primary_key=True)
    userID: Mapped[int] = mapped_column(ForeignKey("user.id"))
    categoryID: Mapped[int] = mapped_column(ForeignKey("category.id"))
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    condition: Mapped[ListingCondition] = mapped_column(
        SAEnum(
            ListingCondition,
            name="listing_condition",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        server_default=DEFAULT_CONDITION,
    )
    sold: Mapped[bool] = mapped_column(nullable=False, insert_default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )  # type: ignore
    is_deactivated: Mapped[bool] = mapped_column(nullable=False, server_default="0")

    def to_dict(self):
        seller = db.session.scalar(select(User).where(User.id == self.userID))

        data: dict[
            str, int | dict[str, int | str | None] | str | float | bool | datetime
        ] = {
            "id": self.id,
            "seller": {
                "id": self.userID,
                "username": seller.username,
                "name": seller.name,
            },
            "title": self.title,
            "price": format((self.price / 100), ".2f"),
            "description": self.description,
            "category": {
                "id": self.categoryID,
                "name": db.session.scalar(
                    select(Category.name).where(Category.id == self.categoryID)
                ),
            },
            "condition": self.condition.value,
            "sold": self.sold,
            "created_at": self.created_at,
            "is_deactivated": self.is_deactivated,
        }
        return data

    def from_dict(self, data: dict[str, str | int], sold: bool = False):
        for field in [
            "id",
            "userID",
            "categoryID",
            "title",
            "price",
            "description",
            "condition",
        ]:
            if field in data:
                if field == "condition":
                    setattr(self, field, Listing.normalize_condition(data[field]))
                else:
                    setattr(self, field, data[field])
        if not getattr(self, "condition", None):
            setattr(self, "condition", Listing.normalize_condition(None))
        setattr(self, "sold", sold)
        return self

    def deactivate(self):
        self.is_deactivated = True
        return self

    def reactivate(self):
        self.is_deactivated = False
        return self

    @staticmethod
    def normalize_title(title: str):
        return title.title()

    @staticmethod
    def normalize_price(price: str):
        price = price.replace(",", ".")
        price = re.sub(r"[^\d.]", "", price)
        price_float = float(price)
        return round(price_float * 100)

    @staticmethod
    def normalize_description(text: str):
        normalized = ""
        for line in text.split("\n"):
            line = line.strip()
            if line:
                normalized += line[0].upper() + line[1:] + "\n"
        return normalized

    @staticmethod
    def normalize_condition(condition: str | ListingCondition | None):
        if not condition:
            return ListingCondition.GOOD
        if isinstance(condition, ListingCondition):
            return condition
        normalized = condition.strip().lower().replace(" ", "_")
        try:
            return ListingCondition(normalized)
        except ValueError as exc:
            raise ValueError("Invalid condition") from exc

    @staticmethod
    def find_open_listings(limit: int | None = None):
        if limit:
            return (
                db.session.execute(
                    select(Listing)
                    .where(~Listing.sold, ~Listing.is_deactivated)
                    .limit(limit)
                )
                .scalars()
                .all()
            )
        return (
            db.session.execute(
                select(Listing).where(~Listing.sold, ~Listing.is_deactivated)
            )
            .scalars()
            .all()
        )
