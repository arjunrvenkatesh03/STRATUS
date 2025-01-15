#module to sample the points to generate paths through 3D space

import numpy as np

def generate_normal(mean, std_dev, num_samples):
    """Generates a list of normally distributed samples."""
    return np.round(np.random.normal(loc=mean, scale=std_dev, size=num_samples)).astype(int)

def generate_random(min_val, max_val, num_samples):
    """Generates a list of randomly distributed samples within a specified range."""
    return np.round(np.random.randint(min_val, max_val, num_samples)).astype(int)

def generate_coordinates(mean, std_dev, min_val, max_val, num_samples):
    """Generates a list of coordinate pairs using normal and uniform distributions."""
    altIdx = generate_normal(mean, std_dev, num_samples)
    longlatIdx = generate_random(min_val, max_val, num_samples)
    coordinate_pairs = list(zip(longlatIdx, altIdx))
    return coordinate_pairs

def sample_within_longitudinal_range_corrected(first_x, min_sep, max_sep, min_val, max_val):
    """Samples a second coordinate's x-value within a specified separation range from the first coordinate."""
    potential_xs = []
    
    # Generate potential x values within the specified range and separation bounds
    for x in range(min_val, max_val + 1):
        separation = abs(x - first_x)
        if min_sep <= separation <= max_sep:
            potential_xs.append(x)
    
    # If there are valid potential x values, randomly choose one
    if potential_xs:
        return np.random.choice(potential_xs)
    else:
        return None

# Other functions (generate_normal, generate_random, generate_coordinates) remain the same

def generate_coordinate_pairs(altitude1, altitude2, std_dev, min_val, max_val, num_samples, min_sep, max_sep):
    """Generates coordinate pairs with specified altitude and separation constraints, ensuring each pair has a valid separation."""
    # Generate initial list of source coordinates
    initial_sourceCoords = generate_coordinates(altitude1, std_dev, min_val, max_val, num_samples)
    
    # Initialize lists to hold final source and destination coordinates
    final_sourceCoords = []
    destCoords = []

    for sourceCoord in initial_sourceCoords:
        # Attempt to find a valid destination coordinate within separation bounds
        second_coord_x = sample_within_longitudinal_range_corrected(sourceCoord[0], min_sep, max_sep, min_val, max_val)
        
        if second_coord_x is not None:  # A valid second x-coordinate was found
            second_coord_alt = generate_normal(altitude2, std_dev, 1)[0]
            
            # Append valid source and destination coordinates to final lists
            final_sourceCoords.append(sourceCoord)
            destCoords.append((second_coord_x, second_coord_alt))

    # Pair each valid source coordinate with its corresponding destination coordinate
    coordinate_pairs = list(zip(final_sourceCoords, destCoords))
    return coordinate_pairs

# # Parameters
# sourceAlt = 100
# std_dev = 3
# min_val = 0
# max_val = 25
# numPaths = 20
# min_sep = 18
# max_sep = 22

# # Generate and print coordinate pairs with the specified constraints
# coordinate_pairs = generate_coordinate_pairs(sourceAlt, sourceAlt, std_dev, min_val, max_val, numPaths, min_sep, max_sep)
# for pair in coordinate_pairs:
#     print(pair)

# print(len(coordinate_pairs))







# import numpy as np

# def generate_normal(mean, std_dev, num_samples):
#     return np.round(np.random.normal(loc=mean, scale=std_dev, size=num_samples)).astype(int)

# #random sampling (generates integers to be used as indices)
# def generate_random(min, max, num_samples):
#     return np.round(np.random.randint(min, max, num_samples)).astype(int)

# def generate_coordinates(mean, std_dev, min_val, max_val, num_samples):
#     altIdx = generate_normal(mean, std_dev, num_samples)
#     longlatIdx = generate_random(min_val, max_val, num_samples)
#     coordinate_pairs = list(zip(longlatIdx, altIdx))
#     return coordinate_pairs

# def generate_coordinate_pairs(altitude1,altitude2, std_dev, min_val, max_val, num_samples):
#     sourceCoords = generate_coordinates(altitude1, std_dev, min_val, max_val, num_samples)
#     destCoords = generate_coordinates(altitude2, std_dev, min_val, max_val, num_samples)
#     coordinate_pairs = list(zip(sourceCoords, destCoords))
#     return coordinate_pairs

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