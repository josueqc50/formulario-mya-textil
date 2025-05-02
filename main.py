from flask import Flask, request, render_template_string, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Configurar Flask
app = Flask(__name__)

# Autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import os, json
creds_data = json.loads(os.environ['GOOGLE_CREDS_JSON'])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_data, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1Ezm-sc-fbrtY5erE4NCyZKIyu_H6FP_BerxDUdzm-r4").sheet1

# HTML con logo y formulario personalizado
HTML_FORM = """
<!doctype html>
<html>
<head>
    <title>Formulario de Ventas - MYA TEXTIL</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f8f8f8; padding: 20px; }
        form { background: white; padding: 20px; border-radius: 8px; max-width: 600px; margin: auto; }
        input, select, textarea { width: 100%; padding: 8px; margin: 8px 0; border: 1px solid #ccc; border-radius: 4px; }
        button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
        img.logo { max-width: 150px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <form action="/submit" method="post">
        <img src="https://i.imgur.com/AbB7k2L.png" alt="MYA TEXTIL Logo" class="logo">
        <label>Fecha:</label>
        <input type="date" name="fecha" required>

        <label>Nombre del Cliente:</label>
        <input type="text" name="cliente" required>

        <label>Producto:</label>
        <input type="text" name="producto" required>

        <label>Cantidad:</label>
        <input type="number" name="cantidad" required>

        <label>Precio Unitario:</label>
        <input type="number" name="precio" step="0.01" required>

        <label>Vendedor Responsable:</label>
        <input type="text" name="vendedor" required>

        <label>Observaciones:</label>
        <textarea name="observaciones"></textarea>

        <button type="submit">Guardar Venta</button>
    </form>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    fecha = request.form['fecha']
    cliente = request.form['cliente']
    producto = request.form['producto']
    cantidad = int(request.form['cantidad'])
    precio = float(request.form['precio'])
    total = cantidad * precio
    vendedor = request.form['vendedor']
    observaciones = request.form['observaciones']

    # Guardar en Google Sheet
    sheet.append_row([fecha, cliente, producto, cantidad, precio, total, vendedor, observaciones])

    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
