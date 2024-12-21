from flask import Flask, jsonify, Response
import requests
import logging
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
import xml.sax.saxutils as saxutils

app = Flask(__name__)

# Configurar logs para depuración
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Endpoint base para obtener datos de las estaciones
BASE_URL = "https://agrometeo.mendoza.gov.ar/api/getInstantaneas.php"

# Lista de estaciones disponibles (1 al 43)
STATIONS = list(range(1, 44))


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
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error al obtener datos de la estación {station_id}: {http_err}")
    except Exception as e:
        logging.error(f"Error al obtener datos de la estación {station_id}: {e}")
    return None


def escape_xml(value):
    """
    Escapa caracteres especiales en valores XML.
    """
    if value is None:
        return ""
    return saxutils.escape(str(value))


def convert_to_wfs(geojson):
    """
    Convierte un objeto GeoJSON a formato XML WFS.
    """
    wfs = Element("wfs:FeatureCollection", {
        "xmlns:wfs": "http://www.opengis.net/wfs",
        "xmlns:gml": "http://www.opengis.net/gml"
    })

    for feature in geojson["features"]:
        member = SubElement(wfs, "wfs:member")
        feature_elem = SubElement(member, "Feature")
        properties = feature["properties"]
        geometry = feature["geometry"]

        for key, value in properties.items():
            property_elem = SubElement(feature_elem, key)
            property_elem.text = escape_xml(value)

        geometry_elem = SubElement(feature_elem, "geometry", {
            "type": geometry["type"]
        })
        coordinates = SubElement(geometry_elem, "coordinates")
        coordinates.text = " ".join(map(str, geometry["coordinates"]))

    return tostring(wfs, encoding="utf-8", method="xml")


@app.route('/stations', methods=['GET'])
def get_all_stations():
    """
    Endpoint para obtener datos de todas las estaciones en formato GeoJSON.
    """
    logging.info("Iniciando la generación del GeoJSON...")

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
                        "Temperatura_Aire": f"{station_data['tempAire']} °C",
                        "Humedad": f"{station_data['humedad']} %",
                        "Punto_de_Rocío": f"{station_data['puntoRocio']} °C",
                        "Velocidad_Viento": f"{station_data['velocidadViento']} m/s",
                        "Dirección_del_Viento": station_data["direccionVientoTexto"]
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


@app.route('/wfs', methods=['GET'])
def get_wfs():
    """
    Endpoint para obtener datos en formato WFS.
    """
    logging.info("Generando datos en formato WFS...")

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
                        "Temperatura_Aire": f"{station_data['tempAire']} °C",
                        "Humedad": f"{station_data['humedad']} %",
                        "Punto_de_Rocío": f"{station_data['puntoRocio']} °C",
                        "Velocidad_Viento": f"{station_data['velocidadViento']} m/s",
                        "Dirección_del_Viento": station_data["direccionVientoTexto"]
                    }
                }
                features.append(feature)
            except KeyError as e:
                logging.error(f"Error procesando datos de la estación {station_id}: {e}")

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    wfs_response = convert_to_wfs(geojson)
    logging.info("WFS generado exitosamente.")
    return Response(wfs_response, content_type='application/xml')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
