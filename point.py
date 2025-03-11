from shapely.geometry import Point
from area import MultiAreas


class Point:
    def __init__(self, name: str, point: Point, metadata: dict):
        self.name = name
        self.point = point
        self.metadata = metadata

    def __repr__(self):
        return f"Point(name={self.name}, point={self.point}, metadata={self.metadata})"

    def pointToArray(self):
        coords = list(self.point.coords)
        return [[x, y] for x, y in coords]

    def assignPolygon(self, candidates: 'MultiAreas', assign: str):
        max_intersection_area = 0
        best_match = None

        for candidate in candidates:
            if self.point.within(candidate.polygon):
                best_match = candidate
                break
            intersection = self.point.intersection(candidate.polygon)
            intersection_area = intersection.area
            if intersection_area > max_intersection_area:
                max_intersection_area = intersection_area
                best_match = candidate

        if best_match:
            self.metadata.update(best_match.metadata)
            self.metadata[assign] = best_match.name

