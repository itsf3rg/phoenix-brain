from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import uuid
import codecs
from typing import List

from models.offer import RideOffer
from engine.scorer import calculate_score
from engine.parser import parse_offer_text

app = FastAPI(title="GigBoss Brain API")

# Deduplication Cache to prevent the Android Scanner from spamming 
# the dashboard with 5 identical cards for the same 6-second offer ping.
RECENT_OFFERS_CACHE = []

# Enable CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_json(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                pass

manager = ConnectionManager()

class RawPayload(BaseModel):
    raw_text: str
    platform: str = "uber"

@app.get("/")
def read_root():
    return {"status": "GigBoss Brain Online. Websockets ready."}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            pass # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/evaluate")
async def evaluate_ride(offer: RideOffer):
    score_data = calculate_score(offer)
    
    payload = {
        "type": "new_offer",
        "offer": offer.model_dump(),
        "evaluation": score_data
    }
    
    await manager.broadcast_json(payload)
    return score_data

@app.post("/parse_and_evaluate")
async def parse_and_evaluate(payload: RawPayload):
    # Safely log incoming payloads to a file to avoid Windows Console Unicode crashes
    with codecs.open("incoming_payloads_debug.log", "a", "utf-8") as f:
        f.write(f"[{payload.platform.upper()}] RAW: {payload.raw_text}\n")
        f.write("-" * 80 + "\n")

    parsed_data = parse_offer_text(payload.raw_text, payload.platform)
    
    # Filter out false-positive empty screen scrapes
    if parsed_data['fare'] <= 0.0:
        return {"status": "ignored", "reason": "No valid fare detected in text"}

    # Project Phoenix: Deduplication Anti-Spam (prevent identical offers hitting the UI twice)
    # Create a unique 3-part mathematical fingerprint for the offer.
    offer_signature = f"{parsed_data['fare']}_{parsed_data['total_miles']}_{parsed_data['total_minutes']}"
    
    if offer_signature in RECENT_OFFERS_CACHE:
        return {"status": "ignored", "reason": "Duplicate offer already pushed to dashboard."}
        
    # Add to cache and keep only the last 20 signatures in memory
    RECENT_OFFERS_CACHE.append(offer_signature)
    if len(RECENT_OFFERS_CACHE) > 20:
        RECENT_OFFERS_CACHE.pop(0)

    offer = RideOffer(
        id=str(uuid.uuid4()),
        platform=payload.platform,
        fare=parsed_data['fare'],
        pickup_miles=parsed_data['pickup_miles'],
        trip_miles=parsed_data['trip_miles'],
        total_miles=parsed_data['total_miles'],
        pickup_minutes=parsed_data['pickup_minutes'],
        total_minutes=parsed_data['total_minutes'],
        raw_text=payload.raw_text
    )
    
    score_data = calculate_score(offer)
    
    broadcast_payload = {
        "type": "new_offer",
        "offer": offer.model_dump(),
        "evaluation": score_data
    }
    
    await manager.broadcast_json(broadcast_payload)
    return {"offer": offer.model_dump(), "evaluation": score_data}
