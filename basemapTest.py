from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

# Create a new figure
fig = plt.figure()

# Define a basemap with orthographic projection centered on lat_0=0, lon_0=0.
m = Basemap(projection='ortho', lat_0=32, lon_0=138)

# Draw coastlines
m.drawcoastlines(linewidth=0.5)

# Draw a land-sea mask
m.drawlsmask(land_color='coral', ocean_color='aqua', lakes=True)

# Display the satellite image with reduced alpha
m.bluemarble(alpha=0.7)

# Show the plot
plt.show()
