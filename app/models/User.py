import re
from sqlalchemy import Integer, String, Date, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import timedelta, datetime, timezone
import secrets
from typing import Optional
from .mixin import PaginatedAPIMixin


class User(PaginatedAPIMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    token: Mapped[Optional[str]] = mapped_column(String(32), index=True, unique=True)
    token_expiration: Mapped[Optional[datetime]]

    def set_password(self, password:str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password:str):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name
        }
        return data
    
    def from_dict(self, data, new_user=False):
        for field in ['name', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])
        return self

    def get_token(self, expires_in=3600):
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

    @staticmethod
    def check_token(token):
        user = db.session.scalar(select(User).where(User.token == token))
        if user is None or user.token_expiration is None or user.token_expiration.replace(
                tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return None
        return user
    
    # Commented out for now, edited version of code moved to forms.py

    #@staticmethod
    #def valid_username(name):
    #    return re.match(r"^[a-zA-Z0-9_.-]{2,}$", name) is not None
    
    #@staticmethod
    #def valid_password(password): # See https://pages.nist.gov/800-63-4/sp800-63b.html#passwordver 
    #    if 15 <= len(password) <= 64:
    #        return False
    #    if not password.strip():
    #        return False
    #    return True

    #@staticmethod
    #def valid_email(email): # See https://stackoverflow.com/a/201378
    #    return re.match(r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])", email) is not None
