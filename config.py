"""
Configuración de la aplicación Flask
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base de la aplicación"""
    
    # ATIONET API Configuration
    ATIONET_BASE_URL = "https://api-beta.ationet.com"
    ATIONET_ENDPOINT = "/VehiclesClass/"  # Endpoint específico para envío de vehículos
    ATIONET_TOKEN = os.getenv('ATIONET_TOKEN')
    
    # CSV Configuration
    CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), 'clases_vehiculos.csv')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Request Configuration
    REQUEST_TIMEOUT = 30
    REQUEST_RETRIES = 3
    BATCH_SIZE = 10  # Número de registros a procesar por lote
