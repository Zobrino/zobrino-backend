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
    
    # Descargar el audio de Twilio (.mp3)
    audio_url = recording_url + ".mp3"

    try:
        audio_data = requests.get(audio_url).content
        with open("temp_audio.mp3", "wb") as f:
            f.write(audio_data)

        with open("temp_audio.mp3", "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        
        translated_text = transcript["text"]

        xml_success = f"""
        <Response>
            <Say voice="alice" language="es-ES">Recibido. Usted dijo: {translated_text}</Say>
        </Response>
        """
        return Response(content=xml_success.strip(), media_type="application/xml")

    except Exception as e:
        xml_error = f"""
        <Response>
            <Say voice="alice" language="es-ES">Ocurrió un error: {str(e)}</Say>
        </Response>
        """
        return Response(content=xml_error.strip(), media_type="application/xml")


@app.post("/", response_class=Response)
async def answer_call():
    xml_content = """
    <Response>
        <Say voice="alice" language="es-ES">Gracias por llamar a Zobrino. Por favor, hable después del tono.</Say>
        <Record
            maxLength="15"
            timeout="2"
            playBeep="true"
            action="/translate"
            method="POST"
            trim="trim-silence"/>
        <Say voice="alice" language="es-ES">No se recibió ningún mensaje. Adiós.</Say>
        <Hangup/>
    </Response>
    """
    return Response(content=xml_content.strip(), media_type="application/xml")


@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Zobrino backend activo"}
