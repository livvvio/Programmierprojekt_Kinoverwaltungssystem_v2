from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean
from sqlmodel import SQLModel, Field


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

    def __repr__(self) -> str:
        return (f"User(username={self.username}, email={self.email}, "
                f"display_name={self.display_name}, is_admin={self.is_admin})")
