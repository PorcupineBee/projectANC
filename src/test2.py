# from PyQt5.QtWidgets import (
#     QApplication, QTableWidget, QTableWidgetItem, QLabel, QWidget
# )
# from PyQt5.QtGui import QPainter, QFont
# from PyQt5.QtCore import Qt
# import sys

# class VerticalLabel(QLabel):
#     def __init__(self, text='', parent=None):
#         super().__init__(text, parent)
#         self.setMinimumSize(50, 100)  # Adjust as needed

#     def paintEvent(self, event):
#         painter = QPainter(self)
#         painter.translate(0, self.height())
#         # painter.translate(self.width(), self.height())
#         painter.rotate(270)
#         painter.drawText(0, 0, self.height(), self.width(), Qt.AlignCenter, self.text())
#         print("called")
#     def sizeHint(self):
#         hint = super().sizeHint()
#         return hint.transposed()

# app = QApplication(sys.argv)

# table = QTableWidget(4, 4)
# table.setHorizontalHeaderLabels(["A", "B", "C", "D"])

# # Add a vertical label to cell (0, 0)
# vlabel = VerticalLabel("Rotated")
# table.setCellWidget(0, 0, vlabel)

# # Add normal item to compare
# table.setItem(0, 1, QTableWidgetItem("Normal"))

# table.resize(400, 300)
# table.show()

# sys.exit(app.exec_())

# from PyQt5.QtWidgets import (
#     QApplication, QTableWidget, QGraphicsScene, 
#     QGraphicsView, QGraphicsTextItem, QTableWidgetItem
# )
# from PyQt5.QtGui import QFont
# from PyQt5.QtCore import Qt
# import sys

# class RotatedTextView(QGraphicsView):
#     def __init__(self, text, parent=None):
#         super().__init__(parent)
#         self.setRenderHints(self.renderHints())
#         scene = QGraphicsScene(self)
#         self.setScene(scene)

#         text_item = QGraphicsTextItem(text)
#         text_item.setFont(QFont("Arial", 12))
#         text_item.setRotation(90)  # Rotate the text 90 degrees
#         scene.addItem(text_item)

#         # Optional: center the view on the text
#         scene.setSceneRect(text_item.boundingRect())
#         self.setFixedSize(60, 100)  # Adjust based on your needs

# app = QApplication(sys.argv)

# table = QTableWidget(4, 4)
# table.setHorizontalHeaderLabels(["A", "B", "C", "D"])

# # Embed the rotated text in a cell
# rotated_widget = RotatedTextView("Rotated")
# table.setCellWidget(0, 0, rotated_widget)

# # Normal text for comparison
# table.setItem(0, 1, QTableWidgetItem("Normal"))

# table.resize(500, 300)
# table.show()

# sys.exit(app.exec_())


# from PyQt5.QtWidgets import QLabel, QApplication
# from PyQt5.QtGui import QPixmap, QPainter, QFont
# from PyQt5.QtCore import Qt
# import sys

# def create_rotated_pixmap(text):
#     pixmap = QPixmap(200, 100)
#     pixmap.fill(Qt.transparent)

#     painter = QPainter(pixmap)
#     painter.setRenderHint(QPainter.Antialiasing)
#     painter.translate(0, 150)
#     painter.rotate(270)
#     painter.setFont(QFont("Arial", 16))
#     painter.drawText(0, 0, text)
#     painter.end()

#     return pixmap

# app = QApplication(sys.argv)
# label = QLabel()
# label.setPixmap(create_rotated_pixmap("Vertical Text"))
# label.show()
# sys.exit(app.exec_())

#%%
from PyQt5.QtWidgets import QApplication, QTableWidget, QLabel, QTableWidgetItem
from PyQt5.QtGui import QPixmap, QPainter, QFont
from PyQt5.QtCore import Qt
import sys

def create_rotated_text_pixmap(text, font_size=14, width=50, height=100):
    # Create a transparent pixmap
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)

    # Create a painter and rotate text
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setFont(QFont("Arial", font_size))
    
    # Move the origin and rotate
    painter.translate(0, height)
    painter.rotate(270)

    # Draw the text
    painter.drawText(0, 0, height, width, Qt.AlignCenter, text)
    painter.end()

    return pixmap

app = QApplication(sys.argv)

# Create the table
table = QTableWidget(4, 4)
table.setHorizontalHeaderLabels(["A", "B", "C", "D"])

# Create the rotated pixmap label
label = QLabel()
rotated_pixmap = create_rotated_text_pixmap("Rotated")
label.setPixmap(rotated_pixmap)
label.setFixedSize(rotated_pixmap.size())
label.setAlignment(Qt.AlignCenter)

# Set the label as a cell widget
table.setCellWidget(0, 0, label)

# Normal item for comparison
table.setItem(0, 1, QTableWidgetItem("Normal"))

table.resize(500, 300)
table.show()

sys.exit(app.exec_())
