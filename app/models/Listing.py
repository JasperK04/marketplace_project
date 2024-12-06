from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app import db

class Listing(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    userID: Mapped[int] = mapped_column(ForeignKey("user.id"))
    categoryID: Mapped[int] = mapped_column(ForeignKey("category.id"))
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)

    def __init__(self, userid: int, categoryid: int, title: str, description: str, price: int):
        """

        :param userid: The user the listing belongs to
        :param categoryid: The category the listing belongs to
        :param title: The title of the listing
        :param description: The description of the listing
        :param price: The price in cents (not euros)
        """
        self.userID = userid
        self.categoryID = categoryid
        self.title = title
        self.description = description
        self.price = price