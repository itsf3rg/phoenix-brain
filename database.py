import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Use DATABASE_URL from environment (e.g. Supabase), fallback to local SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./phoenix_rides.db")

# Only use check_same_thread for SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class RideLog(Base):
    __tablename__ = "ride_logs"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True) # "Uber" or "Lyft"
    fare = Column(Float)
    distance_miles = Column(Float)
    pickup_minutes = Column(Integer)
    dropoff_location = Column(String) # E.g., "Sky Harbor Airport", "Buckeye", "Scottsdale"
    profit_score = Column(Float)
    ai_decision = Column(String) # "ACCEPT", "DECLINE", "IGNORE"
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
