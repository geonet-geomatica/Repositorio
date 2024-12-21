from flask import Flask, Response
import logging
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.sax.saxutils as saxutils

app = Flask(__name__)

# Configurar logs para depuración
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuración básica
BASE_URL = "https://meteorologia.onrender.com/wfs"
SRS_NAME = "EPSG:4326"
TYPENAME = "Estaciones"

# Utilidad para escapar caracteres especiales

def escape_xml(value):
    """Escapa caracteres especiales para XML."""
    if value is None:
        return ""
    return saxutils.escape(str(value))

@app.route('/wfs', methods=['GET'])
def wfs_capabilities():
    """Genera el documento GetCapabilities para el servicio WFS."""
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
                        <Get xlink:href="{BASE_URL}?SERVICE=WFS&amp;REQUEST=GetFeature"/>
                    </HTTP>
                </DCPType>
            </GetFeature>
        </Request>
    </Capability>
    <FeatureTypeList>
        <FeatureType>
            <Name>{escape_xml(TYPENAME)}</Name>
            <Title>Estaciones Agroclimáticas</Title>
            <Abstract>Estaciones meteorológicas de Mendoza</Abstract>
            <DefaultSRS>{escape_xml(SRS_NAME)}</DefaultSRS>
            <LatLongBoundingBox minx="-70.0" miny="-35.0" maxx="-68.0" maxy="-32.0"/>
        </FeatureType>
    </FeatureTypeList>
</wfs:WFS_Capabilities>"""

    return Response(capabilities_xml, content_type='application/xml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
