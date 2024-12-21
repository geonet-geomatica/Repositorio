from flask import Flask, request, Response
import logging
from xml.etree.ElementTree import Element, SubElement, tostring

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "http://meteorologia.onrender.com/wfs"


def create_capabilities(base_url):
    capabilities = Element("wfs:WFS_Capabilities", {
        "version": "1.1.0",
        "xmlns:wfs": "http://www.opengis.net/wfs",
        "xmlns:ogc": "http://www.opengis.net/ogc",
        "xmlns:gml": "http://www.opengis.net/gml",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xmlns:xlink": "http://www.w3.org/1999/xlink",
        "xsi:schemaLocation": "http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.1.0/wfs.xsd"
    })

    # Service section
    service = SubElement(capabilities, "Service")
    SubElement(service, "Name").text = "WFS"
    SubElement(service, "Title").text = "WFS de Estaciones Agroclimáticas"
    SubElement(service, "Abstract").text = "Servicio WFS que proporciona datos climáticos en formato estándar."
    SubElement(service, "Keywords").text = "Clima, Estaciones, WFS, Agroclimática"
    SubElement(service, "Fees").text = "NONE"
    SubElement(service, "AccessConstraints").text = "NONE"

    # Capability section
    capability = SubElement(capabilities, "Capability")
    request_elem = SubElement(capability, "Request")

    # GetCapabilities operation
    get_capabilities = SubElement(request_elem, "GetCapabilities")
    dcp_type = SubElement(get_capabilities, "DCPType")
    http_elem = SubElement(dcp_type, "HTTP")
    get_capabilities_url = SubElement(http_elem, "Get")
    get_capabilities_url.set("xlink:href", base_url)

    # DescribeFeatureType operation
    describe_feature_type = SubElement(request_elem, "DescribeFeatureType")
    dcp_type = SubElement(describe_feature_type, "DCPType")
    http_elem = SubElement(dcp_type, "HTTP")
    describe_feature_type_url = SubElement(http_elem, "Get")
    describe_feature_type_url.set("xlink:href", base_url + "?SERVICE=WFS&REQUEST=DescribeFeatureType")

    # GetFeature operation
    get_feature = SubElement(request_elem, "GetFeature")
    dcp_type = SubElement(get_feature, "DCPType")
    http_elem = SubElement(dcp_type, "HTTP")
    get_feature_url = SubElement(http_elem, "Get")
    get_feature_url.set("xlink:href", base_url + "?SERVICE=WFS&REQUEST=GetFeature")

    # FeatureTypeList
    feature_type_list = SubElement(capabilities, "FeatureTypeList")
    feature_type = SubElement(feature_type_list, "FeatureType")
    SubElement(feature_type, "Name").text = "Estaciones"
    SubElement(feature_type, "Title").text = "Estaciones Agroclimáticas"
    SubElement(feature_type, "Abstract").text = "Estaciones meteorológicas de Mendoza"
    SubElement(feature_type, "DefaultSRS").text = "EPSG:4326"
    bbox = SubElement(feature_type, "LatLongBoundingBox", {
        "minx": "-70.0",
        "miny": "-35.0",
        "maxx": "-68.0",
        "maxy": "-32.0"
    })

    return tostring(capabilities, encoding="utf-8", method="xml")


@app.route('/wfs', methods=['GET'])
def wfs_service():
    service = request.args.get("SERVICE")
    request_type = request.args.get("REQUEST")
    typename = request.args.get("TYPENAME", "Estaciones")
    srsname = request.args.get("SRSNAME", "EPSG:4326")

    if service and service.upper() == "WFS":
        if request_type and request_type.upper() == "GETCAPABILITIES":
            logging.info("Procesando solicitud GetCapabilities...")
            capabilities_xml = create_capabilities(BASE_URL)
            return Response(capabilities_xml, content_type="text/xml")

        elif request_type and request_type.upper() == "DESCRIBEFEATURETYPE":
            logging.info("Procesando solicitud DescribeFeatureType...")
            schema_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
            <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                        xmlns:gml="http://www.opengis.net/gml"
                        xmlns="{BASE_URL}"
                        targetNamespace="{BASE_URL}"
                        elementFormDefault="qualified">
                <xsd:complexType name="EstacionesType">
                    <xsd:sequence>
                        <xsd:element name="Nombre" type="xsd:string"/>
                        <xsd:element name="Fecha" type="xsd:string"/>
                        <xsd:element name="Temperatura_Aire" type="xsd:string"/>
                        <xsd:element name="Humedad" type="xsd:string"/>
                        <xsd:element name="Punto_de_Rocío" type="xsd:string"/>
                        <xsd:element name="Velocidad_Viento" type="xsd:string"/>
                        <xsd:element name="Dirección_del_Viento" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:schema>"""
            return Response(schema_xml, content_type="text/xml")

        elif request_type and request_type.upper() == "GETFEATURE":
            logging.info("Procesando solicitud GetFeature...")
            # Ejemplo estático de una respuesta GML válida
            gml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
            <wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs"
                                   xmlns:gml="http://www.opengis.net/gml"
                                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                   xsi:schemaLocation="{BASE_URL} {BASE_URL}?SERVICE=WFS&REQUEST=DescribeFeatureType">
                <gml:featureMember>
                    <Estaciones>
                        <Nombre>Estación 1</Nombre>
                        <Fecha>2024-01-01</Fecha>
                        <Temperatura_Aire>20°C</Temperatura_Aire>
                        <Humedad>50%</Humedad>
                        <Punto_de_Rocío>10°C</Punto_de_Rocío>
                        <Velocidad_Viento>5 m/s</Velocidad_Viento>
                        <Dirección_del_Viento>NE</Dirección_del_Viento>
                    </Estaciones>
                </gml:featureMember>
            </wfs:FeatureCollection>"""
            return Response(gml_response, content_type="text/xml")

    return Response("Solicitud WFS no válida.", status=400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
