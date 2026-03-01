from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import database
import ai_engine

app = FastAPI(title="Phoenix Rideshare AI Brain")

# Enable CORS for the web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "online", "region": "Phoenix"}

@app.post("/evaluate_ride")
def evaluate_ride(offer: ai_engine.RideOffer, db: Session = Depends(get_db)):
    # 1. Evaluate the ride using our Phoenix logic
    evaluation = ai_engine.evaluate_ride(offer)
    
    # 2. Log to Database
    db_log = database.RideLog(
        platform=offer.platform,
        fare=offer.fare,
        distance_miles=offer.distance_miles,
        pickup_minutes=offer.pickup_minutes,
        dropoff_location=offer.dropoff_location,
        profit_score=evaluation["score"],
        ai_decision=evaluation["decision"],
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    # 3. Return decision to the Android App
    return {
        "log_id": db_log.id,
        "decision": evaluation["decision"],
        "score": evaluation["score"],
        "reasoning": evaluation["reasoning"]
    }

@app.get("/ride_history")
def get_ride_history(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(database.RideLog).order_by(database.RideLog.timestamp.desc()).limit(limit).all()
    return logs
