import os
import requests
import openai
from fastapi import FastAPI, Request
from fastapi.responses import Response

app = FastAPI()

@app.post("/translate", response_class=Response)
async def translate_audio(request: Request):
    form = await request.form()
    recording_url = form.get("RecordingUrl")
    
    if not recording_url:
        xml_error = """
        <Response>
            <Say voice="alice" language="es-ES">No se recibió ningún audio.</Say>
        </Response>
        """
        return Response(content=xml_error.strip(), media_type="application/xml")
    
    # Descargar el audio de Twilio (se debe agregar .mp3)
    audio_url = recording_url + ".mp3"

    try:
        # Descarga el audio
        audio_data = requests.get(audio_url).content
        with open("temp_audio.mp3", "wb") as f:
            f.write(audio_data)

        # Transcribir con Whisper
        with open("temp_audio.mp3", "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        
        translated_text = transcript["text"]  # ← este es el texto que será traducido en la s_
