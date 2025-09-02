"""
Servicio para interactuar con la API de ATIONET
"""
import requests
import json
import logging
import time
from typing import Dict, List, Optional, Tuple
from config import Config

logger = logging.getLogger(__name__)

class ATIONETService:
    """Servicio para interactuar con la API de ATIONET"""
    
    def __init__(self):
        self.base_url = Config.ATIONET_BASE_URL
        self.endpoint = Config.ATIONET_ENDPOINT
        self.token = Config.ATIONET_TOKEN
        self.timeout = Config.REQUEST_TIMEOUT
        self.retries = Config.REQUEST_RETRIES
        
        if not self.token:
            raise ValueError("ATIONET_TOKEN no encontrado en las variables de entorno")
        
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def send_vehicle_data(self, vehicle_data: Dict) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Envía datos de vehículo a ATIONET
        
        Args:
            vehicle_data: Diccionario con los datos del vehículo
            
        Returns:
            Tuple[bool, Optional[Dict], Optional[str]]: (éxito, respuesta, error)
        """
        url = f"{self.base_url}{self.endpoint}"
        
        for attempt in range(self.retries):
            try:
                logger.info(f"Enviando datos a ATIONET (intento {attempt + 1}/{self.retries})")
                logger.debug(f"Datos: {json.dumps(vehicle_data, indent=2)}")
                
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=vehicle_data,
                    timeout=self.timeout
                )
                
                # Log de la respuesta
                logger.debug(f"Status Code: {response.status_code}")
                logger.debug(f"Response: {response.text}")
                
                if response.status_code == 200 or response.status_code == 201:
                    try:
                        response_data = response.json()
                        logger.info("Datos enviados exitosamente")
                        return True, response_data, None
                    except json.JSONDecodeError:
                        logger.info("Datos enviados exitosamente (respuesta sin JSON)")
                        return True, {"status": "success"}, None
                        
                elif response.status_code == 409:
                    # Conflicto - posiblemente datos duplicados
                    error_msg = f"Datos duplicados o conflicto: {response.text}"
                    logger.warning(error_msg)
                    return False, None, error_msg
                    
                elif response.status_code >= 400:
                    error_msg = f"Error del cliente ({response.status_code}): {response.text}"
                    logger.error(error_msg)
                    return False, None, error_msg
                    
                else:
                    error_msg = f"Error del servidor ({response.status_code}): {response.text}"
                    logger.error(error_msg)
                    if attempt < self.retries - 1:
                        wait_time = 2 ** attempt  # Backoff exponencial
                        logger.info(f"Reintentando en {wait_time} segundos...")
                        time.sleep(wait_time)
                        continue
                    return False, None, error_msg
                    
            except requests.exceptions.Timeout:
                error_msg = f"Timeout en intento {attempt + 1}"
                logger.error(error_msg)
                if attempt < self.retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return False, None, "Timeout después de múltiples intentos"
                
            except requests.exceptions.ConnectionError:
                error_msg = f"Error de conexión en intento {attempt + 1}"
                logger.error(error_msg)
                if attempt < self.retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return False, None, "Error de conexión después de múltiples intentos"
                
            except Exception as e:
                error_msg = f"Error inesperado: {str(e)}"
                logger.error(error_msg)
                return False, None, error_msg
        
        return False, None, "Error después de múltiples intentos"
    
    def format_vehicle_data(self, row_data: Dict) -> Dict:
        """
        Formatea los datos del CSV al formato requerido por ATIONET
        
        Args:
            row_data: Datos de una fila del CSV
            
        Returns:
            Dict: Datos formateados para ATIONET
        """
        try:
            formatted_data = {
                "IdVehicleType": row_data['IdVehicleType'],
                "Brand": row_data['Brand'],
                "Model": row_data['Model'],
                "TheoricalConsumption": float(row_data['TheoricalConsumption']),
                "IdCompany": row_data['IdCompany'],
                "VehiclesClassesFuelsMaster": [
                    {
                        "IdFuelMaster": row_data['IdFuelMaster'],
                        "VolumeLimit": float(row_data['VolumeLimit'])
                    }
                ]
            }
            return formatted_data
        except (KeyError, ValueError) as e:
            logger.error(f"Error formateando datos: {e}")
            raise ValueError(f"Error formateando datos de la fila: {e}")
