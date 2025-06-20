from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPixmap

import uuid
import os

class NetworkComponent(QGraphicsItem):
    def __init__(self, component_type, position):
        super().__init__()
        self.component_type = component_type
        self.component_id = str(uuid.uuid4())[:8]
        self.properties = {"name": f"{component_type}_{self.component_id}"}
        self.links = []

        # Graphics settings
        self.width = 100
        self.height = 80
        self.color = QColor(200, 200, 255)
        self.selected_color = QColor(255, 255, 0)
        
        # Icon property
        self.icon_path = None
        self.icon_pixmap = None
        self.icon_size = 32  # Default icon size

        # Set position and flags
        self.setPos(position)
        self.setFlags(QGraphicsItem.ItemIsSelectable |
                     QGraphicsItem.ItemIsMovable |
                     QGraphicsItem.ItemSendsGeometryChanges)

    def set_icon(self, icon_path):
        """Set the icon for this component"""
        self.icon_path = icon_path
        if icon_path and os.path.exists(icon_path):
            self.icon_pixmap = QPixmap(icon_path)
        else:
            self.icon_pixmap = None
        self.update()  # Redraw component with the icon

    def boundingRect(self):
        return QRectF(-self.width/2, -self.height/2, self.width, self.height)

    def paint(self, painter, option, widget):
        # Only draw selection indicator if selected
        if self.isSelected():
            pen = QPen(Qt.yellow, 2, Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.boundingRect())
        
        # Draw icon if available
        if self.icon_pixmap:
            icon_x = -self.icon_size/2
            icon_y = -self.height/2 + 5  # Position icon at top with small padding
            # Create a QRectF for the icon position and size
            icon_rect = QRectF(icon_x, icon_y, self.icon_size, self.icon_size)
            # Draw pixmap with a target rectangle
            painter.drawPixmap(icon_rect, self.icon_pixmap, QRectF(self.icon_pixmap.rect()))
        
        # Draw component name below the icon for identification
        painter.setFont(QFont("Arial", 8))
        name = self.properties.get("name", f"{self.component_type}_{self.component_id}")
        name_rect = QRectF(-self.width/2, self.icon_size + 5, self.width, 20)
        painter.drawText(name_rect, Qt.AlignCenter, name)

    def itemChange(self, change, value):
        # Update connected links when component moves
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            for link in self.links:
                link.update_position()

        return super().itemChange(change, value)

    def add_link(self, link):
        if link not in self.links:
            self.links.append(link)

    def remove_link(self, link):
        if link in self.links:
            self.links.remove(link)

    def get_links(self):
        return self.links

    def get_properties(self):
        return self.properties

    def set_properties(self, properties):
        self.properties.update(properties)
        self.update()  # Redraw component with new properties