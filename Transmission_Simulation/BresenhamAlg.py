import numpy as np
from numba import njit

@njit
def bezier_curve(pair, scale_x=0.333, scale_y=5, offset=10):
    start, end = pair
    x0, y0 = start
    x2, y2 = end

    # Calculate the number of points based on the distance between start and end
    num_points = int(np.sqrt((x0 - x2) ** 2 + (y0 - y2) ** 2))

    # Skip processing if path length is less than 3
    if num_points < 3:
        return np.empty((0, 2), dtype=np.int32)  # Return an empty array

    # Initialize a NumPy array for points
    points = np.empty((num_points, 2), dtype=np.int32)

    # Calculate control point for the Bezier curve, considering the offset for Earth's curvature
    P0_scaled = (start[0] * scale_x, start[1] * scale_y)
    P2_scaled = (end[0] * scale_x, end[1] * scale_y)
    Mx_scaled, My_scaled = (P0_scaled[0] + P2_scaled[0]) / 2.0, (P0_scaled[1] + P2_scaled[1]) / 2.0
    P1x_scaled = Mx_scaled
    P1y_scaled = My_scaled - abs(offset)
    P1 = (P1x_scaled / scale_x, P1y_scaled / scale_y)

    x1, y1 = P1
    point_count = 0

    for i in range(num_points):
        t = i / (num_points - 1)
        xt = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t ** 2 * x2
        yt = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t ** 2 * y2
        x, y = int(round(xt)), int(round(yt))
        
        points[point_count] = [x,y]  # Store points in the array
        point_count += 1

    return points[:point_count]  # Return only the populated part of the array

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

#     return points

# pair = ((163, 9), (183, 12))
# array = np.ones((399,17))
# points = bresenham_line(array, pair)
# print(points)
# print(len(points))

# pair = ((163, 9), (183, 12))
# array = np.ones((399,17))
# points = bresenham_line(array,pair)
# print(points)
# pair = [(393,487),(4867,789)]
# print(is_clear_path(array,pair))
# @njit
# def bresenham_line(array,pair):
#     """
#     Returns the list of points in the array from start to end using Bresenham's line algorithm.

#     :param array: The 2D array in which the line is drawn
#     :param start: A tuple representing the start point (x1, y1)
#     :param end: A tuple representing the end point (x2, y2)
#     :return: A list of tuples representing the pixels along the path
#     """

#     x1, y1 = pair[0]
#     x2, y2 = pair[1]

#     # Get the size of the array
#     height, width = array.shape

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
#                 points.append((x1, y1))
#             err -= dy
#             if err < 0:
#                 y1 += sy
#                 err += dx
#             x1 += sx
#     else:
#         err = dy / 2.0
#         while y1 != y2:
#             if 0 <= x1 < width and 0 <= y1 < height:
#                 points.append((x1, y1))
#             err -= dx
#             if err < 0:
#                 x1 += sx
#                 err += dy
#             y1 += sy
            
#     # Include the last point, if it's inside the array
#     if 0 <= x1 < width and 0 <= y1 < height:
#         points.append((x1, y1))

#     return points


# # array = [[0] * 10 for _ in range(10)]  # Replace with your 2D array
# # start = (2, 3)  # Starting point
# # end = (8, 6)  # Ending point

# # line_pixels = bresenham_line(start[0], start[1], end[0], end[1])
# # print(line_pixels)