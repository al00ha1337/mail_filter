from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)

# Konfiguracja CORS, aby zezwolić na żądania z konkretnego origin
CORS(app, resources={r"/*": {"origins": "https://al00ha1337.github.io"}})

@app.route('/')
def home():
    return "Aplikacja działa! Użyj endpointu /upload, aby przesłać plik.", 200

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nie przesłano pliku"}), 400
    file = request.files['file']
    # Przetwarzanie pliku tutaj
    return jsonify({"message": "Plik przesłany poprawnie!"})
import os
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def filtruj_maile(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            content = infile.read()

        result = []
        wyniki = []

        # Parsowanie JSON
        while content:
            try:
                data, index = json.JSONDecoder().raw_decode(content)
                result.append(data)
                content = content[index:].strip()
            except json.JSONDecodeError:
                break

        # Wyciąganie emaili i haseł
        for item in result:
            if isinstance(item, dict):
                email = item.get('email', 'Brak')
                password = item.get('password', 'Brak')
                wyniki.append(f"{email};{password}")
            elif isinstance(item, list):
                for sub_item in item:
                    if isinstance(sub_item, dict):
                        email = sub_item.get('email', 'Brak')
                        password = sub_item.get('password', 'Brak')
                        wyniki.append(f"{email};{password}")

        # Zapis wyników do pliku tekstowego
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write('\n'.join(wyniki))

        return len(wyniki)
    except Exception as e:
        return str(e)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nie przesłano pliku"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nazwa pliku jest pusta"}), 400

    if file:
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        output_path = os.path.join(PROCESSED_FOLDER, f"processed_{file.filename}")
        file.save(input_path)

        # Przetwarzanie pliku
        processed_count = filtruj_maile(input_path, output_path)
        if isinstance(processed_count, str):  # Jeśli zwróci błąd
            return jsonify({"error": processed_count}), 500

        return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
