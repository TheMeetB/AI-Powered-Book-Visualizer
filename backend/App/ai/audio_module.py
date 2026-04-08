import os
from typing import Any

from dotenv import load_dotenv
from google.cloud import texttospeech
from loguru import logger

load_dotenv()

service_account_json = "backend/App/ai/fine-loader-455404-j7-fb57bc0fa16b.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_json


def synthesize_speech(text: str, idx: int):
    # Initialize the Text-to-Speech client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized (plain text)
    input_text = texttospeech.SynthesisInput(text=text)

    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-GB",  # Match the voice name
        name="en-GB-Wavenet-A",  # British English female voice
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    # Specify the type of audio file you want to receive
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    try:
        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )
        logger.info(f"Chapter:{idx} done")
        return response.audio_content

    except Exception as e:
        logger.warning(f"[synthesize_speech] Error getting audio, error : {e}")


def loop_for_speech(list_chapters: list[tuple[Any, str]]):
    return [(idx, synthesize_speech(i[1], idx)) for idx, i in enumerate(list_chapters)]
