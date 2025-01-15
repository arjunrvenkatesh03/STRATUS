import matplotlib.pyplot as plt
import numpy as np

def plot_pixels():
    # Define the array size and plane position
    array_size = (200, 200)
    plane_position = (100, 100)

    # Create an array of zeros
    array = np.zeros(array_size)

    # Define the square radius
    radius = 20

    # Define the square boundaries
    x_min = max(0, plane_position[0] - radius)
    x_max = min(array_size[0], plane_position[0] + radius)
    y_min = max(0, plane_position[1] - radius)
    y_max = min(array_size[1], plane_position[1] + radius)

    # Set the value of each pixel on the edge of the square to 1
    array[x_min:x_max, y_min] = 1
    array[x_min:x_max, y_max-1] = 1
    array[x_min, y_min:y_max] = 1
    array[x_max-1, y_min:y_max] = 1

    # Plot the array
    plt.imshow(array, cmap='gray')
    plt.show()

# Call the function to execute the code
plot_pixels()