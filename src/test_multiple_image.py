import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
import numpy as np

# Create the application
app = QtWidgets.QApplication([])

# Create a window with GraphicsLayoutWidget
win = pg.GraphicsLayoutWidget()
win.setWindowTitle('Multiple Images in Single ViewBox')
win.resize(800, 600)

# Create the layout
layout = win  # GraphicsLayoutWidget already contains a GraphicsLayout

# Create a single ViewBox
view_box = layout.addViewBox()
view_box.setAspectLocked(True)

# Create a few different sample images as numpy arrays
img1 = np.random.normal(-1, 1, size=(100, 100))
img2 = np.random.normal(-1, 1, size=(100, 100))
img3 = np.random.normal(-1, 1, size=(100, 100))
img3[40:60, 40:60] = 1  # Create a white square

# Create ImageItem objects
img_item1 = pg.ImageItem(img1)
img_item2 = pg.ImageItem(img2)
img_item3 = pg.ImageItem(img3)

# Position the images side by side
img_item1.setPos(0, 0)       # First image at origin
img_item2.setPos(100, 0)     # Second image to the right
img_item3.setPos(200, 0)     # Third image below the first

# Add all image items to the same ViewBox
view_box.addItem(img_item1)
view_box.addItem(img_item2)
view_box.addItem(img_item3)

# Optionally add text labels for each image
label1 = pg.TextItem("Image 1")
label2 = pg.TextItem("Image 2")
label3 = pg.TextItem("Image 3")

label1.setPos(50, -10)
label2.setPos(150, -10)
label3.setPos(50, 200)

view_box.addItem(label1)
view_box.addItem(label2)
view_box.addItem(label3)

# Auto-range to show all items
view_box.autoRange()

# Show the window
win.show()

# Start the Qt event loop
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtWidgets, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()