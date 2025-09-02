"""
Servicio principal para procesar y enviar datos de vehículos a ATIONET
"""
import logging
import time
from typing import Dict, List, Tuple
from ationet_service import ATIONETService
from csv_processor import CSVProcessor
from config import Config

logger = logging.getLogger(__name__)

class VehicleDataProcessor:
    """Procesador principal para datos de vehículos"""
    
    def __init__(self):
        self.ationet_service = ATIONETService()
        self.csv_processor = CSVProcessor()
        self.batch_size = Config.BATCH_SIZE
    
    def process_all_vehicles(self) -> Dict:
        """
        Procesa todos los vehículos del CSV y los envía a ATIONET
        
        Returns:
            Dict: Resumen del procesamiento
        """
        logger.info("Iniciando procesamiento de vehículos")
        
        start_time = time.time()
        summary = {
            "total_records": 0,
            "processed_successfully": 0,
            "failed_records": 0,
            "skipped_duplicates": 0,
            "errors": [],
            "processing_time_seconds": 0
        }
        
        try:
            # Obtener registros sin procesar
            unprocessed_records = self.csv_processor.get_unprocessed_records()
            summary["total_records"] = len(unprocessed_records)
            
            if not unprocessed_records:
                logger.info("No hay registros nuevos para procesar")
                return summary
            
            logger.info(f"Procesando {len(unprocessed_records)} registros en lotes de {self.batch_size}")
            
            # Procesar en lotes
            for i in range(0, len(unprocessed_records), self.batch_size):
                batch = unprocessed_records[i:i + self.batch_size]
                batch_number = (i // self.batch_size) + 1
                total_batches = (len(unprocessed_records) + self.batch_size - 1) // self.batch_size
                
                logger.info(f"Procesando lote {batch_number}/{total_batches} ({len(batch)} registros)")
                
                batch_summary = self._process_batch(batch)
                
                # Actualizar resumen
                summary["processed_successfully"] += batch_summary["processed_successfully"]
                summary["failed_records"] += batch_summary["failed_records"]
                summary["skipped_duplicates"] += batch_summary["skipped_duplicates"]
                summary["errors"].extend(batch_summary["errors"])
                
                # Pausa pequeña entre lotes para no sobrecargar la API
                if i + self.batch_size < len(unprocessed_records):
                    time.sleep(1)
            
            summary["processing_time_seconds"] = round(time.time() - start_time, 2)
            
            logger.info(f"Procesamiento completado en {summary['processing_time_seconds']} segundos")
            logger.info(f"Exitosos: {summary['processed_successfully']}, "
                       f"Fallidos: {summary['failed_records']}, "
                       f"Duplicados: {summary['skipped_duplicates']}")
            
            return summary
            
        except Exception as e:
            error_msg = f"Error en procesamiento general: {str(e)}"
            logger.error(error_msg)
            summary["errors"].append(error_msg)
            summary["processing_time_seconds"] = round(time.time() - start_time, 2)
            return summary
    
    def _process_batch(self, batch: List[Tuple[str, Dict]]) -> Dict:
        """
        Procesa un lote de registros
        
        Args:
            batch: Lista de tuplas (record_id, record_data)
            
        Returns:
            Dict: Resumen del lote procesado
        """
        batch_summary = {
            "processed_successfully": 0,
            "failed_records": 0,
            "skipped_duplicates": 0,
            "errors": []
        }
        
        for record_id, record_data in batch:
            try:
                # Formatear datos para ATIONET
                formatted_data = self.ationet_service.format_vehicle_data(record_data)
                
                # Enviar a ATIONET
                success, response, error = self.ationet_service.send_vehicle_data(formatted_data)
                
                if success:
                    # Marcar como procesado
                    self.csv_processor.save_processed_record(record_id, record_data)
                    batch_summary["processed_successfully"] += 1
                    logger.debug(f"Registro {record_id} procesado exitosamente")
                    
                else:
                    # Verificar si es un error de duplicado
                    if error and ("duplicate" in error.lower() or "conflict" in error.lower() or "409" in error):
                        batch_summary["skipped_duplicates"] += 1
                        logger.warning(f"Registro {record_id} ya existe (duplicado)")
                        # Aún así lo marcamos como procesado para no intentarlo de nuevo
                        self.csv_processor.save_processed_record(record_id, record_data)
                    else:
                        # Error real
                        batch_summary["failed_records"] += 1
                        error_msg = f"Error procesando {record_id}: {error}"
                        batch_summary["errors"].append(error_msg)
                        logger.error(error_msg)
                        
                        # Guardar en archivo de fallidos
                        self.csv_processor.save_failed_record(record_id, record_data, error or "Error desconocido")
                
                # Pausa pequeña entre registros
                time.sleep(0.1)
                
            except Exception as e:
                error_msg = f"Error inesperado procesando {record_id}: {str(e)}"
                batch_summary["errors"].append(error_msg)
                batch_summary["failed_records"] += 1
                logger.error(error_msg)
                
                # Guardar en archivo de fallidos
                self.csv_processor.save_failed_record(record_id, record_data, str(e))
        
        return batch_summary
    
    def get_processing_status(self) -> Dict:
        """
        Obtiene el estado actual del procesamiento
        
        Returns:
            Dict: Estado del procesamiento
        """
        try:
            # Cargar datos del CSV
            df = self.csv_processor.load_csv_data()
            total_records = len(df)
            
            # Obtener registros procesados
            processed_ids = self.csv_processor.get_processed_records()
            processed_count = len(processed_ids)
            
            # Obtener registros sin procesar
            unprocessed_records = self.csv_processor.get_unprocessed_records()
            pending_count = len(unprocessed_records)
            
            return {
                "total_records": total_records,
                "processed_records": processed_count,
                "pending_records": pending_count,
                "completion_percentage": round((processed_count / total_records * 100), 2) if total_records > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado: {e}")
            return {
                "error": str(e),
                "total_records": 0,
                "processed_records": 0,
                "pending_records": 0,
                "completion_percentage": 0
            }
