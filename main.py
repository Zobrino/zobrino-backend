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
speech_config.speech_synthesis_voice_name = "es-MX-JorgeNeural"

@app.post("/translate", response_class=Response)
async def translate_audio(request: Request):
    form = await request.form()
    recording_url = form.get("RecordingUrl")
    
    if not recording_url:
        return Response(content="""
        <Response>
            <Say voice="alice" language="es-ES">No se recibió audio.</Say>
        </Response>
        """.strip(), media_type="application/xml")

    try:
        audio_url = recording_url + ".mp3"
        audio_data = requests.get(audio_url).content
        with open("temp_audio.mp3", "wb") as f:
            f.write(audio_data)

        # Transcripción con Whisper
        with open("temp_audio.mp3", "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        original_text = transcript["text"]

        # Traducción al inglés
        translation = translate_client.translate(original_text, target_language="en")
        translated_text = translation["translatedText"]

        # Generación de voz con Azure
        output_file = "static/respuesta.mp3"
        audio_config = AudioOutputConfig(filename=output_file)
        synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        synthesizer.speak_text_async(translated_text).get()

        # Responder con la voz generada
        xml_response = f"""
        <Response>
            <Play>https://zobrino-backend-production-503e1.up.railway.app/static/respuesta.mp3</Play>
        </Response>
        """
        return Response(content=xml_response.strip(), media_type="application/xml")

    except Exception as e:
        return Response(content=f"""
        <Response>
            <Say voice="alice" language="es-ES">Error: {str(e)}</Say>
        </Response>
        """.strip(), media_type="application/xml")

@app.post("/", response_class=Response)
async def answer_call():
    return Response(content="""
    <Response>
        <Say voice="alice" language=
