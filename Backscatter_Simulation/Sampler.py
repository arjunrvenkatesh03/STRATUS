#module to sample the points to generate paths through 3D space
import numpy as np

def generate_normal(mean, std_dev, num_samples):
    return np.round(np.random.normal(loc=mean, scale=std_dev, size=num_samples)).astype(int)

#random sampling (generates integers to be used as indices)
def generate_random(min, max, num_samples=100):
    return np.round(np.random.randint(min, max, num_samples)).astype(int)

def generate_coordinates(mean, std_dev, min_val, max_val, num_samples):
    x_coords = generate_normal(mean, std_dev, num_samples)
    y_coords = generate_random(min_val, max_val, num_samples)
    coordinate_pairs = list(zip(x_coords, y_coords))
    return coordinate_pairs

def generate_coordinate_pairs(altitude1,altitude2, std_dev, min_val, max_val, num_samples):
    sourceCoords = generate_coordinates(altitude1, std_dev, min_val, max_val, num_samples)
    destCoords = generate_coordinates(altitude2, std_dev, min_val, max_val, num_samples)
    coordinate_pairs = list(zip(sourceCoords, destCoords))
    return coordinate_pairs

# Example usage
# mean = 50
# altitude1 = 40
# altitude2 = 60
# std_dev = 10
# min_val = 0
# max_val = 100
# num_samples = 100

# coordinates = generate_coordinate_pairs(altitude1,altitude2, std_dev, min_val, max_val, num_samples)

# # Print the coordinate pairs
# for coord in coordinates:
#     print(coord)