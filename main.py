from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)
CORS(app)

# Autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_data = json.loads(os.environ['GOOGLE_CREDS_JSON'])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_data, scope)
client = gspread.authorize(creds)

# Cambiar de sheet1 a la hoja llamada "proformas"
sheet = client.open_by_key("1Ezm-sc-fbrtY5erE4NCyZKIyu_H6FP_BerxDUdzm-r4").worksheet("proformas")
datos_sheet = client.open_by_key("14w5C5rPPUHHzPgQRiVKfRMM97j7qRRqyLB0cACjx56c").worksheet("DATOS")

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

        proximo = obtener_siguiente_numero()

        for fila in filas:
            fila_con_numero = [proximo] + fila
            sheet.append_row(fila_con_numero)

        return jsonify({"mensaje": "Datos guardados correctamente."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/proximo-numero", methods=["GET"])
def proximo_numero():
    try:
        return jsonify({"numero": obtener_siguiente_numero()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/opciones", methods=["GET"])
def obtener_opciones():
    try:
        colores = datos_sheet.col_values(1)[1:]
        productos = datos_sheet.col_values(2)[1:]
        clientes = datos_sheet.col_values(3)[1:]

        return jsonify({
            "colores": colores,
            "productos": productos,
            "clientes": clientes
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def obtener_siguiente_numero():
    registros = sheet.get_all_values()
    numeros = [int(fila[0]) for fila in registros[1:] if fila[0].isdigit()]
    return str(max(numeros) + 1) if numeros else "1"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
