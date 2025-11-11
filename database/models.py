from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin # Import UserMixin
import uuid

# This creates a database object that we will connect to our app
db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

# --- NEW User Model ---
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    # --- ADD Foreign Key to link a Profile to a User ---
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    unified_profile_json = db.Column(db.JSON)
    qdrant_id = db.Column(db.String(36), unique=True, nullable=True)
    skills = db.relationship('Skill', backref='profile', cascade="all, delete-orphan")

class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    profile_id = db.Column(db.String(36), db.ForeignKey('profiles.id'), nullable=False)