from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt

class DragDropTree(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(2)  # Two columns: Name + Close Button
        self.setHeaderLabels(["Item", ""])  # Header names
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(self.InternalMove)  # Enable reordering
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionBehavior(self.SelectRows)

        self.populate_tree()  # Fill tree with items

    def populate_tree(self):
        """Populate the tree with items and buttons"""
        for i in range(5):
            item = QTreeWidgetItem(self)
            item.setText(0, f"Item {i+1}")  # Set name in first column
            
            # Create Close button
            close_button = QPushButton("X")
            close_button.clicked.connect(lambda _, row=i: self.removeRow(row))
            self.setItemWidget(item, 1, close_button)  # Add button in column 2

    def removeRow(self, row):
        """Removes a row from the tree"""
        if row < self.topLevelItemCount():
            self.takeTopLevelItem(row)  # Remove the row

    def dropEvent(self, event):
        """Handles row reordering with shifting"""
        source_item = self.currentItem()
        drop_pos = self.indexAt(event.pos()).row()

        if source_item and drop_pos != -1:
            source_row = self.indexOfTopLevelItem(source_item)

            if source_row == drop_pos:
                return  # No need to move if dropped at the same position

            # Take out the source item
            self.takeTopLevelItem(source_row)

            # Insert it at the new position
            self.insertTopLevelItem(drop_pos, source_item)

            event.accept()
        else:
            event.ignore()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.tree = DragDropTree()
        layout.addWidget(self.tree)
        self.setLayout(layout)

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()
