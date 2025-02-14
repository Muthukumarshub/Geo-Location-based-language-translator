from flask import Flask, render_template, request
import requests
import uuid
import azure.cognitiveservices.speech as speechsdk
import os
import time

# Constants for Azure Translator API
TRANSLATOR_KEY = "3sZFPDTQhTSDp3dEZ0S4s5JOOlsBc5tqB5irQIwZ1FpNwz4KwksIJQQJ99BAACGhslBXJ3w3AAAbACOGlPPt"
TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com/"
TRANSLATOR_LOCATION = "centralindia"

# Azure Speech Service Configuration
SPEECH_KEY = "FEE8hmK2Zxo3gCPrqauFteYlcgd6b92T0j7YhoQbKeGmlbIUXek1JQQJ99BAACYeBjFXJ3w3AAAYACOG909H"  # Replace with your Azure subscription key
SPEECH_REGION = "eastus"  # Replace with your service region
speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
speech_config.speech_synthesis_voice_name = "en-US-AvaMultilingualNeural"

# Initialize Flask app
app = Flask(__name__)

# Ensure the 'static' directory exists
if not os.path.exists("static"):
    os.makedirs("static")

AUDIO_FILE = os.path.join("static", "output_audio.wav")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get text and target language from the form
        original_text = request.form["text"]
        target_language = request.form["language"]

        # Azure Translator API setup
        path = "/translate?api-version=3.0"
        constructed_url = TRANSLATOR_ENDPOINT + path + "&to=" + target_language
        headers = {
            "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
            "Ocp-Apim-Subscription-Region": TRANSLATOR_LOCATION,
            "Content-type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }

        # Request translation
        body = [{"text": original_text}]
        response = requests.post(constructed_url, headers=headers, json=body)

        # Extract translated text
        translated_text = response.json()[0]["translations"][0]["text"]

        # Text to Speech
        audio_config = speechsdk.audio.AudioOutputConfig(filename=AUDIO_FILE)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        result = speech_synthesizer.speak_text_async(translated_text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized successfully!")
            timestamp = int(time.time())
            return render_template("index.html", original_text=original_text, translated_text=translated_text, target_language=target_language, audio_file=AUDIO_FILE, timestamp=timestamp)
        else:
            cancellation_details = result.cancellation_details
            print(f"Speech synthesis failed: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")
            return render_template("index.html", error="Text-to-speech synthesis failed.")
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=1000)
