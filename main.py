import requests
import openai
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CallRequest(BaseModel):
    audio_url: str

@app.post("/translate")
async def translate_audio(req: CallRequest):
    try:
        # 1. Descargar el archivo de audio desde la URL
        response = requests.get(req.audio_url)
        if response.status_code != 200:
            return {"error": "No se pudo descargar el audio"}

        with open("audio.mp3", "wb") as f:
            f.write(response.content)

        # 2. Transcripción con Whisper
        with open("audio.mp3", "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)

        return {
            "translated_text": transcript["text"],
            "voice_url": "https://example.com/audio.mp3"  # se actualizará en la siguiente etapa
        }

    except Exception as e:
        return {"error": str(e)}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
