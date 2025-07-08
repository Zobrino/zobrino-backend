import os
import requests

def texto_a_voz(texto, idioma='es-MX', voz='es-MX-DaliaNeural'):
    azure_key = os.environ.get("AZURE_SPEECH_KEY")
    azure_region = os.environ.get("AZURE_SPEECH_REGION")
    
    if not azure_key or not azure_region:
        raise ValueError("Faltan las credenciales de Azure Speech")

    url = f"https://{azure_region}.tts.speech.microsoft.com/cognitiveservices/v1"

    headers = {
        "Ocp-Apim-Subscription-Key": azure_key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
        "User-Agent": "zobrino-backend"
    }

    ssml = f"""
    <speak version='1.0' xml:lang='{idioma}'>
        <voice xml:lang='{idioma}' name='{voz}'>{texto}</voice>
    </speak>
    """

    response = requests.post(url, headers=headers, data=ssml.encode("utf-8"))
    
    if response.status_code == 200:
        with open("respuesta.mp3", "wb") as out:
            out.write(response.content)
        return "respuesta.mp3"
    else:
        raise Exception(f"Error en Azure TTS: {response.status_code}, {response.text}")
