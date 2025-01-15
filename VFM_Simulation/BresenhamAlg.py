import numpy as np
from numba import njit

#GPT$ generated code for Bresenhams line algorithm to see what voxels are in the path of the laser
@njit
def bresenham_line(array,pair):
    """
    Returns the list of points in the array from start to end using Bresenham's line algorithm.

    :param array: The 2D array in which the line is drawn
    :param start: A tuple representing the start point (x1, y1)
    :param end: A tuple representing the end point (x2, y2)
    :return: A list of tuples representing the pixels along the path
    """

    x1, y1 = pair[0]
    x2, y2 = pair[1]
    # Get the size of the array
    height, width = array.shape
    # Initialize the list of points
    points = []
    # Bresenham's line algorithm
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = -1 if x1 > x2 else 1
    sy = -1 if y1 > y2 else 1
    if dx > dy:
        err = dx / 2.0
        while x1 != x2:
            if 0 <= x1 < width and 0 <= y1 < height:
                points.append((x1, y1))
            err -= dy
            if err < 0:
                y1 += sy
                err += dx
            x1 += sx
    else:
        err = dy / 2.0
        while y1 != y2:
            if 0 <= x1 < width and 0 <= y1 < height:
                points.append((x1, y1))
            err -= dx
            if err < 0:
                x1 += sx
                err += dy
            y1 += sy
            
               
    # Include the last point, if it's inside the array
    if 0 <= x1 < width and 0 <= y1 < height:
        points.append((x1, y1))

    return points

array = np.zeros((10155,1020))

@njit
def is_clear_path(array,pair):
    points = bresenham_line(array,pair)
    for point in points:
        if array[point[0], point[1]] == 1:
            return True
    return False
# pair = [(393,487),(4867,789)]
# print(is_clear_path(array,pair))



# #GPT4 generate code for Bresenhams line algorithm to see what voxels are in the path of the laser and saves the value stored in the voxel
# def bresenham_3D(start, end):
#     # Bresenham's line algorithm in 3D
#     x1, y1, z1 = start
#     x2, y2, z2 = end
#     points = []
#     dx, dy, dz = abs(x2 - x1), abs(y2 - y1), abs(z2 - z1)
#     xs = 1 if x2 > x1 else -1
#     ys = 1 if y2 > y1 else -1
#     zs = 1 if z2 > z1 else -1

#     # Driving axis is X-axis
#     if dx >= dy and dx >= dz:
#         p1 = 2 * dy - dx
#         p2 = 2 * dz - dx
#         while x1 != x2:
#             x1 += xs
#             if p1 >= 0:
#                 y1 += ys
#                 p1 -= 2 * dx
#             if p2 >= 0:
#                 z1 += zs
#                 p2 -= 2 * dx
#             p1 += 2 * dy
#             p2 += 2 * dz
#             points.append((x1, y1, z1))

#     # Driving axis is Y-axis
#     elif dy >= dx and dy >= dz:
#         p1 = 2 * dx - dy
#         p2 = 2 * dz - dy
#         while y1 != y2:
#             y1 += ys
#             if p1 >= 0:
#                 x1 += xs
#                 p1 -= 2 * dy
#             if p2 >= 0:
#                 z1 += zs
#                 p2 -= 2 * dy
#             p1 += 2 * dx
#             p2 += 2 * dz
#             points.append((x1, y1, z1))

#     # Driving axis is Z-axis
#     else:
#         p1 = 2 * dy - dz
#         p2 = 2 * dx - dz
#         while z1 != z2:
#             z1 += zs
#             if p1 >= 0:
#                 y1 += ys
#                 p1 -= 2 * dz
#             if p2 >= 0:
#                 x1 += xs
#                 p2 -= 2 * dz
#             p1 += 2 * dy
#             p2 += 2 * dx
#             points.append((x1, y1, z1))

#     return points




# #generate a 3D matrix of 0s and 1s to represent the voxels
# matrix = np.random.randint(0, 14, (100, 100, 100))

# print(voxels_in_path(matrix, (0, 0, 0), (78,55,23)))
# #Note running this code with the random matrix generated above works! Have yet to test with the actual data
