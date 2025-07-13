import os
import requests
import openai
import json

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from google.cloud import translate_v2 as translate
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer
from azure.cognitiveservices.speech.audio import AudioOutputConfig

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar servicios
google_credentials = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
translate_client = translate.Client.from_service_account_info(google_credentials)
AZURE_KEY = os.environ["AZURE_SPEECH_KEY"]
AZURE_REGION = os.environ["AZURE_SPEECH_REGION"]
speech_config = SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
speech_config.speech_synthesis_voice_name = "es-MX-JorgeNeural"

@app.post("/translate", response_class=Response)
async def translate_audio(request: Request):
    try:
        form = await request.form()
        recording_url = form.get("RecordingUrl")
        if not recording_url:
            return Response(content="<Response><Say>No se recibió audio.</Say></Response>", media_type="application/xml")

        print("🎧 Descargando audio desde:", recording_url)
        audio_response = requests.get(recording_url)
        with open("user_audio.wav", "wb") as f:
            f.write(audio_response.content)
        print("✅ Audio guardado")

        print("🧠 Transcribiendo con Whisper...")
        with open("user_audio.wav", "rb") as audio_file:
            transcript_response = openai.Audio.transcribe("whisper-1", audio_file)
        texto_transcrito = transcript_response["text"]
        print("✅ Texto transcrito:", texto_transcrito)

        print("🌍 Traduciendo con Google...")
        resultado_traduccion = translate_client.translate(texto_transcrito, target_language="en")
        texto_traducido = resultado_traduccion["translatedText"]
        print("✅ Texto traducido:", texto_traducido)

        print("🗣️ Generando voz con Azure...")
        audio_config = AudioOutputConfig(filename="static/respuesta.mp3")
        synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        synthesizer.speak_text_async(texto_traducido).get()
        print("✅ Voz generada")

        return Response(content=f"<Response><Play>https://web-production-503e1.up.railway.app/static/respuesta.mp3</Play></Response>", media_type="application/xml")

    except Exception as e:
        print("❌ ERROR:", e)
        return Response(content=f"<Response><Say>Ocurrió un error: {str(e)}</Say></Response>", media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
