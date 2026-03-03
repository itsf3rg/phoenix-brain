import asyncio
import websockets
import json
import time

async def inject_mocks():
    uri = "wss://phoenix-brain.onrender.com/ws"
    
    mock_offers = [
        {
            "type": "new_offer",
            "offer": {
                "id": "mock-uber-1",
                "platform": "Uber",
                "fare": 13.77,
                "pickup_miles": 1.9,
                "trip_miles": 18.3,
                "total_miles": 20.2,
                "pickup_minutes": 1,
                "total_minutes": 33,
                "is_silent": False,
                "raw_text": "Live mock text"
            },
            "evaluation": {
                "dollars_per_mile": 0.68,
                "dollars_per_hour": 25.03,
                "score": 38,
                "decision": "DECLINE"
            }
        },
        {
            "type": "new_offer",
            "offer": {
                "id": "mock-lyft-1",
                "platform": "Lyft",
                "fare": 24.60,
                "pickup_miles": 1.2,
                "trip_miles": 27.8,
                "total_miles": 29.0,
                "pickup_minutes": 1,
                "total_minutes": 44,
                "is_silent": False,
                "raw_text": "Live mock text"
            },
            "evaluation": {
                "dollars_per_mile": 0.85,
                "dollars_per_hour": 33.54,
                "score": 67,
                "decision": "IGNORE"
            }
        },
        {
            "type": "new_offer",
            "offer": {
                "id": "mock-uber-2",
                "platform": "Uber",
                "fare": 8.75,
                "pickup_miles": 2.4,
                "trip_miles": 6.5,
                "total_miles": 8.9,
                "pickup_minutes": 9,
                "total_minutes": 23,
                "is_silent": False,
                "raw_text": "Live mock text"
            },
            "evaluation": {
                "dollars_per_mile": 0.98,
                "dollars_per_hour": 22.82,
                "score": 88,
                "decision": "ACCEPT"
            }
        }
    ]
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to GigBoss WebSocket.")
            for payload in mock_offers:
                print(f"Injecting mock offer for {payload['offer']['platform']}: ${payload['offer']['fare']}")
                await websocket.send(json.dumps(payload))
                time.sleep(2) # Wait 2 seconds between cards so we can see the animation slide down
            print("Injection complete.")
    except Exception as e:
        print(f"Failed to connect to active WS server: {e}")

if __name__ == "__main__":
    asyncio.run(inject_mocks())
