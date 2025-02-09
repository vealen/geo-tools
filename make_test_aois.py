from eo_aoi_tools import *
import os

aoi_complexity = {
    "SQUARE": {
        "Micro square": {'area':0.5},
        "Small square": {'area':1},
        "Normal square": {'area':1000},
        "Large square": {'area':10000},
        "Enormous square": {'area':60000},
    },
    "CIRCLES": {
        "100 vertices": {"area": 5000, "vertex_count": 100, "noise": 0.05},
        "3000 vertices": {"area": 5000, "vertex_count": 3000, "noise": 0.05},
        "10k vertices": {"area": 5000, "vertex_count": 10000, "noise": 0.05},
        "50k vertices": {"area": 5000, "vertex_count": 50000, "noise": 0.05},
    },
}


def generate_random_shapes_from_dict(input_geojson, shape_type='complex', num_shapes=1,
                                     complexity_dict=None):
    """
    Generate random shapes based on an input GeoJSON file and AOI complexity dictionary.

    Parameters:
    input_geojson (str): Path to the input GeoJSON file
    shape_type (str): Type of shape to generate ('circle' or 'square')
    num_shapes (int): Number of random shapes to generate
    noise_factor (float): Noise factor for complex shapes
    complexity_dict (dict): AOI complexity dictionary for shapes

    Returns:
    str: Path to the output GeoJSON file with generated shapes
    """

    if complexity_dict is None:
        raise ValueError("complexity_dict must be provided to generate shapes.")

    # Read the input GeoJSON
    with open(input_geojson, 'r') as f:
        input_data = geojson.load(f)

    # Extract the boundary of the input GeoJSON
    input_boundary = shape(input_data['features'][0]['geometry'])

    # Prepare output features
    output_features = []

    for _ in range(num_shapes):

        # Generate shapes for all options based on the shape type
        if shape_type.lower() == 'complex':
            circle_options = complexity_dict['CIRCLES']
            for selected_option, properties in circle_options.items():
                while True:
                    minx, miny, maxx, maxy = input_boundary.bounds
                    rand_lon = np.random.uniform(minx, maxx)
                    rand_lat = np.random.uniform(miny, maxy)
                    point = Point(rand_lon, rand_lat)
                    print(point)
                    if input_boundary.contains(point):
                        print('Found enough points to create')
                        break

                area = properties['area']
                num_vertices = properties['vertex_count']
                noise_factor = properties['noise']

                polygon, name = generate_complex_circle(num_vertices=num_vertices, area_hectares=area,
                                                        center_lat=rand_lat, center_lon=rand_lon,
                                                        noise_factor=noise_factor)

                # Convert to GeoJSON feature
                geojson_polygon = geojson.Feature(geometry=mapping(polygon), properties={
                    'name': name,
                    'shape_type': shape_type,
                    'area_hectares': area,
                    'center_lat': rand_lat,
                    'center_lon': rand_lon,
                    'num_vertex': num_vertices
                })

                output_features.append(geojson_polygon)

        elif shape_type.lower() == 'square':
            square_options = complexity_dict['SQUARE']
            for selected_option, properties in square_options.items():
                while True:
                    minx, miny, maxx, maxy = input_boundary.bounds
                    rand_lon = np.random.uniform(minx, maxx)
                    rand_lat = np.random.uniform(miny, maxy)
                    point = Point(rand_lon, rand_lat)
                    print(point)
                    if input_boundary.contains(point):
                        print('Found enough points to create')
                        break
                area = properties['area']
                area_hectares = area

                polygon, name = generate_square_polygon(area_hectares=area_hectares, center_lat=rand_lat,
                                                        center_lon=rand_lon)

                # Convert to GeoJSON feature
                geojson_polygon = geojson.Feature(geometry=mapping(polygon), properties={
                    'name': name,
                    'shape_type': shape_type,
                    'area_hectares': area_hectares,
                    'center_lat': rand_lat,
                    'center_lon': rand_lon,
                })

                output_features.append(geojson_polygon)

        else:
            raise ValueError("Shape type must be 'complex' or 'square'")

    # Create feature collection
    output_data = geojson.FeatureCollection(output_features)
    file_name_without_extension = os.path.splitext(os.path.basename(input_geojson))[0]




    output_file = f"{shape_type}_set_boundaries_{file_name_without_extension}.geojson"

    with open(output_file, "w") as f:
        geojson.dump(output_data, f)

    print(f"Generated {num_shapes} {shape_type} shapes within the input boundary.")
    return output_file




directory = '/Users/fiodor/Documents/Orbify/orbifyinc/geo-tools/aois/Whole_continents'


for name in os.listdir(directory):

    file_path = os.path.join(directory, name)


    if os.path.isfile(file_path):
        generate_random_shapes_from_dict(input_geojson=file_path, shape_type='complex',num_shapes=5, complexity_dict=aoi_complexity)
        generate_random_shapes_from_dict(input_geojson=file_path, shape_type='square',num_shapes=5, complexity_dict=aoi_complexity)




