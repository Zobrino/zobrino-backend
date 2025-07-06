from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CallRequest(BaseModel):
    audio_url: str

@app.post("/translate")
async def translate_audio(req: CallRequest):
    # Placeholder response
    return {"translated_text": "Texto traducido de prueba", "voice_url": "https://example.com/audio.mp3"}