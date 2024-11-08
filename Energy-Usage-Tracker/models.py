from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Date, Boolean

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    role = Column(String(50), nullable=False, default='Viewer')

class EnergyUsage(db.Model):
    __tablename__ = 'energy_usage'
    id = Column(Integer, primary_key=True)
    device_id = Column(String(50), nullable=False)
    location = Column(String(255), nullable=False)
    energy_consumption_kwh = Column(Float, nullable=False)
    carbon_emissions_kgco2e = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
