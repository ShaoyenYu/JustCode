# Demonstrates how to plot a 3D function in cartesian coordinates.
# Uses the marching cubes algorithm in scikit-image to obtain a isosurface.
# Example contributed by CAChemE.org
# Adapted from: http://www.walkingrandomly.com/?p=2326

# quote from: https://gist.github.com/franktoffel/f79d84319f043c1d3c897f3732489460


import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from skimage import measure

matplotlib.use("TkAgg")

# Set up mesh
n = 100

x = np.linspace(-3, 3, n)
y = np.linspace(-3, 3, n)
z = np.linspace(-3, 3, n)
X, Y, Z = np.meshgrid(x, y, z)


# Create cardioid function
def f_heart(x, y, z):
    F = 320 * ((-x ** 2 * z ** 3 - 9 * y ** 2 * z ** 3 / 80) +
               (x ** 2 + 9 * y ** 2 / 4 + z ** 2 - 1) ** 3)
    return F


# Obtain value to at every point in mesh
vol = f_heart(X, Y, Z)

# Extract a 2D surface mesh from a 3D volume (F=0)
verts, faces, _, _ = measure.marching_cubes(vol, 0, spacing=(0.1, 0.1, 0.1))

# Create a 3D figure
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot the surface
ax.plot_trisurf(verts[:, 0], verts[:, 1], faces, verts[:, 2],
                cmap='Spectral', lw=1)

# Change the angle of view and title
ax.view_init(15, -15)

# ax.set_title(u"Made with ❤ (and Python)", fontsize=15) # if you have Python 3
ax.set_title("Made with ♥ and Python", fontsize=15)

# Show me some love ^^
plt.show()
