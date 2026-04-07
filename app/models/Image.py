from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class Image(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    filepath: Mapped[str] = mapped_column(nullable=False)
    filename: Mapped[str] = mapped_column(nullable=False)
    # type: Mapped[str] = mapped_column(nullable=False)
    # variant: Mapped[str] = mapped_column(nullable=False)
    userID: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    listingID: Mapped[int] = mapped_column(ForeignKey("listing.id"), nullable=True)

    def from_dict(self, data: dict[str, str | int | None]):
        for field in ["filepath", "filename", "userID", "listingID"]:
            if field in data:
                setattr(self, field, data[field])
        return self
