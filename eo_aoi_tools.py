import geojson
from shapely.geometry import Polygon, mapping, shape, Point
import numpy as np

def generate_complex_circle(num_vertices, area_hectares, center_lat=54.11, center_lon=22.93, noise_factor=0.00005):
    """
    Generates a complex polygon in EPSG:4326 (latitude/longitude) around a specified point and saves it as a GeoJSON file.

    Parameters:
        num_vertices (int): Number of vertices for the polygon.
        area_hectares (float): Area of the polygon in hectares.
        center_lat (float): Latitude of the center point.
        center_lon (float): Longitude of the center point.
        noise_factor (float): Factor controlling the noise level in the polygon shape.

    Returns:
        Polygon, name
    """
    # Convert area from hectares to square meters
    area_sqm = area_hectares * 10000

    # Calculate the radius for a circle with the given area (in meters)
    radius_m = np.sqrt(area_sqm / np.pi)

    # Approximate degree conversions (1 degree lat ≈ 111,000 m, lon depends on latitude)
    lat_per_meter = 1 / 111000  # Degrees latitude per meter
    lon_per_meter = 1 / (111000 * np.cos(np.radians(center_lat)))  # Degrees longitude per meter

    # Generate angles for the vertices
    angles = np.linspace(0, 2 * np.pi, num_vertices)

    # Add noise to the radius to create a complex boundary
    noise = np.random.normal(0, radius_m * noise_factor, num_vertices)  # Customizable noise factor
    radius_with_noise = radius_m + noise

    # Convert meters to degrees and generate polygon coordinates
    latitudes = center_lat + (radius_with_noise * np.sin(angles) * lat_per_meter)
    longitudes = center_lon + (radius_with_noise * np.cos(angles) * lon_per_meter)

    # Create the polygon
    polygon = Polygon(zip(longitudes, latitudes))
    name = f"cmplx_{num_vertices}_{area_hectares}ha.geojson"
    return polygon,name





def generate_square_polygon(area_hectares, center_lat=54.11, center_lon=22.93, rotation=0):
    """
    Generates a square polygon in EPSG:4326 (latitude/longitude) around a specified point.

    Parameters:
    area_hectares (float): Area of the square in hectares.
    center_lat (float): Latitude of the center point.
    center_lon (float): Longitude of the center point.
    rotation (float): Rotation angle of the square in degrees.

    Returns:
    Polygon, name
    """
    # Convert area from hectares to square meters
    side_length_m = np.sqrt(area_hectares * 10000)

    # Approximate degree conversions
    lat_per_meter = 1 / 111000
    lon_per_meter = 1 / (111000 * np.cos(np.radians(center_lat)))

    # Calculate half the side length
    half_side = side_length_m / 2

    # Create base square vertices before rotation
    base_vertices = [
        (-half_side, -half_side),
        (half_side, -half_side),
        (half_side, half_side),
        (-half_side, half_side)
    ]

    # Apply rotation if specified
    rotation_rad = np.radians(rotation)
    rotation_matrix = np.array([
        [np.cos(rotation_rad), -np.sin(rotation_rad)],
        [np.sin(rotation_rad), np.cos(rotation_rad)]
    ])

    # Rotate vertices
    rotated_vertices = [np.dot(rotation_matrix, vertex) for vertex in base_vertices]

    # Convert to geographic coordinates
    latitudes = [center_lat + vertex[1] * lat_per_meter for vertex in rotated_vertices]
    longitudes = [center_lon + vertex[0] * lon_per_meter for vertex in rotated_vertices]

    # Create the polygon
    polygon = Polygon(zip(longitudes, latitudes))
    name = f"square_{area_hectares}"
    return polygon, name


def polygon_to_geojson(polygon,name):
    # Convert to GeoJSON
    geojson_polygon = geojson.Feature(geometry=mapping(polygon), properties={})
    geojson_data = geojson.FeatureCollection([geojson_polygon])

    # Save to file
    output_file = name
    with open(output_file, "w") as f:
        geojson.dump(geojson_data, f)

    print(f"GeoJSON file created: {output_file}")


def generate_random_shapes(input_geojson, shape_type='circle', num_shapes=1,
                           min_area_hectares=1, max_area_hectares=10,
                           noise_factor=0.00005, num_vertices=20):
    """
    Generate random shapes based on an input GeoJSON file.

    Parameters:
    input_geojson (str): Path to the input GeoJSON file
    shape_type (str): Type of shape to generate ('circle' or 'square')
    num_shapes (int): Number of random shapes to generate
    min_area_hectares (float): Minimum area for generated shapes
    max_area_hectares (float): Maximum area for generated shapes
    noise_factor (float): Noise factor for complex shapes
    num_vertices (int): Number of vertices for complex circles

    Returns:
    str: Path to the output GeoJSON file with generated shapes
    """
    # Read the input GeoJSON
    with open(input_geojson, 'r') as f:
        input_data = geojson.load(f)

    # Extract the boundary of the input GeoJSON
    input_boundary = shape(input_data['features'][0]['geometry'])

    # Prepare output features
    output_features = []

    for _ in range(num_shapes):
        # Randomly sample a point within the input boundary
        while True:
            minx, miny, maxx, maxy = input_boundary.bounds
            rand_lon = np.random.uniform(minx, maxx)
            rand_lat = np.random.uniform(miny, maxy)
            point = Point(rand_lon, rand_lat)
            if input_boundary.contains(point):
                break

        # Randomly choose area within specified range
        area_hectares = np.random.uniform(min_area_hectares, max_area_hectares)

        # Generate shape based on type
        if shape_type.lower() == 'circle':
            polygon, name = generate_complex_circle(num_vertices, area_hectares, rand_lat, rand_lon, noise_factor)
        elif shape_type.lower() == 'square':
            polygon, name = generate_square_polygon(area_hectares, rand_lat, rand_lon)
        else:
            raise ValueError("Shape type must be 'circle' or 'square'")

        # Convert to GeoJSON feature
        geojson_polygon = geojson.Feature(geometry=mapping(polygon), properties={
            'name': name,
            'shape_type': shape_type,
            'area_hectares': area_hectares,
            'center_lat': rand_lat,
            'center_lon': rand_lon
        })

        output_features.append(geojson_polygon)

    # Create feature collection
    output_data = geojson.FeatureCollection(output_features)

    # Save output file
    output_file = f"random_{shape_type}s_in_boundary.geojson"
    with open(output_file, "w") as f:
        geojson.dump(output_data, f)

    print(f"Generated {num_shapes} {shape_type} shapes within the input boundary.")
    return output_file


