from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import re

app = Flask(__name__)
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
        wyniki = []

        with open(input_path, 'r', encoding='utf-8') as infile:
            content = infile.read()

            # Sprawdź, czy dane są w formacie JSON
            try:
                data = json.loads(content)
                if isinstance(data, list):  # Dane jako lista JSON
                    for item in data:
                        if isinstance(item, dict):
                            email = item.get('email', 'Brak')
                            password = item.get('password', 'Brak')
                            wyniki.append(f"{email};{password}")
            except json.JSONDecodeError:
                # Dane w formacie tekstowym
                for line in content.splitlines():
                    line = line.strip()
                    if "login:" in line.lower():
                        email_match = re.search(r'login:\s*(\S+@\S+)', line, re.IGNORECASE)
                        if email_match:
                            email = email_match.group(1)
                            wyniki.append(f"{email};Brak")
                    if "pass:" in line.lower():
                        pass_match = re.search(r'pass:\s*(\S+)', line, re.IGNORECASE)
                        if pass_match:
                            password = pass_match.group(1)
                            if wyniki and "Brak" in wyniki[-1]:
                                wyniki[-1] = wyniki[-1].replace("Brak", password)
                            else:
                                wyniki.append(f"Brak;{password}")

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
