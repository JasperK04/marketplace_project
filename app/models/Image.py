from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class Image(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    # Binary image data (webp). Prefer storing image bytes here.
    data: Mapped[bytes] = mapped_column(nullable=True)
    # Optional original filename for reference
    filename: Mapped[str] = mapped_column(nullable=True)
    # type: Mapped[str] = mapped_column(nullable=False)
    # variant: Mapped[str] = mapped_column(nullable=False)
    userID: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    listingID: Mapped[int] = mapped_column(ForeignKey("listing.id"), nullable=True)

    def from_dict(self, data: dict[str, str | int | None]):
        for field in ["data", "filename", "userID", "listingID"]:
            if field in data:
                setattr(self, field, data[field])
        return self
