from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column("username", String, nullable=False))
    email: str = Field(sa_column=Column("email", String, nullable=False, unique=True))
    password_hash: str = Field(sa_column=Column("passwordHash", String, nullable=False))
    display_name: Optional[str] = Field(default=None, sa_column=Column("displayName", String, nullable=True))
    is_admin: bool = Field(
        default=False,
        sa_column=Column("isAdmin", Boolean, nullable=False, default=False)
    )
    createdAt: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        sa_column=Column("createdAt", String, nullable=False,
                         default=lambda ctx: datetime.utcnow().isoformat())
    )

    def get_username(self): return self.username
    def set_username(self, username: str): self.username = username

    def get_email(self): return self.email
    def set_email(self, email: str): self.email = email

    def get_password_hash(self): return self.password_hash
    def set_password_hash(self, password_hash: str): self.password_hash = password_hash

    def get_display_name(self): return self.display_name
    def set_display_name(self, display_name: str): self.display_name = display_name

    def is_admin_user(self) -> bool: return self.is_admin

    def __repr__(self):
        return (f"User(username={self.username}, email={self.email}, "
                f"display_name={self.display_name}, is_admin={self.is_admin})")