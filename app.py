from flask import Flask, jsonify
import requests

app = Flask(__name__)

# URL base de la API original
BASE_API_URL = "https://agrometeo.mendoza.gov.ar/api/getInstantaneas.php"

@app.route('/get_all_weather_geojson', methods=['GET'])
def get_all_weather_geojson():
    """
    Endpoint para obtener datos de todas las estaciones en formato GeoJSON.
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
                        "nombre": data["Nombre"],
                        "temperatura": data["tempAire"],
                        "humedad": data["humedad"],
                        "viento": data["velocidadViento"]
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
    app.run(debug=True, host='0.0.0.0', port=5000)

