#file that contains the functions to generate the random points to be used to generate the sample paths through 3D matrix space

import numpy as np
from numba import njit

#there are two kinds of sampling that we may want to do. Random sampling and sampling from a normal distribution

#normal distribution sampling (generates integers to be used as indices)
def generate_normal(mean, std_dev, num_samples=100):
    return np.round(np.random.normal(loc=mean, scale=std_dev, size=num_samples)).astype(int)

#random sampling (generates integers to be used as indices)
def generate_random(min, max, num_samples=100):
    return np.round(np.random.randint(min, max, num_samples)).astype(int)

#section to generate the collection of random points to be used to sample the paths through the 3D matrix representing real space
def generate_coordinate_pairs(altitude1, altitude2, length, num_samples):
    xmin, xmax = 0, length - 1 #bounds on the uniform distribution used to generate the random points (in voxels)
    std_dev = 20 #this is the standard deviation of the normal distribution used to generate the random points (in voxels) might change this later so not hardcoded

    #generate the random points
    x1_points = generate_random(xmin, xmax, num_samples)
    y1_points = generate_normal(altitude1, std_dev, num_samples)

    x2_points = generate_random(xmin, xmax, num_samples)
    y2_points = generate_normal(altitude2, std_dev, num_samples)

    #combine the points list into two list of x,y,z coordinates
    source_points = zip(x1_points, y1_points)
    dest_points = zip(x2_points, y2_points)

    point_pairs_list = zip(source_points, dest_points)
    point_pairs_list = [list(pair) for pair in point_pairs_list]
    return point_pairs_list

# list1 = [(1, 4, 7), (2, 5, 8), (3, 6, 9)]
# list2 = [(10, 13, 16), (11, 14, 17), (12, 15, 18)]
#example usage
# numbers1 = generate_normal(mean=1000, std_dev=100)
# print(numbers1)

# numbers2 = generate_normal(mean=1000, std_dev=100)
# print(numbers2)