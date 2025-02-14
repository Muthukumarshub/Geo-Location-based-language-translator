from flask import Flask, render_template, request
import requests
import uuid

# Constants for Azure Translator API
KEY = "3sZFPDTQhTSDp3dEZ0S4s5JOOlsBc5tqB5irQIwZ1FpNwz4KwksIJQQJ99BAACGhslBXJ3w3AAAbACOGlPPt"
ENDPOINT = "https://api.cognitive.microsofttranslator.com/"
LOCATION = "centralindia"

# Initialize Flask app
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def index_post():
    # Get text and target language from the form
    original_text = request.form["text"]
    target_language = request.form["language"]

    # Azure Translator API setup
    path = "/translate?api-version=3.0"
    constructed_url = ENDPOINT + path + "&to=" + target_language
    headers = {
        "Ocp-Apim-Subscription-Key": KEY,
        "Ocp-Apim-Subscription-Region": LOCATION,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }

    # Request translation
    body = [{"text": original_text}]
    response = requests.post(constructed_url, headers=headers, json=body)

    # Extract translated text
    translated_text = response.json()[0]["translations"][0]["text"]

    # Render index.html with the translation result
    return render_template(
        "index.html",
        original_text=original_text,
        translated_text=translated_text,
        target_language=target_language,
    )

if __name__ == "__main__":
    app.run(debug=True, port=1000)

