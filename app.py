from flask import Flask, jsonify
import requests

app = Flask(__name__)

# URL base de la API original
BASE_API_URL = "https://<dominio>/api/getInstantaneas.php"

@app.route('/get_all_weather_geojson', methods=['GET'])
def get_all_weather_geojson():
    """
    Endpoint para obtener datos de todas las estaciones en formato GeoJSON con toda la información disponible.
    """
    estaciones = range(1, 44)  # Lista de estaciones
    features = []

    for estacion in estaciones:
        try:
            api_url = f"{BASE_API_URL}?estacion={estacion}"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()[0]
                # Crear un Feature para cada estación
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(data["lng"]), float(data["lat"])]
                    },
                    "properties": {
                        "Nombre": data.get("Nombre", "N/A"),
                        "Fecha": data.get("fecha", "N/A"),
                        "Temperatura Aire": f"{data.get('tempAire', 'N/A')} °C",
                        "Humedad": f"{data.get('humedad', 'N/A')} %",
                        "Punto de Rocío": f"{data.get('puntoRocio', 'N/A')} °C",
                        "Velocidad Viento": f"{data.get('velocidadViento', 'N/A')} m/s",
                        "Dirección del Viento": data.get("direccionVientoTexto", "N/A"),
                        "Atraso": data.get("atraso", "N/A"),
                        "Máximo Atraso Permitido": data.get("atraso_max", "N/A"),
                        "Web Disponible": "Sí" if data.get("web", 0) == 1 else "No",
                        "URL Gráfico": f"https://agrometeo.mendoza.gov.ar/informes/grafico.php?estacion={estacion}"
                    }
                }
                features.append(feature)
        except Exception as e:
            print(f"Error al procesar la estación {estacion}: {e}")

    # Estructura GeoJSON final
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return jsonify(geojson)

if __name__ == '__main__':


