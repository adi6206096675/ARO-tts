from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google import genai
import asyncio
import os

app = FastAPI(title="Aro Live", description="Real-Time Voice AI via WebSockets")

# Initialize the Google Gemini Client
# IMPORTANT: You must set your API key in your terminal first: export GEMINI_API_KEY="your_key"
client = genai.Client()

@app.on_event("startup")
async def startup_message():
    print("🚀 Aro Real-Time WebSocket Server is Online.")

@app.websocket("/v1/audio/stream")
async def websocket_endpoint(websocket: WebSocket):
    # 1. Accept the incoming WebSocket connection from your frontend app
    await websocket.accept()
    print("🟢 User connected to Aro Live Stream")
    
    try:
        # 2. Open a real-time connection to the Gemini Live model
        # (Using the current standard live model identifier)
        async with client.aio.live.connect(model='gemini-2.0-flash-exp', config={"generation_config": {"response_modalities": ["AUDIO"]}}) as gemini_session:
            print("🔗 Connected to Gemini Live API")
            
            # --- TASK A: Receive audio from User -> Send to Gemini ---
            async def listen_to_user():
                try:
                    while True:
                        # Receive raw audio data from the browser/app
                        user_audio_chunk = await websocket.receive_bytes()
                        # Stream it directly to Gemini
                        await gemini_session.send(input={"data": user_audio_chunk, "mime_type": "audio/pcm"}, end_of_turn=False)
                except WebSocketDisconnect:
                    print("User disconnected.")
                except Exception as e:
                    print(f"Error reading user audio: {e}")

            # --- TASK B: Receive audio from Gemini -> Send to User ---
            async def listen_to_gemini():
                try:
                    async for response in gemini_session.receive():
                        # When Gemini speaks, it sends audio chunks
                        server_content = response.server_content
                        if server_content is not None:
                            model_turn = server_content.model_turn
                            if model_turn is not None:
                                for part in model_turn.parts:
                                    if part.inline_data:
                                        # Send Gemini's audio chunk back to the browser/app
                                        await websocket.send_bytes(part.inline_data.data)
                except Exception as e:
                    print(f"Error receiving Gemini audio: {e}")

            # 3. Run both tasks simultaneously!
            # This is the magic that allows barge-in and real-time interruption.
            await asyncio.gather(
                listen_to_user(),
                listen_to_gemini()
            )

    except WebSocketDisconnect:
        print("🔴 User disconnected from Aro Live Stream.")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        await websocket.close()