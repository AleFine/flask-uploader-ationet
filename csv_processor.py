"""
Servicio para procesar datos CSV
"""
import pandas as pd
import json
import logging
from typing import List, Dict, Tuple
from pathlib import Path
from config import Config

logger = logging.getLogger(__name__)

class CSVProcessor:
    """Procesador de archivos CSV para datos de vehículos"""
    
    def __init__(self, csv_path: str = None):
        self.csv_path = csv_path or Config.CSV_FILE_PATH
        self.processed_file = self.csv_path.replace('.csv', '_processed.json')
        self.failed_file = self.csv_path.replace('.csv', '_failed.json')
        
    def load_csv_data(self) -> pd.DataFrame:
        """
        Carga los datos del archivo CSV
        
        Returns:
            pd.DataFrame: DataFrame con los datos del CSV
        """
        try:
            if not Path(self.csv_path).exists():
                raise FileNotFoundError(f"Archivo CSV no encontrado: {self.csv_path}")
            
            df = pd.read_csv(self.csv_path)
            logger.info(f"CSV cargado exitosamente. Filas: {len(df)}")
            
            # Validar columnas requeridas
            required_columns = [
                'IdVehicleType', 'Brand', 'Model', 'TheoricalConsumption',
                'IdCompany', 'IdFuelMaster', 'VolumeLimit'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Columnas faltantes en el CSV: {missing_columns}")
            
            # Limpiar datos
            df = df.dropna(subset=required_columns)
            logger.info(f"Filas válidas después de limpieza: {len(df)}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error cargando CSV: {e}")
            raise
    
    def get_processed_records(self) -> List[str]:
        """
        Obtiene la lista de registros ya procesados
        
        Returns:
            List[str]: Lista de IDs de registros procesados
        """
        try:
            if Path(self.processed_file).exists():
                with open(self.processed_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('processed_ids', [])
            return []
        except Exception as e:
            logger.warning(f"Error leyendo archivo de procesados: {e}")
            return []
    
    def save_processed_record(self, record_id: str, record_data: Dict):
        """
        Guarda un registro como procesado
        
        Args:
            record_id: ID único del registro
            record_data: Datos del registro procesado
        """
        try:
            processed_data = {"processed_ids": [], "records": []}
            
            if Path(self.processed_file).exists():
                with open(self.processed_file, 'r', encoding='utf-8') as f:
                    processed_data = json.load(f)
            
            if record_id not in processed_data["processed_ids"]:
                processed_data["processed_ids"].append(record_id)
                processed_data["records"].append({
                    "id": record_id,
                    "data": record_data,
                    "processed_at": pd.Timestamp.now().isoformat()
                })
            
            with open(self.processed_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error guardando registro procesado: {e}")
    
    def save_failed_record(self, record_id: str, record_data: Dict, error_message: str):
        """
        Guarda un registro que falló en el procesamiento
        
        Args:
            record_id: ID único del registro
            record_data: Datos del registro que falló
            error_message: Mensaje de error
        """
        try:
            failed_data = {"failed_records": []}
            
            if Path(self.failed_file).exists():
                with open(self.failed_file, 'r', encoding='utf-8') as f:
                    failed_data = json.load(f)
            
            failed_data["failed_records"].append({
                "id": record_id,
                "data": record_data,
                "error": error_message,
                "failed_at": pd.Timestamp.now().isoformat()
            })
            
            with open(self.failed_file, 'w', encoding='utf-8') as f:
                json.dump(failed_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error guardando registro fallido: {e}")
    
    def create_record_id(self, row: pd.Series) -> str:
        """
        Crea un ID único para el registro basado en sus datos
        
        Args:
            row: Fila del DataFrame
            
        Returns:
            str: ID único del registro
        """
        # Crear un ID único basado en los campos clave
        key_fields = [
            str(row['IdVehicleType']),
            str(row['Brand']).strip().upper(),
            str(row['Model']).strip().upper(),
            str(row['IdCompany']),
            str(row['IdFuelMaster'])
        ]
        return "_".join(key_fields)
    
    def get_unprocessed_records(self) -> List[Tuple[str, Dict]]:
        """
        Obtiene los registros que aún no han sido procesados
        
        Returns:
            List[Tuple[str, Dict]]: Lista de tuplas (record_id, record_data)
        """
        try:
            df = self.load_csv_data()
            processed_ids = self.get_processed_records()
            
            unprocessed_records = []
            
            for _, row in df.iterrows():
                record_id = self.create_record_id(row)
                
                if record_id not in processed_ids:
                    record_data = row.to_dict()
                    unprocessed_records.append((record_id, record_data))
            
            logger.info(f"Registros sin procesar: {len(unprocessed_records)}")
            return unprocessed_records
            
        except Exception as e:
            logger.error(f"Error obteniendo registros sin procesar: {e}")
            raise
