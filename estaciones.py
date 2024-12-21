from flask import Flask, request, Response
import logging
from xml.sax.saxutils import escape

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "http://meteorologia.onrender.com/wfs"

# Función para escapar caracteres especiales
def escape_xml(value):
    if value is None:
        return ""
    return escape(str(value))


@app.route('/wfs', methods=['GET'])
def wfs_service():
    service = request.args.get("SERVICE")
    request_type = request.args.get("REQUEST")
    typename = request.args.get("TYPENAME", "Estaciones")
    srsname = request.args.get("SRSNAME", "EPSG:4326")

    if service and service.upper() == "WFS":
        if request_type and request_type.upper() == "GETCAPABILITIES":
            capabilities_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
            <wfs:WFS_Capabilities xmlns:wfs="http://www.opengis.net/wfs"
                                  xmlns:ogc="http://www.opengis.net/ogc"
                                  xmlns:gml="http://www.opengis.net/gml"
                                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                  xmlns:xlink="http://www.w3.org/1999/xlink"
                                  version="1.1.0"
                                  xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.1.0/wfs.xsd">
                <Service>
                    <Name>WFS</Name>
                    <Title>WFS de Estaciones Agroclimáticas</Title>
                    <Abstract>Servicio WFS que proporciona datos climáticos en formato estándar.</Abstract>
                    <Keywords>Clima, Estaciones, WFS, Agroclimática</Keywords>
                    <Fees>NONE</Fees>
                    <AccessConstraints>NONE</AccessConstraints>
                </Service>
                <Capability>
                    <Request>
                        <GetCapabilities>
                            <DCPType>
                                <HTTP>
                                    <Get xlink:href="{BASE_URL}?SERVICE=WFS&REQUEST=GetCapabilities"/>
                                </HTTP>
                            </DCPType>
                        </GetCapabilities>
                        <DescribeFeatureType>
                            <DCPType>
                                <HTTP>
                                    <Get xlink:href="{BASE_URL}?SERVICE=WFS&REQUEST=DescribeFeatureType"/>
                                </HTTP>
                            </DCPType>
                        </DescribeFeatureType>
                        <GetFeature>
                            <DCPType>
                                <HTTP>
                                    <Get xlink:href="{BASE_URL}?SERVICE=WFS&REQUEST=GetFeature"/>
                                </HTTP>
                            </DCPType>
                        </GetFeature>
                    </Request>
                </Capability>
                <FeatureTypeList>
                    <FeatureType>
                        <Name>Estaciones</Name>
                        <Title>Estaciones Agroclimáticas</Title>
                        <Abstract>Estaciones meteorológicas de Mendoza</Abstract>
                        <DefaultSRS>EPSG:4326</DefaultSRS>
                        <LatLongBoundingBox minx="-70.0" miny="-35.0" maxx="-68.0" maxy="-32.0"/>
                    </FeatureType>
                </FeatureTypeList>
            </wfs:WFS_Capabilities>"""
            return Response(capabilities_xml, content_type="text/xml")

        elif request_type and request_type.upper() == "GETFEATURE":
            gml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
            <wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs"
                                   xmlns:gml="http://www.opengis.net/gml"
                                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                   xsi:schemaLocation="{BASE_URL} {BASE_URL}?SERVICE=WFS&REQUEST=DescribeFeatureType">
                <gml:featureMember>
                    <Estaciones>
                        <Nombre>{escape_xml("Estación 1")}</Nombre>
                        <Fecha>{escape_xml("2024-01-01")}</Fecha>
                        <Temperatura_Aire>{escape_xml("20°C")}</Temperatura_Aire>
                        <Humedad>{escape_xml("50%")}</Humedad>
                        <Punto_de_Rocío>{escape_xml("10°C")}</Punto_de_Rocío>
                        <Velocidad_Viento>{escape_xml("5 m/s")}</Velocidad_Viento>
                        <Dirección_del_Viento>{escape_xml("NE")}</Dirección_del_Viento>
                    </Estaciones>
                </gml:featureMember>
            </wfs:FeatureCollection>"""
            return Response(gml_response, content_type="text/xml")

    return Response("Solicitud WFS no válida.", status=400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
