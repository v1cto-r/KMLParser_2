import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from shapely.geometry import Polygon

from area import Area, MultiAreas


def parseKML(kml_file: str) -> MultiAreas:
    """
    Parses a KML file, extracts Shapely Polygons and metadata, handling MultiGeometry.

    Args:
        kml_file (str): Path to the KML file.

    Returns:
        list: A list of dictionaries containing 'name', 'polygon', and 'metadata'.
    """
    namespace = {
        "kml": "http://www.opengis.net/kml/2.2",
        "gx": "http://www.google.com/kml/ext/2.2",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance"
    }
    tree = ET.parse(kml_file)
    root = tree.getroot()

    placemarks = []
    for placemark in root.findall(".//kml:Placemark", namespace):
        base_name = placemark.find("kml:name", namespace).text

        metadata = {}

        # Check and parse <description>
        description_element = placemark.find("kml:description", namespace)
        if description_element is not None and description_element.text:
            description = description_element.text
            soup = BeautifulSoup(description, "html.parser")
            for row in soup.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) == 2:
                    key = cells[0].text.strip()
                    value = cells[1].text.strip()
                    metadata[key] = value

        # Check and parse <SimpleData> for metadata
        simple_data_elements = placemark.findall(".//kml:SimpleData", namespace)
        for simple_data in simple_data_elements:
            key = simple_data.get("name")  # Get the attribute 'name' as the key
            value = simple_data.text.strip() if simple_data.text else None
            if key and value:
                metadata[key] = value

        # Find all polygons in MultiGeometry
        multi_geometry = placemark.find(".//kml:MultiGeometry", namespace)
        polygons = []
        if multi_geometry:
            for i, polygon_tag in enumerate(multi_geometry.findall("kml:Polygon", namespace)):
                coordinates_tag = polygon_tag.find(".//kml:coordinates", namespace)
                if coordinates_tag is not None:
                    coordinates = coordinates_tag.text.strip()
                    coord_list = [
                        tuple(map(float, coord.split(",")[:2]))
                        for coord in coordinates.split()
                    ]
                    polygon = Polygon(coord_list)
                    # Generate unique names for multiple polygons
                    sub_name = f"{base_name}.{chr(65 + i)}" if i > 0 else base_name
                    polygons.append(Area(sub_name, polygon, metadata))
        else:
            # Handle single polygons
            coordinates = placemark.find(".//kml:coordinates", namespace).text.strip()
            coord_list = [
                tuple(map(float, coord.split(",")[:2]))
                for coord in coordinates.split()
            ]
            polygon = Polygon(coord_list)
            polygons.append(Area(base_name, polygon, metadata))

        placemarks.extend(polygons)

    return MultiAreas(placemarks)
