from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json

app = Flask(__name__)

# Konfiguracja CORS, aby zezwolić na żądania z GitHub Pages
CORS(app, supports_credentials=True, origins=["https://al00ha1337.github.io"])

@app.route('/')
def home():
    return "Aplikacja działa! Użyj endpointu /upload, aby przesłać plik.", 200

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Sprawdź, czy plik jest w żądaniu
        if 'file' not in request.files:
            return jsonify({"error": "Nie przesłano pliku"}), 400

        file = request.files['file']

        # Zapisanie przesłanego pliku
        input_path = f"/tmp/{file.filename}"
        file.save(input_path)

        # Przetwarzanie pliku
        output_path = f"/tmp/processed_{file.filename}"
        with open(input_path, 'r', encoding='utf-8') as infile:
            content = infile.read()

        result = []
        while content:
            try:
                data, index = json.JSONDecoder().raw_decode(content)
                result.append(data)
                content = content[index:].strip()
            except json.JSONDecodeError:
                break

        # Wyciąganie emaili i haseł
        wyniki = []
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

        # Zapis wyników do pliku
        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.write('\n'.join(wyniki))

        # Zwróć plik wynikowy
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        # Obsługa błędów
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
