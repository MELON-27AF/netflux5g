from PyQt5.QtGui import QColor
from models.network_component import NetworkComponent
import os

class ComponentFactory:
    def __init__(self):
        # Define component type to color mapping
        self.component_colors = {
            # 5G Core
            "amf": QColor(100, 200, 255),  # Light blue
            "smf": QColor(100, 230, 255),
            "upf": QColor(100, 255, 255),
            "pcf": QColor(150, 200, 255),
            "udm": QColor(150, 230, 255),
            "ausf": QColor(150, 255, 255),
            "nrf": QColor(200, 200, 255),

            # RAN
            "gnb": QColor(100, 255, 100),  # Light green
            "ue": QColor(150, 255, 150),

            # Network
            "switch": QColor(255, 200, 100),  # Light orange
            "router": QColor(255, 150, 100),
            "host": QColor(255, 255, 100),  # Light yellow
            "controller": QColor(255, 100, 100),  # Light red
        }
        
        # Define component type to icon mapping
        # Use absolute path for icons instead of relative path
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        base_icon_path = os.path.join(current_dir, "src", "assets", "icons")
        
        # Alternative direct path if above doesn't work
        # base_icon_path = os.path.join(current_dir, "assets", "icons")
        
        self.component_icons = {
            # 5G Core
            "amf": os.path.join(base_icon_path, "5G core.png"),
            "smf": os.path.join(base_icon_path, "5G core.png"),
            "upf": os.path.join(base_icon_path, "5G core.png"),
            "pcf": os.path.join(base_icon_path, "5G core.png"),
            "udm": os.path.join(base_icon_path, "5G core.png"),
            "ausf": os.path.join(base_icon_path, "5G core.png"),
            "nrf": os.path.join(base_icon_path, "5G core.png"),
            
            # RAN
            "gnb": os.path.join(base_icon_path, "gNB.png"),
            "ue": os.path.join(base_icon_path, "ue.png"),
            
            # Network
            "switch": os.path.join(base_icon_path, "switch.png"),
            "router": os.path.join(base_icon_path, "Router.png"),
            "host": os.path.join(base_icon_path, "host.png"),
            "controller": os.path.join(base_icon_path, "controller.png"),
        }
        
        # Verify that icon files exist
        for component_type, icon_path in self.component_icons.items():
            if not os.path.exists(icon_path):
                print(f"Warning: Icon for {component_type} not found at {icon_path}")

    def create_component(self, component_type, position):
        """
        Factory method to create network components by type.
        """
        if component_type not in self.component_colors:
            return None

        # Create the base component
        component = NetworkComponent(component_type, position)

        # Set component-specific properties
        component.color = self.component_colors[component_type]
        
        # Set component icon
        if component_type in self.component_icons:
            component.set_icon(self.component_icons[component_type])

        # Set type-specific default properties
        if component_type == "amf":
            component.properties.update({
                "capacity": 100,
                "region": "region1"
            })
        elif component_type == "smf":
            component.properties.update({
                "upf_selection": "local"
            })
        elif component_type == "upf":
            component.properties.update({
                "capacity": 1000
            })
        elif component_type == "gnb":
            component.properties.update({
                "tac": 1,
                "frequency": "FR1",
                "power": 20
            })
        elif component_type == "ue":
            component.properties.update({
                "imsi": "001010000000001",
                "k": "465B5CE8B199B49FAA5F0A2EE238A6BC",
                "opc": "E8ED289DEBA952E4283B54E88E6183CA"
            })
        elif component_type in ["switch", "router"]:
            component.properties.update({
                "openflow": True
            })
        elif component_type == "controller":
            component.properties.update({
                "controller_type": "ODL",
                "port": 6653
            })

        return component