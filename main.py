import os
import requests
import openai
import json

from fastapi import FastAPI, Request
from fastapi.responses import Response
from google.cloud import translate_v2 as translate
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer
from azure.cognitiveservices.speech.audio import AudioOutputConfig

app = FastAPI()

# Configurar Google Translate
google_credentials = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
translate_client = translate.Client.from_service_account_info(google_credentials)

# Configurar Azure TTS
AZURE_KEY = os.environ["AZURE_SPEECH_KEY"]
AZURE_REGION = os.environ["AZURE_SPEECH_REGION"]
speech_config = SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
speech_config.speech_synthesis_voice_name = "es-MX-JorgeNeural"  # Voz cálida, neutral y clara

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
    
    # 1. Descargar el audio del usuario
    audio_response = requests.get(recording_url)
    with open("user_audio.wav", "wb") as f:
        f.write(audio_response.content)

    # 2. Transcripción con Whisper (OpenAI)
    with open("user_audio.wav", "rb") as audio_file:
        transcript_response = openai.Audio.transcribe("whisper-1", audio_file)
        texto_transcrito = transcript_response["text"]

    # 3. Traducir el texto con Google Translate
    resultado_traduccion = translate_client.translate(texto_transcrito, target_language="en")
    texto_traducido = resultado_traduccion["translatedText"]

    # 4. Convertir texto traducido a voz con Azure y guardar en static/respuesta.mp3
    audio_config = AudioOutputConfig(filename="static/respuesta.mp3")
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    synthesizer.speak_text_async(texto_traducido).get()

    # 5. Responder a Twilio con XML que reproduce el MP3 generado
    return Response(content=f"""
<Response>
    <Play>https://web-production-503e1.up.railway.app/static/respuesta.mp3</Play>
</Response>
""", media_type="application/xml")

# Esto permite ejecutar localmente si lo deseas
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
