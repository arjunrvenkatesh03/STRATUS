#Section to import all the libraries needed for the project
import numpy as np
import pandas as pd
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import pyhdf
from pyhdf.SD import SD, SDC
from matplotlib import colors
from numba import njit, jit

#section to pull the functions from the other modules that make up this project
from VoxelHomogenization import homogenize_array_size
from Visualizer import visualise_data
from Parser import parse_hdf_file
from PointsSampler import generate_coordinate_pairs
from BresenhamAlg import bresenham_line, is_clear_path

# @njit
# def bresenham_line(array, pair):
#     x1,y1 = pair[0]
#     x2,y2 = pair[1]

#     # Get the size of the array
#     width, height = array.shape

#     # Initialize the list of points
#     points = []

#     # Bresenham's line algorithm
#     dx = abs(x2 - x1)
#     dy = abs(y2 - y1)

#     sx = -1 if x1 > x2 else 1
#     sy = -1 if y1 > y2 else 1

#     if dx > dy:
#         err = dx / 2.0
#         while x1 != x2:
#             if 0 <= x1 < width and 0 <= y1 < height:
#                 points.append((y1, x1))
#             err -= dy
#             if err < 0:
#                 y1 += sy
#                 err += dx
#             x1 += sx
#     else:
#         err = dy / 2.0
#         while y1 != y2:
#             if 0 <= x1 < width and 0 <= y1 < height:
#                 points.append((y1, x1))
#             err -= dx
#             if err < 0:
#                 x1 += sx
#                 err += dy
#             y1 += sy
            
#     # Include the last point, if it's inside the array
#     if 0 <= x1 < width and 0 <= y1 < height:
#         points.append((y1, x1))

#     return np.array(points, dtype=np.int64)

# @njit
# def bresenham_line(x0, y0, x1, y1):
#     """Generate points on a line from (x0, y0) to (x1, y1) using Bresenham's line algorithm."""
#     points = []
#     dx = abs(x1 - x0)
#     dy = abs(y1 - y0)
#     x, y = x0, y0
#     sx = -1 if x0 > x1 else 1
#     sy = -1 if y0 > y1 else 1
#     if dx > dy:
#         err = dx / 2.0
#         while x != x1:
#             points.append((x, y))
#             err -= dy
#             if err < 0:
#                 y += sy
#                 err += dx
#             x += sx
#     else:
#         err = dy / 2.0
#         while y != y1:
#             points.append((x, y))
#             err -= dx
#             if err < 0:
#                 x += sx
#                 err += dy
#             y += sy
#     points.append((x1, y1))
#     return points

# def plot_paths(plane_position, columns, array_shape, step=20):

# @njit
def has_cloud(path, array):
    """Check if there is a cloud in the path."""
    for x, y in path:
        if array[x, y] == 1:
            return True
    return False

# def plot_visibility_circle(plane_position, array):
    """Plot angular visibility as a circle around the plane position."""
    plane_x, plane_y = plane_position
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Plot each path as a line from the plane to the edge of the array
    for angle in np.linspace(0, 360, 180):
        end_x = plane_x + array.shape[0] * np.cos(np.radians(angle))
        end_y = plane_y + array.shape[1] * np.sin(np.radians(angle))
        path = bresenham_line(plane_x, plane_y, end_x, end_y)
        color = 'red' if has_cloud(path, array) else 'green'
        x, y = zip(*path)
        ax.plot(y, x, color=color, linewidth=0.5)  # y, x because we're plotting columns and rows

    # Draw a circle around the plane
    circle = patches.Circle((plane_y, plane_x), radius=min(array.shape)/2, fill=False, color='black')
    ax.add_patch(circle)

    # Set up plot
    ax.set_xlim(0, array.shape[1])
    ax.set_ylim(0, array.shape[0])
    ax.invert_yaxis()  # Invert y-axis to match array indexing
    ax.set_aspect('equal')  # Ensure the plot is a circle, not an ellipse
    ax.set_title('Angular Visibility from Point (100, 200)')
    ax.set_xlabel('Column Index')
    ax.set_ylabel('Row Index')
    plt.show()
    """Plot Bresenham lines from a plane position to all points in specified columns."""
    plane_x, plane_y = plane_position
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plot each column's paths
    for idx, col in enumerate(columns):
        color = 'blue' if idx == 0 else 'red'
        for row in range(0, array_shape[0]):  # Only plot every 'step' paths
            path = bresenham_line(plane_x, plane_y, row, col)
            x, y = zip(*path)
            ax.plot(y, x, color=color, linewidth=0.5)  # y, x because we're plotting columns and rows
            # ax.text(y[0], x[0], 'Start', fontsize=12)  # Label start point
            # ax.text(y[-1], x[-1], 'End', fontsize=12)  # Label end point

    # Set up plot
    ax.set_xlim(0, array_shape[1])
    ax.set_ylim(0, array_shape[0])
    ax.invert_yaxis()  # Invert y-axis to match array indexing
    ax.set_title('Paths from Point (100, 200) to Columns 80 (blue) and 120 (red)')
    ax.set_xlabel('Column Index')
    ax.set_ylabel('Row Index')
    plt.show()

