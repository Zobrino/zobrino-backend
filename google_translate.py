import os
import json
from google.cloud import translate_v2 as translate

# Leer el JSON desde la variable de entorno
service_account_info = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])

# Autenticación
translate_client = translate.Client.from_service_account_info(service_account_info)

def traducir(texto, origen='es', destino='en'):
    if isinstance(texto, bytes):
        texto = texto.decode('utf-8')

    resultado = translate_client.translate(
        texto,
        source_language=origen,
        target_language=destino
    )

    return resultado['translatedText']
