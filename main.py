from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)

# Autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_data = json.loads(os.environ['GOOGLE_CREDS_JSON'])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_data, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1Ezm-sc-fbrtY5erE4NCyZKIyu_H6FP_BerxDUdzm-r4").sheet1

@app.route("/", methods=["GET"])
def index():
    return "<h1>API de formulario de ventas funcionando</h1>"

@app.route("/submit", methods=["POST"])
def guardar_ventas():
    try:
        data = request.get_json()
        filas = data.get("filas", [])

        if not filas:
            return jsonify({"error": "No se recibieron filas válidas."}), 400

        for fila in filas:
            sheet.append_row(fila)

        return jsonify({"mensaje": "Datos guardados correctamente."})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
