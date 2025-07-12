import os
import requests
import openai
import json

from fastapi import FastAPI, Request
from fastapi.responses import Response
from google.cloud import translate_v2 as translate
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig
from azure.cognitiveservices.speech.audio import AudioOutputConfig

app = FastAPI()

# Configurar Google Translate
google_credentials = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
translate_client = translate.Client.from_service_account_info(google_credentials)

# Configurar Azure TTS
AZURE_KEY = os.environ["AZURE_SPEECH_KEY"]
AZURE_REGION = os.environ["AZURE_SPEECH_REGION"]
speech_config = SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
speech_config.speech_synthesis_voice_name = "es-MX-JorgeNeural"  # Voz masculina cálida y neutral

@app.post("/translate", response_class=Response)
async def translate_audio(request: Request):
    form = await request.form()
    recording_url = form.get("RecordingUrl")

    if not recording_url:
        return Response(content="""
<Response>
    <Say voice="alice" language="es-ES">No se recibió audio.</Say>
</Response>
""", media_type="application/xml")
    
    # Descargar el audio del usuario
    audio_response = requests.get(recording_url)
    with open("user_audio.wav", "wb") as f:
        f.write(audio_response.content)

    # Transcripción con Whisper (OpenAI)
    with open("user_audio.wav", "rb") as audio_file:
        transcript_response = openai.Audio.transcribe("whisper-1", audio_file)
        texto_transcrito = transcript_response["text"]

    # Traducir el texto
    resultado_traduccion = translate_client.translate(texto_transcrito, target_language="en")
    texto_traducido = resultado_traduccion["translatedText"]

    # Convertir texto traducido a voz con Azure
    output_path = "static/respuesta.mp3"
