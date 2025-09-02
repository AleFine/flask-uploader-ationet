"""
Aplicación Flask para procesar y enviar datos de vehículos a ATIONET
"""
from flask import Flask, jsonify, request, render_template_string
import logging
import os
from datetime import datetime
from vehicle_processor import VehicleDataProcessor
from config import Config

# Configurar logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ationet_processor.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Template HTML simple para la interfaz
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ATIONET Vehicle Processor</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .status-card { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .btn { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #0056b3; }
        .btn:disabled { background: #ccc; cursor: not-allowed; }
        .success { color: #28a745; }
        .error { color: #dc3545; }
        .warning { color: #ffc107; }
        .progress { width: 100%; background: #e9ecef; border-radius: 4px; margin: 10px 0; }
        .progress-bar { height: 20px; background: #28a745; border-radius: 4px; transition: width 0.3s; }
        .log-area { background: #f8f9fa; padding: 15px; border-radius: 4px; max-height: 300px; overflow-y: auto; font-family: monospace; font-size: 12px; }
        #processing { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚗 ATIONET Vehicle Data Processor</h1>
        
        <div class="status-card">
            <h3>Estado del Procesamiento</h3>
            <div id="status-info">
                <p>Cargando estado...</p>
            </div>
        </div>
        
        <div class="status-card">
            <h3>Acciones</h3>
            <button class="btn" onclick="refreshStatus()">🔄 Actualizar Estado</button>
            <button class="btn" onclick="startProcessing()" id="process-btn">🚀 Procesar Vehículos</button>
            <button class="btn" onclick="viewLogs()">📋 Ver Logs</button>
        </div>
        
        <div id="processing" class="status-card">
            <h3>⏳ Procesando...</h3>
            <p>El procesamiento está en curso. Por favor espere...</p>
            <div class="progress">
                <div class="progress-bar" style="width: 0%" id="progress-bar"></div>
            </div>
        </div>
        
        <div class="status-card">
            <h3>Resultado del Último Procesamiento</h3>
            <div id="result-info">
                <p>No hay resultados disponibles</p>
            </div>
        </div>
        
        <div class="status-card">
            <h3>Logs del Sistema</h3>
            <div id="logs" class="log-area">
                <p>Los logs aparecerán aquí...</p>
            </div>
        </div>
    </div>
    
    <script>
        function refreshStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    updateStatusDisplay(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('status-info').innerHTML = '<p class="error">Error obteniendo estado</p>';
                });
        }
        
        function updateStatusDisplay(data) {
            const statusDiv = document.getElementById('status-info');
            if (data.error) {
                statusDiv.innerHTML = `<p class="error">Error: ${data.error}</p>`;
                return;
            }
            
            statusDiv.innerHTML = `
                <p><strong>Total de registros:</strong> ${data.total_records}</p>
                <p><strong>Procesados:</strong> <span class="success">${data.processed_records}</span></p>
                <p><strong>Pendientes:</strong> <span class="warning">${data.pending_records}</span></p>
                <p><strong>Progreso:</strong> ${data.completion_percentage}%</p>
                <div class="progress">
                    <div class="progress-bar" style="width: ${data.completion_percentage}%"></div>
                </div>
            `;
        }
        
        function startProcessing() {
            const btn = document.getElementById('process-btn');
            const processingDiv = document.getElementById('processing');
            
            btn.disabled = true;
            btn.textContent = '⏳ Procesando...';
            processingDiv.style.display = 'block';
            
            fetch('/api/process', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    updateResultDisplay(data);
                    refreshStatus();
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('result-info').innerHTML = '<p class="error">Error durante el procesamiento</p>';
                })
                .finally(() => {
                    btn.disabled = false;
                    btn.textContent = '🚀 Procesar Vehículos';
                    processingDiv.style.display = 'none';
                });
        }
        
        function updateResultDisplay(data) {
            const resultDiv = document.getElementById('result-info');
            resultDiv.innerHTML = `
                <p><strong>Tiempo de procesamiento:</strong> ${data.processing_time_seconds} segundos</p>
                <p><strong>Exitosos:</strong> <span class="success">${data.processed_successfully}</span></p>
                <p><strong>Fallidos:</strong> <span class="error">${data.failed_records}</span></p>
                <p><strong>Duplicados:</strong> <span class="warning">${data.skipped_duplicates}</span></p>
                <p><strong>Total procesados:</strong> ${data.total_records}</p>
                ${data.errors.length > 0 ? `<p class="error"><strong>Errores:</strong><br>${data.errors.join('<br>')}</p>` : ''}
            `;
        }
        
        function viewLogs() {
            fetch('/api/logs')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('logs').innerHTML = data.logs.map(log => `<div>${log}</div>`).join('');
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('logs').innerHTML = '<p class="error">Error cargando logs</p>';
                });
        }
        
        // Cargar estado inicial
        refreshStatus();
        
        // Auto-refresh cada 30 segundos
        setInterval(refreshStatus, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Página principal con interfaz de usuario"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def get_status():
    """Obtiene el estado actual del procesamiento"""
    try:
        processor = VehicleDataProcessor()
        status = processor.get_processing_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_vehicles():
    """Inicia el procesamiento de todos los vehículos"""
    try:
        logger.info("Iniciando procesamiento de vehículos desde API")
        processor = VehicleDataProcessor()
        result = processor.process_all_vehicles()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error en procesamiento: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs')
def get_logs():
    """Obtiene los últimos logs del sistema"""
    try:
        log_file = 'ationet_processor.log'
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Obtener las últimas 50 líneas
                logs = [line.strip() for line in lines[-50:] if line.strip()]
        
        return jsonify({"logs": logs})
    except Exception as e:
        logger.error(f"Error obteniendo logs: {e}")
        return jsonify({"logs": [f"Error cargando logs: {e}"]})

@app.route('/api/test-connection')
def test_connection():
    """Prueba la conexión con ATIONET"""
    try:
        from ationet_service import ATIONETService
        service = ATIONETService()
        
        # Crear datos de prueba
        test_data = {
            "IdVehicleType": "test-id",
            "Brand": "TEST",
            "Model": "TEST",
            "TheoricalConsumption": 10.0,
            "IdCompany": "test-company-id",
            "VehiclesClassesFuelsMaster": [
                {
                    "IdFuelMaster": "test-fuel-id",
                    "VolumeLimit": 50.0
                }
            ]
        }
        
        # Intentar enviar (esto debería fallar pero nos dará información sobre la conexión)
        success, response, error = service.send_vehicle_data(test_data)
        
        return jsonify({
            "connection_test": True,
            "success": success,
            "response": response,
            "error": error,
            "token_configured": bool(Config.ATIONET_TOKEN)
        })
        
    except Exception as e:
        return jsonify({
            "connection_test": False,
            "error": str(e),
            "token_configured": bool(Config.ATIONET_TOKEN)
        }), 500

if __name__ == '__main__':
    logger.info("Iniciando aplicación ATIONET Vehicle Processor")
    logger.info(f"Token configurado: {'Sí' if Config.ATIONET_TOKEN else 'No'}")
    logger.info(f"Archivo CSV: {Config.CSV_FILE_PATH}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
