from PyQt5.QtWidgets import QGraphicsLineItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QColor

class NetworkLink(QGraphicsLineItem):
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
        self.properties = {}

        # Set appearance
        self.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))
        self.setZValue(-1)  # Ensure links are drawn below components

        # Update the line position
        self.update_position()

    def update_position(self):
        # Update the line to connect the two components
        self.setLine(
            self.source.pos().x(), self.source.pos().y(),
            self.target.pos().x(), self.target.pos().y()
        )

    def get_properties(self):
        return self.properties

    def set_properties(self, properties):
        self.properties.update(properties)

        # Update appearance based on properties
        if "bandwidth" in properties:
            # Adjust line width based on bandwidth
            width = 1 + min(5, int(properties["bandwidth"]) // 100)
            pen = self.pen()
            pen.setWidth(width)
            self.setPen(pen)