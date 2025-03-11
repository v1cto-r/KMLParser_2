from typing import Iterator
from shapely.geometry import Polygon

class Area:
    def __init__(self, name: str, polygon: Polygon, metadata: dict):
        self.name = name
        self.polygon = polygon
        self.metadata = metadata

    def __repr__(self):
        return f"Area(name={self.name}, polygon={self.polygon}, metadata={self.metadata})"

    def polygontoArray(self):
        coords = list(self.polygon.exterior.coords)
        return [[x, y] for x, y in coords]

    def assignPolygon(self, candidates: 'MultiAreas', assign: str):
        max_intersection_area = 0
        best_match = None

        for candidate in candidates:
            if self.polygon.within(candidate.polygon):
                best_match = candidate
                break
            intersection = self.polygon.intersection(candidate.polygon)
            intersection_area = intersection.area
            if intersection_area > max_intersection_area:
                max_intersection_area = intersection_area
                best_match = candidate

        if best_match:
            self.metadata.update(best_match.metadata)
            self.metadata[assign] = best_match.name

    def assignCentroid(self):
        self.metadata["CENTROID"] = self.polygon.centroid.coords[0]

class MultiAreas:
    def __init__(self, areas: list):
        if not all(isinstance(area, Area) for area in areas):
            raise ValueError("All elements in the areas list must be instances of the Area class.")
        self.areas = areas

    def __repr__(self):
        return f"MultiArea(areas={self.areas})"

    def __iter__(self) -> Iterator[Area]:
        return iter(self.areas)

    def exportToExcel(self, filename: str):
        import pandas as pd
        data = []
        for area in self.areas:
            data.append({
                "name": area.name,
                **area.metadata
            })

        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)

    def exportToJSON(self, filename: str):
        import json
        data = []
        for area in self.areas:
            data.append({
                "name": area.name,
                "coordinates": area.polygontoArray(),
                **area.metadata
            })

        with open(filename, "w") as f:
            json.dump(data, f)

    def exportToCSV(self, filename: str):
        import csv
        data = []
        for area in self.areas:
            data.append({
                "name": area.name,
                "coordinates": area.polygontoArray(),
                **area.metadata
            })

        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "coordinates", *area.metadata.keys()])
            writer.writeheader()
            writer.writerows(data)

    def exportToKML(self, filename: str):
        import xml.etree.ElementTree as ET
        from xml.dom import minidom

        kml = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
        document = ET.SubElement(kml, "Document")

        for area in self.areas:
            placemark = ET.SubElement(document, "Placemark")
            name = ET.SubElement(placemark, "name")
            name.text = area.name

            polygon = ET.SubElement(placemark, "Polygon")
            outer_boundary_is = ET.SubElement(polygon, "outerBoundaryIs")
            linear_ring = ET.SubElement(outer_boundary_is, "LinearRing")
            coordinates = ET.SubElement(linear_ring, "coordinates")
            coords = " ".join([f"{x},{y}" for x, y in area.polygon.exterior.coords])
            coordinates.text = coords

        xmlstr = minidom.parseString(ET.tostring(kml)).toprettyxml(indent="    ")
        with open(filename, "w") as f:
            f.write(xmlstr)

    def exportToGeoJSON(self, filename: str):
        import json
        data = {
            "type": "FeatureCollection",
            "features": []
        }
        for area in self.areas:
            feature = {
                "type": "Feature",
                "properties": area.metadata,
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [area.polygontoArray()]
                }
            }
            data["features"].append(feature)

        with open(filename, "w") as f:
            json.dump(data, f)

    def exportToDatabase(self, uri: str, database: str, collection: str):
        import pymongo
        from pymongo.server_api import ServerApi
        client = pymongo.MongoClient(uri, server_api=ServerApi('1'))
        db = client[database]
        areas = db[collection]
        areas.insert_many([{
            "name": area.name,
            "coordinates": area.polygontoArray(),
            **area.metadata
        } for area in self.areas])
        client.close()
