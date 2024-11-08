from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Boolean

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)  # Set length to 150 for usernames
    password = Column(String(255), nullable=False)               # Length 255 for secure storage of hashed passwords
    is_admin = Column(Boolean, default=False)
    role = Column(String(50), nullable=False, default='Viewer')  # New role attribute with default 'Viewer'


class Property(db.Model):
    __tablename__ = 'properties'
    id = Column(Integer, primary_key=True)
    property_id = Column(String(50), unique=True, nullable=False)  # Length of 50 for IDs
    location = Column(String(255), nullable=False)                 # Length 255 for locations
    price = Column(Float, nullable=False)
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Integer, nullable=False)
    square_feet = Column(Integer, nullable=False)
    year_built = Column(Integer, nullable=False)
    property_type = Column(String(100), nullable=False)            # Length 100 for property types
    listing_status = Column(String(100), nullable=False)           # Length 100 for listing status
