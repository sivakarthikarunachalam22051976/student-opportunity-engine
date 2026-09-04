from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey
)

from sqlalchemy.orm import relationship

try:
    from .database import Base
except ImportError:
    from database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    profile = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False
    )


class StudentProfile(Base):

    __tablename__ = "student_profiles"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    year = Column(
        Integer
    )

    branch = Column(
        String
    )

    location = Column(
        String
    )

    interests = Column(
        Text
    )

    skills = Column(
        Text
    )

    opportunity_type = Column(
        String
    )

    user = relationship(
        "User",
        back_populates="profile"
    )


class SavedOpportunity(Base):

    __tablename__ = "saved_opportunities"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    opportunity_id = Column(
        Integer
    )

    title = Column(
        String
    )

    organization = Column(
        String
    )

    source_url = Column(
        String
    )