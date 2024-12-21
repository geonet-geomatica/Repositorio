from flask import Flask, request, jsonify, Response
import requests
import logging
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.sax.saxutils as saxutils

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "https://agrometeo.mendoza.gov.ar/api/getInstantaneas.php"
STATIONS = list(range(1, 44))


def fetch_station_data(station_id):
    try:
        logging.info(f"Obteniendo datos para la estación {station_id}...")
        response = requests.get(f"{BASE_URL}?estacion={station_id}")
        response.raise_for_status()
        data = response.json()
        if data and len(data) > 0:
            return data[0]
        else:
            logging.warning(f"No se encontraron datos para la estación {station_id}.")
            return None
    except Exception as e:
        logging.error(f"Error al obtener datos: {e}")
        return None


def escape_xml(value):
    return saxutils.escape(str(value)) if value else ""


def create_capabilities():
    capabilities = Element("WFS_Capabilities", {
        "version": "1.1.0",
        "xmlns": "http://www.opengis.net/wfs",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation": "http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.1.0/wfs.xsd"
    })

    service = SubElement(capabilities, "Service")
    SubElement(service, "Title").text = "WFS de Estaciones Agroclimáticas"
    SubElement(service, "Abstract").text = "Servicio WFS que proporciona datos climáticos en formato estándar."
    SubElement(service, "Fees").text = "NONE"
    SubElement(service, "AccessConstraints").text = "NONE"

    operations = SubElement(capabilities, "OperationsMetadata")
    operation = SubElement(operations, "Operation", {"name": "GetCapabilities"})
    SubElement(operation, "DCP").text = "HTTP"

    feature_type_list = SubElement(capabilities, "FeatureTypeList")
    feature_type = SubElement(feature_type_list, "FeatureType")
    SubElement(feature_type, "Name").text = "Estaciones"
    SubElement(feature_type, "Title").text = "Estaciones Agroclimáticas"
    SubElement(feature_type, "DefaultSRS").text = "EPSG:4326"

    return tostring(capabilities, encoding="utf-8", method="xml")


def create_feature_collection():
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

    return geojson


@app.route('/wfs', methods=['GET'])
def wfs_service():
    service = request.args.get("SERVICE")
    request_type = request.args.get("REQUEST")

    if service and service.upper() == "WFS":
        if request_type and request_type.upper() == "GETCAPABILITIES":
            logging.info("Procesando solicitud GetCapabilities...")
            capabilities_xml = create_capabilities()
            return Response(capabilities_xml, content_type="text/xml")

        elif request_type and request_type.upper() == "GETFEATURE":
            logging.info("Procesando solicitud GetFeature...")
            geojson = create_feature_collection()
            return jsonify(geojson)

    return Response("Solicitud WFS no válida.", status=400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
