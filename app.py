from flask import Flask, jsonify
import requests
import logging

app = Flask(__name__)

# Configurar logs para depuración
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Endpoint base para obtener datos de las estaciones
BASE_URL = "https://agrometeo.mendoza.gov.ar/api/getInstantaneas.php"

# Lista de estaciones disponibles
STATIONS = list(range(1, 44))  # Estaciones del 1 al 43

def fetch_station_data(station_id):
    """
    Función para obtener datos de una estación específica.
    """
    try:
        logging.info(f"Obteniendo datos para la estación {station_id}...")
        response = requests.get(f"{BASE_URL}?estacion={station_id}")
        response.raise_for_status()  # Levanta excepciones para códigos HTTP no exitosos
        data = response.json()
        
        if data and len(data) > 0:
            logging.info(f"Datos recibidos para la estación {station_id}: {data[0]}")
            return data[0]
        else:
            logging.warning(f"No se encontraron datos para la estación {station_id}.")
            return None
    except Exception as e:
        logging.error(f"Error al obtener datos de la estación {station_id}: {e}")
        return None

@app.route('/stations', methods=['GET'])
def get_all_stations():
    """
    Endpoint para obtener datos de todas las estaciones en formato GeoJSON.
    """
    features = []
    for station_id in STATIONS:
        station_data = fetch_station_data(station_id)
        if station_data:
            try:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(station_data["lng"]), float(station_data["lat"])]
                    },
                    "properties": {
                        "Nombre": station_data["Nombre"],
                        "Fecha": station_data["fecha"],
                        "Temperatura Aire": f"{station_data['tempAire']} °C",
                        "Humedad": f"{station_data['humedad']} %",
                        "Punto de Rocío": f"{station_data['puntoRocio']} °C",
                        "Velocidad Viento": f"{station_data['velocidadViento']} m/s",
                        "Dirección del Viento": station_data["direccionVientoTexto"]
                    }
                }
                features.append(feature)
            except KeyError as e:
                logging.error(f"Error procesando datos de la estación {station_id}: {e}")
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    logging.info("GeoJSON generado exitosamente.")
    return jsonify(geojson)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
