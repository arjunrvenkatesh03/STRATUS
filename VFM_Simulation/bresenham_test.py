def bresenham_line(array, start, end):
    """
    Returns the list of points in the array from start to end using Bresenham's line algorithm.

    :param array: The 2D array in which the line is drawn
    :param start: A tuple representing the start point (x1, y1)
    :param end: A tuple representing the end point (x2, y2)
    :return: A list of tuples representing the pixels along the path
    """

    # Unpack the start and end points
    x1, y1 = start
    x2, y2 = end

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

import numpy as np

# Create a 2D array using numpy
array = np.zeros((10, 10))

# Define the start and end points
start = (9, 0)
end = (7, 9)

# Call the function
points = bresenham_line(array, start, end)

# Print the points
print(points)

