# ATIONET Vehicle Data Processor

Una aplicación Flask para procesar y enviar datos de vehículos desde un archivo CSV a la API de ATIONET de forma segura y eficiente.

**Endpoint utilizado**: `https://api-beta.ationet.com/VehiclesClass/`

## 🚀 Características

- **Procesamiento por lotes**: Evita sobrecargar la API procesando en lotes configurables
- **Prevención de duplicados**: Rastrea registros ya procesados para evitar envíos duplicados
- **Reintentos automáticos**: Manejo robusto de errores con reintentos exponenciales
- **Interfaz web**: Panel de control web para monitorear y controlar el procesamiento
- **Logging completo**: Registro detallado de todas las operaciones
- **Validación de datos**: Validación de datos antes del envío
- **Manejo de errores**: Gestión robusta de errores de red y API

## 📋 Requisitos

- Python 3.8+
- Token de API de ATIONET válido
- Archivo CSV con datos de vehículos

## 🛠️ Instalación

1. **Clonar o descargar el proyecto**

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**:
   - Asegúrate de que el archivo `.env` contenga tu token de ATIONET:
   ```
   ATIONET_TOKEN=tu_token_aqui
   ```

4. **Verificar archivo CSV**:
   - Asegúrate de que `clases_vehiculos.csv` esté en el directorio raíz
   - El archivo debe contener las columnas requeridas

## 🎯 Uso

### Iniciar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

### Interfaz Web

1. **Página Principal**: Accede a `http://localhost:5000`
2. **Estado del Procesamiento**: Monitorea cuántos registros han sido procesados
3. **Procesar Vehículos**: Inicia el procesamiento de datos pendientes
4. **Ver Logs**: Revisa los logs del sistema en tiempo real

### API Endpoints

- `GET /api/status` - Obtiene el estado actual del procesamiento
- `POST /api/process` - Inicia el procesamiento de vehículos
- `GET /api/logs` - Obtiene los logs del sistema
- `GET /api/test-connection` - Prueba la conexión con ATIONET

## 📊 Formato del CSV

El archivo `clases_vehiculos.csv` debe contener las siguientes columnas:

```csv
IdVehicleType,Brand,Model,TheoricalConsumption,IdCompany,IdFuelMaster,VolumeLimit,Description
```

**Ejemplo**:
```csv
d75446d0-c106-40e6-a995-a3fd1d801a47,FIAT,MOBI,18,7c6fda73-9474-4828-afac-efbb861a7eae,91a7b229-1ad0-479f-9984-7c7e2878822c,10.57,Premium Diesel
```

## 🔧 Configuración

### Archivo `config.py`

Puedes modificar la configuración en `config.py`:

```python
class Config:
    ATIONET_BASE_URL = "https://api-beta.ationet.com"
    REQUEST_TIMEOUT = 30
    REQUEST_RETRIES = 3
    BATCH_SIZE = 10  # Registros por lote
```

### Variables de Entorno

- `ATIONET_TOKEN`: Token de autenticación para la API de ATIONET
- `LOG_LEVEL`: Nivel de logging (DEBUG, INFO, WARNING, ERROR)

## 📁 Estructura del Proyecto

```
FlaskProject/
├── app.py                    # Aplicación principal Flask
├── config.py                 # Configuración de la aplicación
├── ationet_service.py        # Servicio para interactuar con ATIONET API
├── csv_processor.py          # Procesador de archivos CSV
├── vehicle_processor.py      # Procesador principal de vehículos
├── clases_vehiculos.csv      # Datos de vehículos a procesar
├── .env                      # Variables de entorno
├── requirements.txt          # Dependencias de Python
└── README.md                 # Este archivo
```

## 🛡️ Prevención de Duplicados

El sistema implementa múltiples mecanismos para prevenir duplicados:

1. **ID único por registro**: Se genera un ID único basado en campos clave
2. **Archivo de procesados**: Se mantiene un registro de IDs ya procesados
3. **Validación antes del envío**: Se verifica si un registro ya fue procesado
4. **Manejo de respuestas 409**: Se detectan y manejan errores de conflicto de la API

## 📊 Monitoreo y Logs

### Archivos de seguimiento generados:

- `ationet_processor.log` - Log principal de la aplicación
- `clases_vehiculos_processed.json` - Registros procesados exitosamente
- `clases_vehiculos_failed.json` - Registros que fallaron en el procesamiento

### Información en los logs:

- Inicio y fin de procesamiento
- Detalles de cada envío a la API
- Errores y reintentos
- Estadísticas de procesamiento

## 🚨 Manejo de Errores

El sistema maneja varios tipos de errores:

1. **Errores de red**: Reintentos automáticos con backoff exponencial
2. **Errores de API**: Clasificación y manejo específico según código de respuesta
3. **Datos inválidos**: Validación y logging de datos mal formateados
4. **Duplicados**: Detección y omisión de registros ya procesados

## 🔍 Solución de Problemas

### Error: "ATIONET_TOKEN no encontrado"
- Verifica que el archivo `.env` exista y contenga el token
- Asegúrate de que la variable se llame exactamente `ATIONET_TOKEN`

### Error: "Archivo CSV no encontrado"
- Verifica que `clases_vehiculos.csv` esté en el directorio raíz
- Comprueba que el archivo tenga las columnas requeridas

### Errores de conexión con ATIONET
- Verifica tu conexión a internet
- Confirma que el token sea válido y no haya expirado
- Usa el endpoint `/api/test-connection` para diagnosticar

### Registros no se procesan
- Revisa los logs en `ationet_processor.log`
- Verifica que los datos en el CSV sean válidos
- Comprueba el archivo de fallidos `clases_vehiculos_failed.json`

## 🔄 Proceso de Envío

1. **Carga de datos**: Lee el archivo CSV y valida las columnas requeridas
2. **Filtrado**: Excluye registros ya procesados
3. **Formateo**: Convierte datos al formato requerido por ATIONET
4. **Envío por lotes**: Procesa registros en lotes para evitar sobrecarga
5. **Seguimiento**: Registra éxitos y fallos para evitar duplicados

## 📈 Mejores Prácticas Implementadas

- **Idempotencia**: Los envíos se pueden repetir sin crear duplicados
- **Tolerancia a fallos**: Continúa procesando aunque algunos registros fallen
- **Logging completo**: Trazabilidad completa de todas las operaciones
- **Configuración flexible**: Fácil ajuste de parámetros sin cambiar código
- **Interfaz intuitiva**: Panel web para operación sin conocimientos técnicos
- **Validación robusta**: Verificación de datos antes del procesamiento

## 🤝 Soporte

Para problemas o preguntas:

1. Revisa los logs en `ationet_processor.log`
2. Verifica la configuración en `.env` y `config.py`
3. Usa el endpoint de prueba de conexión
4. Revisa los archivos de registros procesados y fallidos
