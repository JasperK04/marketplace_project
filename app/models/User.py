from operator import is_
import re
from flask_login import UserMixin
from sqlalchemy import Integer, String, Date, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from datetime import timedelta, datetime, timezone
import secrets
from typing import Optional
from .mixin import PaginatedAPIMixin


class User(PaginatedAPIMixin, UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    is_admin: Mapped[bool] = mapped_column(nullable=False, server_default="0")
    is_deactivated: Mapped[bool] = mapped_column(nullable=False, server_default="0")
    about_me: Mapped[str] = mapped_column(String(140), nullable=True)
    token: Mapped[Optional[str]] = mapped_column(String(32), index=True, unique=True)
    token_expiration: Mapped[Optional[datetime]]

    def set_password(self, password:str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password:str):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        data: dict[str, str|int] = {
            'id': self.id,
            'name': self.name
        }
        return data

    def from_dict(self, data:dict[str, str], new_user:bool=False):
        for field in ['name', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])
        return self

    def get_token(self, expires_in:int=3600):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration and self.token_expiration.replace(
                tzinfo=timezone.utc) > now + timedelta(seconds=60):
            return self.token
        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.now(timezone.utc) - timedelta(
            seconds=1)

    def make_admin(self):
        """
        Makes the account an admin

        Note that this does not make the database commit
        This is left to the caller
        """
        self.is_admin = True
        return self

    def deactivate(self):
        """
        Deactivates the user account

        Note that this does not make the database commit
        This is left to the caller
        """
        self.is_deactivated = True
        return self

    def reactivate(self):
        """
        Reactivates the user account

        Note that this does not make the database commit
        This is left to the caller
        """
        self.is_deactivated = False
        return self


    @staticmethod
    def check_token(token:str):
        user = db.session.scalar(select(User).where(User.token == token))
        if user is None or user.token_expiration is None or user.token_expiration.replace(
                tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return None
        return user


    @staticmethod
    def valid_username(name:str):
        return re.match(r"^[a-zA-Z0-9_.-]{2,}$", name) is not None

    @staticmethod
    def valid_password(password:str): # See https://pages.nist.gov/800-63-4/sp800-63b.html#passwordver
        if len(password) < 15 or len(password) >= 64:
            return False
        if not password.strip():
            return False
        return True

    @staticmethod
    def valid_email(email:str): # See https://stackoverflow.com/a/201378
        return re.match(r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])", email) is not None

@login.user_loader
def load_user(id:str):
    return db.session.get(User, int(id))
