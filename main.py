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
google_credentials =_
