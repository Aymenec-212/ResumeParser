# app/models/user.py
from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    profiles = relationship("Profile", back_populates="owner")


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    unified_profile_json = Column(JSON)

    owner = relationship("User", back_populates="profiles")
    skills = relationship("Skill", back_populates="profile", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    profile_id = Column(String, ForeignKey("profiles.id"), nullable=False)

    profile = relationship("Profile", back_populates="skills")