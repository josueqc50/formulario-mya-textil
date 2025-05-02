from flask import Flask, request, render_template_string, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

app = Flask(__name__)

# Autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_data = json.loads(os.environ['GOOGLE_CREDS_JSON'])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_data, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1Ezm-sc-fbrtY5erE4NCyZKIyu_H6FP_BerxDUdzm-r4").sheet1

# HTML con JS y autocompletado desde Google Sheets
HTML_FORM = """
<!doctype html>
<html>
<head>
    <title>Formulario de Ventas - MYA TEXTIL</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }
        .form-wrapper { background: white; padding: 20px; border-radius: 8px; max-width: 1000px; margin: auto; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ccc; padding: 6px; text-align: center; }
        input { width: 100%; box-sizing: border-box; padding: 4px; }
        button { margin-top: 10px; padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .total-row td { font-weight: bold; }
    </style>
    <script>
        function calcularTotales() {
            let totalGeneral = 0;
            for (let i = 1; i <= 30; i++) {
                let kg = parseFloat(document.getElementById('kg_' + i).value) || 0;
                let precio = parseFloat(document.getElementById('precio_' + i).value) || 0;
                let total = kg * precio;
                document.getElementById('total_' + i).value = total.toFixed(2);
                totalGeneral += total;
            }
            document.getElementById('total_general').innerText = totalGeneral.toFixed(2);
        }
    </script>
</head>
<body>
    <div class="form-wrapper">
    <form action="/submit" method="post">
        <h2>MYA TEXTIL</h2>
        <label>Fecha: <input type="date" name="fecha" required></label>
        <label>Cliente: <input type="text" name="cliente" list="clientes" required></label>
        <datalist id="clientes">
            <option value="Cliente A"><option value="Cliente B"><option value="Cliente C">
        </datalist>
        <table>
            <thead>
                <tr><th>#</th><th>Color</th><th>Producto</th><th>Partida</th><th>Kg</th><th>Precio Unitario</th><th>Total</th></tr>
            </thead>
            <tbody>
                {% for i in range(1, 31) %}
                <tr>
                    <td>{{ i }}</td>
                    <td><input type="text" name="color_{{ i }}"></td>
                    <td><input type="text" name="producto_{{ i }}" list="productos"></td>
                    <td><input type="text" name="partida_{{ i }}"></td>
                    <td><input type="number" name="kg_{{ i }}" id="kg_{{ i }}" step="0.01" oninput="calcularTotales()"></td>
                    <td><input type="number" name="precio_{{ i }}" id="precio_{{ i }}" step="0.01" oninput="calcularTotales()"></td>
                    <td><input type="number" name="total_{{ i }}" id="total_{{ i }}" readonly></td>
                </tr>
                {% endfor %}
            </tbody>
            <tfoot>
                <tr class="total-row"><td colspan="6">TOTAL GENERAL</td><td id="total_general">0.00</td></tr>
            </tfoot>
        </table>
        <label>Vendedor Responsable: <input type="text" name="vendedor" required></label>
        <button type="submit">Guardar Venta</button>
    </form>
    </div>
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
    vendedor = request.form['vendedor']
    for i in range(1, 31):
        color = request.form.get(f'color_{i}', '')
        producto = request.form.get(f'producto_{i}', '')
        partida = request.form.get(f'partida_{i}', '')
        kg = request.form.get(f'kg_{i}', '')
        precio = request.form.get(f'precio_{i}', '')
        total = request.form.get(f'total_{i}', '')
        if any([color, producto, partida, kg, precio, total]):
            sheet.append_row([fecha, cliente, color, producto, partida, kg, precio, total, vendedor])
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

Actualizado formulario con 30 líneas y total automático