# Example usage
# plane_position = (100, 200)  # Plane is at (100,200)
# columns = [180, 220]
# array_shape = (200, 400)
# plot_paths(plane_position, columns, array_shape)
# plot_visibility_circle(plane_position, np.random.choice([0,1], size = array_shape, p=[0.8,0.2]))


#@njit
import numpy as np

def calculate_cloud_coverage(plane_position, array, angular_view):
    # Define the look distance
    look_distance = 50  # replace with your actual look distance

    # Define the plane coordinates
    plane_x, plane_y = plane_position

    # Define the square boundaries
    x_min = max(plane_x - look_distance, 0)
    x_max = min(plane_x + look_distance, array.shape[0])
    y_min = max(plane_y - look_distance, 0)
    y_max = min(plane_y + look_distance, array.shape[1])

    # # Define the square boundaries
    # x_min = max(0, plane_x - radius)
    # x_max = min(array.shape[0], plane_x + radius)
    # y_min = max(0, plane_y - radius)
    # y_max = min(array.shape[1], plane_y + radius)

    # Initialize the cloud count, paths list, and path count within angular view
    cloud_count = 0
    paths = []
    path_count = 0

    # Loop over every pixel on the edge of the square
    for x in [x_min, x_max-1]:
        for y in range(y_min, y_max):
            # Calculate the angle from the horizontal
            angle = np.arctan2((y - plane_y) * 0.03, (x - plane_x) * 1) * 180 / np.pi
            # Make the angle always positive
            if angle < 0:
                angle += 360
            # print(angle)

            lookup_angle = angular_view[1]
            lookdown_angle = angular_view[0]
            # Check if the angle is within the angular view
            if (0 <= angle <= lookup_angle) or (360 - lookdown_angle <= angle <= 360):
                pair = np.array([[plane_x, plane_y], [x, y]], dtype=np.int64)
                path = bresenham_line(array, pair)
                paths.append(path)
                path_count += 1
                if has_cloud(path, array):
                    cloud_count += 1

    for y in [y_min, y_max-1]:
        for x in range(x_min, x_max):
            # Calculate the angle from the horizontal
            angle = np.arctan2(y - plane_y, x - plane_x) * 180 / np.pi

            # Make the angle always positive
            if angle < 0:
                angle += 360
            # print(angle)

            # Check if the angle is within the angular view
            if (0 <= angle <= lookup_angle) or (360 - lookdown_angle <= angle <= 360):
                pair = np.array([[plane_x, plane_y], [x, y]], dtype=np.int64)
                path = bresenham_line(array, pair)
                paths.append(path)
                path_count += 1
                if has_cloud(path, array):
                    cloud_count += 1

    # Calculate and return the percentage of paths that have a cloud and the paths
    return (cloud_count / path_count), paths



# @njit
# def calculate_cloud_coverage(array, plane_position):
#     plane_x, plane_y = plane_position
#     # Define the square radius
#     radius = 100

#     # Define the square boundaries
#     x_min = max(0, plane_x - radius)
#     x_max = min(array.shape[0], plane_x + radius)
#     y_min = max(0, plane_y - radius)
#     y_max = min(array.shape[1], plane_y + radius)

#     # Initialize the cloud count and paths list
#     cloud_count = 0
#     paths = []

#     # Loop over every pixel on the edge of the square
#     for x in [x_min, x_max-1]:
#         for y in range(y_min, y_max):
#             pair = np.array([[plane_x, plane_y], [x, y]], dtype=np.int64)
#             path = bresenham_line(array, pair)
#             paths.append(path)
#             if has_cloud(path, array):
#                 cloud_count += 1
#     for y in [y_min, y_max-1]:
#         for x in range(x_min, x_max):
#             pair = np.array([[plane_x, plane_y], [x, y]], dtype=np.int64)
#             path = bresenham_line(array, pair)
#             paths.append(path)
#             if has_cloud(path, array):
#                 cloud_count += 1

