from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)

    def __init__(self, name:str, email:str):
        self.name = name
        self.email = email
        self.email = email

    def set_password(self, password:str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password:str):
        return check_password_hash(self.password_hash, password)

