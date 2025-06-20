from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem,
                            QMenu, QAction, QMessageBox)
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor

import json
import yaml
from models.network_component import NetworkComponent

class NetworkCanvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Canvas settings
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        # Network components
        self.components = []
        self.links = []

        # Selection mode
        self.current_mode = "select"  # "select", "add_component", "add_link"
        self.current_component_type = None

        # Link drawing
        self.temp_link_start = None
        self.temp_link = None

        # Initialize the canvas
        self.init_canvas()

    def init_canvas(self):
        # Set scene size (can be adjusted later)
        self.scene.setSceneRect(QRectF(0, 0, 5000, 5000))

        # Draw grid
        self.draw_grid()

    def draw_grid(self):
        # Draw a grid on the canvas
        grid_size = 20
        grid_pen = QPen(QColor(230, 230, 230))

        for x in range(0, int(self.scene.width()), grid_size):
            self.scene.addLine(x, 0, x, self.scene.height(), grid_pen)

        for y in range(0, int(self.scene.height()), grid_size):
            self.scene.addLine(0, y, self.scene.width(), y, grid_pen)

    def set_mode(self, mode, component_type=None):
        self.current_mode = mode
        self.current_component_type = component_type

        if mode == "select":
            self.setCursor(Qt.ArrowCursor)
        elif mode == "add_component":
            self.setCursor(Qt.CrossCursor)
        elif mode == "add_link":
            self.setCursor(Qt.CrossCursor)

    def add_component(self, component_type, position):
        from models.component_factory import ComponentFactory

        factory = ComponentFactory()
        component = factory.create_component(component_type, position)

        if component:
            self.scene.addItem(component)
            self.components.append(component)
            return component
        return None

    def add_link(self, source, target):
        from models.network_link import NetworkLink

        link = NetworkLink(source, target)
        self.scene.addItem(link)
        self.links.append(link)

        # Associate the link with the components
        source.add_link(link)
        target.add_link(link)

        return link

    def clear(self):
        self.scene.clear()
        self.components.clear()
        self.links.clear()
        self.draw_grid()

    def save_to_file(self, filename):
        data = {
            "components": [],
            "links": []
        }

        # Save components
        for component in self.components:
            component_data = {
                "id": component.component_id,
                "type": component.component_type,
                "x": component.pos().x(),
                "y": component.pos().y(),
                "properties": component.get_properties()
            }
            data["components"].append(component_data)

        # Save links
        for link in self.links:
            link_data = {
                "source_id": link.source.component_id,
                "target_id": link.target.component_id,
                "properties": link.get_properties()
            }
            data["links"].append(link_data)

        # Save to file
        with open(filename, 'w') as file:
            if filename.endswith('.json'):
                json.dump(data, file, indent=2)
            else:
                yaml.dump(data, file)

    def load_from_file(self, filename):
        # Clear existing network
        self.clear()

        # Load from file
        with open(filename, 'r') as file:
            if filename.endswith('.json'):
                data = json.load(file)
            else:
                data = yaml.safe_load(file)

        # Process components
        component_map = {}  # Map component_id to component object
        from models.component_factory import ComponentFactory
        factory = ComponentFactory()

        for component_data in data.get("components", []):
            component_type = component_data.get("type")
            pos = QPointF(component_data.get("x", 0), component_data.get("y", 0))

            component = factory.create_component(component_type, pos)
            if component:
                component.component_id = component_data.get("id")
                component.set_properties(component_data.get("properties", {}))
                self.scene.addItem(component)
                self.components.append(component)
                component_map[component.component_id] = component

        # Process links
        for link_data in data.get("links", []):
            source_id = link_data.get("source_id")
            target_id = link_data.get("target_id")

            if source_id in component_map and target_id in component_map:
                source = component_map[source_id]
                target = component_map[target_id]

                link = self.add_link(source, target)
                link.set_properties(link_data.get("properties", {}))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())

            if self.current_mode == "add_component" and self.current_component_type:
                self.add_component(self.current_component_type, scene_pos)

            elif self.current_mode == "add_link":
                item = self.scene.itemAt(scene_pos, self.transform())
                if isinstance(item, NetworkComponent):
                    if self.temp_link_start is None:
                        # Start drawing a link
                        self.temp_link_start = item
                        self.temp_link = self.scene.addLine(
                            item.pos().x(), item.pos().y(),
                            scene_pos.x(), scene_pos.y(), 
                            QPen(Qt.DashLine)
                        )
                    else:
                        # Finish the link
                        if item != self.temp_link_start:  # Can't link to itself
                            self.add_link(self.temp_link_start, item)

                        # Clean up temporary link
                        if self.temp_link:
                            self.scene.removeItem(self.temp_link)
                            self.temp_link = None
                        self.temp_link_start = None

        # Continue with standard event handling
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.current_mode == "add_link" and self.temp_link_start:
            scene_pos = self.mapToScene(event.pos())
            # Update temporary link end point
            self.temp_link.setLine(
                self.temp_link_start.pos().x(), self.temp_link_start.pos().y(),
                scene_pos.x(), scene_pos.y()
            )

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        item = self.scene.itemAt(scene_pos, self.transform())

        menu = QMenu(self)

        if item and isinstance(item, NetworkComponent):
            # Component-specific menu
            menu.addAction("Edit Properties").triggered.connect(
                lambda: self.parent().property_panel.edit_component(item)
            )
            menu.addSeparator()
            menu.addAction("Delete").triggered.connect(
                lambda: self.delete_component(item)
            )
        else:
            # Canvas menu
            menu.addAction("Paste").triggered.connect(self.paste_component)
            select_action = menu.addAction("Select Mode")
            select_action.setCheckable(True)
            select_action.setChecked(self.current_mode == "select")
            select_action.triggered.connect(lambda: self.set_mode("select"))

            link_action = menu.addAction("Add Link Mode")
            link_action.setCheckable(True)
            link_action.setChecked(self.current_mode == "add_link")
            link_action.triggered.connect(lambda: self.set_mode("add_link"))

        menu.exec_(event.globalPos())

    def delete_component(self, component):
        # Remove all links connected to this component
        links_to_remove = component.get_links()
        for link in links_to_remove:
            link.source.remove_link(link)
            link.target.remove_link(link)
            self.scene.removeItem(link)
            self.links.remove(link)

        # Remove the component
        self.scene.removeItem(component)
        self.components.remove(component)

    def paste_component(self):
        # Implement clipboard functionality if needed
        pass

    def wheelEvent(self, event):
        # Zoom in/out with mouse wheel
        zoom_factor = 1.2

        if event.angleDelta().y() > 0:
            # Zoom in
            self.scale(zoom_factor, zoom_factor)
        else:
            # Zoom out
            self.scale(1.0 / zoom_factor, 1.0 / zoom_factor)