from flask import Flask, request, Response
import logging
from xml.sax.saxutils import escape

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "http://meteorologia.onrender.com/wfs"

# Función para escapar caracteres XML
def escape_xml(value):
    return escape(str(value)) if value is not None else ""

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
                        <Get xlink:href="{BASE_URL}?SERVICE=WFS&amp;REQUEST=GetCapabilities"/>
                    </HTTP>
                </DCPType>
            </GetCapabilities>
            <DescribeFeatureType>
                <DCPType>
                    <HTTP>
                        <Get xlink:href="{BASE_URL}?SERVICE=WFS&amp;REQUEST=DescribeFeatureType"/>
                    </HTTP>
                </DCPType>
            </DescribeFeatureType>
            <GetFeature>
                <DCPType>
                    <HTTP>
                        <Get xlink:href="{BASE_URL}?SERVICE=WFS&amp;REQUEST=GetFeature"/
