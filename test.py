

from  eo_aoi_tools import polygon_to_geojson


import numpy as np
from shapely.geometry import Polygon
from shapely.affinity import scale, rotate
from shapely.ops import transform
from shapely.validation import make_valid
from pyproj import Transformer

import random
import math
from shapely.geometry import Polygon, Point
from pyproj import Geod

def generate_polygon(num_vertices, target_area_ha):
    # Convert target area from hectares to square meters
    target_area_m2 = target_area_ha * 10000

    # Generate random points around a center
    center = Point(0, 0)
    points = []
    for _ in range(num_vertices):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0.1, 1.0)  # Adjust the range to control the shape
        x = center.x + distance * math.cos(angle)
        y = center.y + distance * math.sin(angle)
        points.append((x, y))

    # Create a polygon from the points
    polygon = Polygon(points)

    # Calculate the area of the polygon
    geod = Geod(ellps="WGS84")
    area_m2, _ = geod.geometry_area_perimeter(polygon)

    # Scale the polygon to match the target area
    scale_factor = math.sqrt(target_area_m2 / abs(area_m2))
    scaled_polygon = Polygon([(x * scale_factor, y * scale_factor) for x, y in polygon.exterior.coords])

    # Reproject the polygon to CRS 4326 (WGS84)
    # Since we are working in a local coordinate system, we need to translate the polygon to a real-world location
    # For simplicity, let's place the polygon at a specific latitude and longitude
    latitude = 45.0
    longitude = 10.0
    translated_polygon = Polygon([(longitude + x, latitude + y) for x, y in scaled_polygon.exterior.coords])

    return translated_polygon




# Example usage
polygon = generate_polygon(5000, 2000)
polygon_to_geojson(polygon,'dupa')