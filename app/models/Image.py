from sqlalchemy import Integer, String, ForeignKey, select, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column
from app import db

from app.models.User import User
from app.models.Listing import Listing

class Image(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    filepath : Mapped[str] = mapped_column(nullable=False)
    filename: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    variant: Mapped[str] = mapped_column(nullable=False)
    userID: Mapped[int] = mapped_column(ForeignKey("user.id"),nullable=True)
    listingID: Mapped[int] = mapped_column(ForeignKey("listing.id"),nullable=True)