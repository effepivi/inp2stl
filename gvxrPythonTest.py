#!/usr/bin/env python3

import os
import numpy as np
dir_path = os.path.dirname(os.path.realpath(__file__))

# Use Matplotlib
try:
    import matplotlib
    matplotlib.use("TkAgg")

    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    from matplotlib.colors import PowerNorm
    use_matplotlib = True;
except ImportError:
    print("Matplotlib is not installed. Try to install it if you want to display and plot data.")
    use_matplotlib = False;

import gvxrPython3 as gvxr


# Print the libraries' version
print (gvxr.getVersionOfSimpleGVXR())
print (gvxr.getVersionOfCoreGVXR())

# Create the subplot first
# If called later, it crashes on my Macbook Pro
if use_matplotlib:
    plt.subplot(131)

# Create an OpenGL context
print("Create a OpenGL context")
gvxr.createWindow(0, 1, "OPENGL");
gvxr.setWindowSize(512, 512);



# Load the data
print("Load the data");
#gvxr.loadSceneGraph("DogBone.stl", "m");

gvxr.loadMeshFile("male_model",
                  "male_model-bin.stl",
                  "mm")

gvxr.setHU("male_model", 1000);


min_corner = None;
max_corner = None;

NoneType = type(None);


# Process every node
for i in range(gvxr.getNumberOfChildren('root')):
    # Get the label
    label = gvxr.getChildLabel('root', i);

    # Update the bounding box
    if isinstance(min_corner, NoneType):
        min_corner = np.array(gvxr.getNodeOnlyBoundingBox(label, "cm")[0:3]);
    else:
        current_min_corner = np.array(gvxr.getNodeOnlyBoundingBox(label, "cm")[0:3]);
        min_corner[0] = min(min_corner[0], current_min_corner[0]);
        min_corner[1] = min(min_corner[1], current_min_corner[1]);
        min_corner[2] = min(min_corner[2], current_min_corner[2]);

    if isinstance(max_corner, NoneType):
        max_corner = np.array(gvxr.getNodeOnlyBoundingBox(label, "cm")[3:6]);
    else:
        current_max_corner = np.array(gvxr.getNodeOnlyBoundingBox(label, "cm")[3:6]);
        max_corner[0] = max(max_corner[0], current_max_corner[0]);
        max_corner[1] = max(max_corner[1], current_max_corner[1]);
        max_corner[2] = max(max_corner[2], current_max_corner[2]);



    print("Bounding box of ", label, " is ", gvxr.getNodeOnlyBoundingBox(label, "mm"), " in mm");

    #print("Move ", label, " to the centre");
    #gvxr.moveToCentre(label);
    #print("Bounding box of ", label, " is ", gvxr.getNodeOnlyBoundingBox(label, "mm"), " in mm");

    #print("Move the mesh to the center");
    #gvxr.moveToCenter(label);

    # print("Set ", label, "'s Hounsfield unit");
    # gvxr.setHU(label, 1000);


centre = [min_corner[0] + (max_corner[0] - min_corner[0]) / 2.0,
    min_corner[1] + (max_corner[1] - min_corner[1]) / 2.0,
    min_corner[2] + (max_corner[2] - min_corner[2]) / 2.0];

# Set up the beam
print("Set up the beam")
gvxr.setSourcePosition(centre[0], centre[1], centre[2] - 10.0, "cm");
gvxr.usePointSource();
#gvxr.useParallelBeam();
gvxr.setMonoChromatic(0.08, "MeV", 1000);

# Set up the detector
print("Set up the detector");
gvxr.setDetectorPosition(centre[0], centre[1], centre[2] + 10.0, "cm");
gvxr.setDetectorUpVector(0, -1, 0);
gvxr.setDetectorNumberOfPixels(640, 320);
gvxr.setDetectorPixelSize(0.125, 0.125, "mm");



# Compute an X-ray image
print("Compute an X-ray image");
gvxr.disableArtefactFiltering();
# Not working anymore gvxr.enableArtefactFilteringOnGPU();
# Not working anymore gvxr.enableArtefactFilteringOnCPU();
x_ray_image = gvxr.computeXRayImage();

# Save the last image into a file
print("Save the last image into a file");
gvxr.saveLastXRayImage();
gvxr.saveLastLBuffer();

# Display the image with Matplotlib
if use_matplotlib:
    plt.imshow(x_ray_image, cmap="gray");
    plt.colorbar(orientation='horizontal');
    plt.title("Using a linear colour scale");

    plt.subplot(132)
    plt.imshow(x_ray_image, norm=LogNorm(), cmap="gray");
    plt.colorbar(orientation='horizontal');
    plt.title("Using a log colour scale");

    plt.subplot(133)
    plt.imshow(x_ray_image, norm=PowerNorm(gamma=1./2.), cmap="gray");
    plt.colorbar(orientation='horizontal');
    plt.title("Using a Power-law colour scale");

    plt.show();

# Display the 3D scene (no event loop)
gvxr.displayScene();

# Display the 3D scene (no event loop)
# Run an interactive loop
# (can rotate the 3D scene and zoom-in)
# Keys are:
# Q/Escape: to quit the event loop (does not close the window)
# B: display/hide the X-ray beam
# W: display the polygon meshes in solid or wireframe
# N: display the X-ray image in negative or positive
# H: display/hide the X-ray detector
gvxr.renderLoop();
