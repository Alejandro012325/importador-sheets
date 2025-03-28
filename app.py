import os
import tempfile
import pandas as pd
from flask import Flask, request, jsonify, render_template_string
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)

# --- Configuración de la API de Google Sheets ---
SERVICE_ACCOUNT_FILE = 'service_account.json'  # Si decides incluirlo; de lo contrario, lo montas como secreto.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1wTtwIfw_t30_DN6oKwhPwAul_EI_DNAWDMJk_q73wtA'
RANGE_NAME = 'Consolidado!B2'

# Crea las credenciales y el servicio.
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

@app.route('/', methods=['GET'])
def home():
    return render_template_string("<h2>Servicio de Importación Activo</h2>")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No se encontró el archivo en la solicitud."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No se seleccionó ningún archivo."}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        df = pd.read_excel(tmp_path, engine='openpyxl')
        df = df.iloc[:, :49]
        df = df.fillna('')
        data = df.iloc[1:].values.tolist()

        body = {'values': data}
        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            body=body
        ).execute()

        os.remove(tmp_path)
        return jsonify({"success": True, "message": f"Reporte importado correctamente. {result.get('updatedCells')} celdas actualizadas."})
    except Exception as e:
        os.remove(tmp_path)
        return jsonify({"success": False, "message": f"Ocurrió un error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
