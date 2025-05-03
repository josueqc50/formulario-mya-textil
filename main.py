
from flask import Flask, request, render_template_string, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
from datetime import datetime

app = Flask(__name__)

# Autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_data = json.loads(os.environ['GOOGLE_CREDS_JSON'])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_data, scope)
client = gspread.authorize(creds)

# Hojas de cálculo
sheet_ventas = client.open_by_key("1Ezm-sc-fbrtY5erE4NCyZKIyu_H6FP_BerxDUdzm-r4").sheet1
sheet_datos = client.open_by_key("14w5C5rPPUHHzPgQRiVKfRMM97j7qRRqyLB0cACjx56c").worksheet("DATOS")

# Obtener listas desde hoja DATOS
colores = sheet_datos.col_values(1)[1:]
productos = sheet_datos.col_values(2)[1:]
clientes = sheet_datos.col_values(3)[1:]

def construir_options(lista):
    return ''.join([f'<option value="{item}">' for item in lista])

HTML_FORM = """<!doctype html>
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

        function validarFormulario() {
            let cliente = document.getElementById('cliente').value.trim();
            if (!cliente) {
                alert("Por favor ingresa el nombre del cliente.");
                return false;
            }

            let filasValidas = 0;
            for (let i = 1; i <= 30; i++) {
                let color = document.getElementById('color_' + i).value.trim();
                let producto = document.getElementById('producto_' + i).value.trim();
                let partida = document.getElementById('partida_' + i).value.trim();
                let kg = parseFloat(document.getElementById('kg_' + i).value) || 0;
                let precio = parseFloat(document.getElementById('precio_' + i).value) || 0;

                if (color && producto && partida && kg > 0 && precio > 0) {
                    filasValidas++;
                }
            }

            if (filasValidas === 0) {
                alert("Debes ingresar al menos una fila con color, producto, partida, kg y precio válidos.");
                return false;
            }

            return true;
        }
    </script>
</head>
<body>
    <div class="form-wrapper">
    <form id="formulario" action="/submit" method="post" onsubmit="return validarFormulario()">
        <h2>MYA TEXTIL</h2>
        <label>Fecha:
            <input type="date" name="fecha" value="{{ fecha_actual }}" required>
        </label>
        <label>Cliente:
            <input list="clientes" name="cliente" id="cliente" required>
            <datalist id="clientes">{{ opciones_clientes|safe }}</datalist>
        </label>
        <table>
            <thead>
                <tr><th>#</th><th>Color</th><th>Producto</th><th>Partida</th><th>Kg</th><th>Precio Unitario</th><th>Total</th></tr>
            </thead>
            <tbody>
                {% for i in range(1, 31) %}
                <tr>
                    <td>{{ i }}</td>
                    <td><input list="colores" name="color_{{ i }}" id="color_{{ i }}"></td>
                    <td><input list="productos" name="producto_{{ i }}" id="producto_{{ i }}"></td>
                    <td><input type="text" name="partida_{{ i }}" id="partida_{{ i }}"></td>
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
        <label>Vendedor Responsable:
            <input type="text" name="vendedor" required>
        </label>
        <button type="submit">Guardar Venta</button>
    </form>
    </div>
    <datalist id="colores">{{ opciones_colores|safe }}</datalist>
    <datalist id="productos">{{ opciones_productos|safe }}</datalist>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(
        HTML_FORM,
        opciones_colores=construir_options(colores),
        opciones_productos=construir_options(productos),
        opciones_clientes=construir_options(clientes),
        fecha_actual=datetime.now().strftime('%Y-%m-%d')
    )

@app.route('/submit', methods=['POST'])
def submit():
    try:
        fecha = request.form.get('fecha', '').strip()
        cliente = request.form.get('cliente', '').strip()
        vendedor = request.form.get('vendedor', '').strip()

        if not cliente:
            return "<h2>Error: El campo CLIENTE es obligatorio.</h2>", 400

        filas_guardadas = 0
        for i in range(1, 31):
            color = request.form.get(f'color_{i}', '').strip()
            producto = request.form.get(f'producto_{i}', '').strip()
            partida = request.form.get(f'partida_{i}', '').strip()
            kg = request.form.get(f'kg_{i}', '0').strip()
            precio = request.form.get(f'precio_{i}', '0').strip()
            total = request.form.get(f'total_{i}', '0').strip()

            if all([color, producto, partida]) and float(kg) > 0 and float(precio) > 0:
                sheet_ventas.append_row([
                    fecha, cliente, color, producto, partida,
                    float(kg), float(precio), float(total), vendedor
                ])
                filas_guardadas += 1

        if filas_guardadas == 0:
            return "<h2>Error: Debes ingresar al menos una fila con datos completos.</h2>", 400

        return redirect('/')
    except Exception as e:
        return f"<h2>Error al guardar la venta</h2><p>{str(e)}</p>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