#     # Calculate and return the percentage of paths that have a cloud and the paths
#     return (cloud_count / ((x_max - x_min) * (y_max - y_min))), paths

# Call the function to execute the code

# # Define the array shape and cloud probabilities
# array_shape = (200, 400)
# cloud_probabilities = [0.7, 0.3]

# # Create the cloud array
# array = np.random.choice([0, 1], size=array_shape, p=cloud_probabilities)
# plane_x, plane_y = 100, 200
# coverage, paths = calculate_cloud_coverage(array, plane_x, plane_y)

# Plot the paths
# plt.imshow(array, cmap='gray')
# for i, path in enumerate(paths):
#     if i % 5 == 0:
#         plt.plot([p[1] for p in path], [p[0] for p in path], color='red')
# plt.show()

# @njit
def main(filename):
    # Call file parser function to get the three data arrays
    lowAlt_data, midAlt_data, highAlt_data, minLat, maxLat, minLong, maxLong, minTime, maxTime, daynightFlag = parse_hdf_file(filename)


    # Call the voxel homogenization function to homogenize the voxel size of the three data arrays
    lowAlt_data = homogenize_array_size(lowAlt_data, "low")
    midAlt_data = homogenize_array_size(midAlt_data, "mid")
    highAlt_data = homogenize_array_size(highAlt_data, "high")
    formattedData = np.concatenate((highAlt_data, midAlt_data, lowAlt_data), axis=1)

    # Make a copy of the cloud data to filter out locations of clouds (=2)
    cloudData = formattedData.copy()
    cloudData[cloudData != 2] = 0
    cloudData[cloudData == 2] = 1

    # Rotate the cloudData array 90 degrees twice and assign it back
    cloudData_array = np.rot90(cloudData, 3)
    # print(cloudData_array.shape)
    # plt.plot(cloudData_array, cmap='gray')

    # # Define the array shape and cloud probabilities
    # array_shape = (200, 400)
    # cloud_probabilities = [0.7, 0.3]

    # # Create the cloud array
    # array = np.random.choice([0, 1], size=array_shape, p=cloud_probabilities)

    # Define the plane position (x-coordinate will be updated in the loop)
    plane_position = [0, cloudData_array.shape[1] // 2]

    # Define the altitude range
    altitudes = range(5, cloudData_array.shape[0] - 5)

    # Initialize lists to store the altitudes and cloud coverages
    altitude_list = []
    cloud_coverage_list = []

    # Define the number of sweeps and the horizontal positions for each sweep as well as the angular view
    angular_view = (75,90)
    num_sweeps = 1
    horizontal_positions = np.linspace(10, cloudData_array.shape[1] - 10, num_sweeps)
    

    # Perform the altitude sweeps
    for pos in horizontal_positions:
        plane_position[1] = int(pos)
        for altitude in altitudes:
            # Update the plane position
            plane_position[0] = altitude

            # Calculate the cloud coverage
            coverage, paths = calculate_cloud_coverage(plane_position, cloudData_array, angular_view)

            # Store the altitude and cloud coverage
            altitude_list.append(altitude)
            cloud_coverage_list.append(coverage)

    # # Create a DataFrame with the results
    # df = pd.DataFrame({
    #     'altitude': altitude_list,
    #     'cloud_coverage': cloud_coverage_list})

    # Convert the lists to arrays
    altitude_array = np.array(altitude_list)
    cloud_coverage_array = np.array(cloud_coverage_list)

    # Reshape the arrays to have a shape of (num_sweeps, len(altitudes))
    altitude_array = altitude_array.reshape(num_sweeps, len(altitudes))
    cloud_coverage_array = cloud_coverage_array.reshape(num_sweeps, len(altitudes))

    # Calculate the average cloud coverage at each altitude
    coverage_list = cloud_coverage_array.mean(axis=0)
    # print(coverageMean.shape)
    # Create a DataFrame with the results
    # df = pd.DataFrame({
    #     'altitude': altitude_array[0, :],
    #     'coverage_mean': coverageMean})


    # Return the DataFrame
    return filename, altitude_list, coverage_list

# df = main()
# print(df.head(10))
# print(df["cloud_coverage"].mean())
