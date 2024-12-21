from flask import Flask, request, Response
import logging
from xml.etree.ElementTree import Element, SubElement, tostring

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "https://agrometeo.mendoza.gov.ar/api/getInstantaneas.php"
STATIONS = list(range(1, 44))


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
    describe_feature_type_url.set("xlink:href", base_url)

    # GetFeature operation
    get_feature = SubElement(request_elem, "GetFeature")
    dcp_type = SubElement(get_feature, "DCPType")
    http_elem = SubElement(dcp_type, "HTTP")
    get_feature_url = SubElement(http_elem, "Get")
    get_feature_url.set("xlink:href", base_url)

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

    if service and service.upper() == "WFS":
        if request_type and request_type.upper() == "GETCAPABILITIES":
            logging.info("Procesando solicitud GetCapabilities...")
            base_url = request.url_root + "wfs"
            capabilities_xml = create_capabilities(base_url)
            return Response(capabilities_xml, content_type="text/xml")

        elif request_type and request_type.upper() == "GETFEATURE":
            logging.info("Procesando solicitud GetFeature...")
            # Aquí puedes implementar la lógica para devolver los datos de las estaciones
            return Response("GetFeature aún no implementado.", content_type="text/xml")

    return Response("Solicitud WFS no válida.", status=400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
