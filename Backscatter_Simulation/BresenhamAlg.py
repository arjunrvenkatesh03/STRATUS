#file to read data array and use bresenhams line algorithm to find what pixels are in the line
import numpy as np

def bresenham_line(x0, y0, x1, y1):
    """
    Bresenham's line algorithm implementation.
    Returns a list of coordinates representing the line.
    """
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    steep = dy > dx
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
    dy = abs(y1 - y0)
    err = 0
    y = y0
    ystep = 1 if y0 < y1 else -1
    line = []
    for x in range(x0, x1 + 1):
        coord = (y, x) if steep else (x, y)
        line.append(coord)
        err += dy
        if 2 * err >= dx:
            y += ystep
            err -= dx
    return line


# array = [[0] * 10 for _ in range(10)]  # Replace with your 2D array
# start = (2, 3)  # Starting point
# end = (8, 6)  # Ending point

# line_pixels = bresenham_line(start[0], start[1], end[0], end[1])
# print(line_pixels)