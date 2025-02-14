from flask import Flask, render_template, request, send_file
import os
import requests
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import PyPDF2
from docx import Document

load_dotenv()

# Initialize Flask app with custom template folder
app = Flask(__name__, template_folder='views')  # Set template_folder to 'views'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'docx'}

# Azure Translator API Configuration
API_KEY = "3sZFPDTQhTSDp3dEZ0S4s5JOOlsBc5tqB5irQIwZ1FpNwz4KwksIJQQJ99BAACGhslBXJ3w3AAAbACOGlPPt"
ENDPOINT = "https://muthu.cognitiveservices.azure.com/translator/text/v3.0"
LOCATION = "global"  # e.g., "eastus"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text(filepath):
    ext = filepath.rsplit('.', 1)[1].lower()
    text = ""
    
    if ext == 'txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    elif ext == 'pdf':
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
    elif ext == 'docx':
        doc = Document(filepath)
        for para in doc.paragraphs:
            text += para.text + '\n'
    return text

def translate_text(text, target_lang='es'):
    url = f"{ENDPOINT}/translate"
    headers = {
        'Ocp-Apim-Subscription-Key': API_KEY,
        'Ocp-Apim-Subscription-Region': LOCATION,
        'Content-Type': 'application/json',
    }
    params = {
        'api-version': '3.0',
        'to': target_lang
    }
    body = [{'text': text}]
    
    response = requests.post(url, headers=headers, params=params, json=body)
    response.raise_for_status()
    return response.json()[0]['translations'][0]['text']

@app.route('/', methods=['GET', 'POST'])
def sample():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file uploaded!", 400
        
        file = request.files['file']
        target_lang = request.form.get('target_lang', 'es')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            
            # Extract text from the document
            text = extract_text(upload_path)
            
            # Translate the text
            translated_text = translate_text(text, target_lang)
            
            # Save translated text to a temporary file
            output_filename = f"translated_{filename.split('.')[0]}.txt"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translated_text)
            
            # Cleanup original file
            os.remove(upload_path)
            
            return send_file(output_path, as_attachment=True)
    
    return render_template('sample.html')  # Flask will now look in the 'views' folder

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)