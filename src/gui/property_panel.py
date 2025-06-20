from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit,
                            QComboBox, QSpinBox, QPushButton, QLabel,
                            QScrollArea, QGroupBox)
from PyQt5.QtCore import Qt

class PropertyPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_component = None
        self.property_widgets = {}

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel("Properties")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)

        # Scrollable property area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.property_container = QWidget()
        self.property_layout = QFormLayout(self.property_container)
        scroll.setWidget(self.property_container)

        layout.addWidget(scroll)

        # Apply button
        self.apply_button = QPushButton("Apply Changes")
        self.apply_button.clicked.connect(self.apply_properties)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)

        # Show initial empty state
        self.show_empty_state()

    def show_empty_state(self):
        self.title_label.setText("Properties")
        self.clear_properties()

        label = QLabel("Select a component to edit its properties")
        label.setAlignment(Qt.AlignCenter)
        self.property_layout.addRow(label)

        self.apply_button.setEnabled(False)

    def clear_properties(self):
        # Clear all widgets from the property layout
        while self.property_layout.count():
            item = self.property_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.property_widgets = {}

    def edit_component(self, component):
        self.current_component = component
        self.title_label.setText(f"Properties: {component.component_type}")

        self.clear_properties()

        # Get component properties
        properties = component.get_properties()

        # Basic properties group
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout(basic_group)

        # ID field
        id_edit = QLineEdit(component.component_id)
        id_edit.setReadOnly(True)  # ID cannot be changed
        basic_layout.addRow("ID:", id_edit)

        # Name field
        name_edit = QLineEdit(properties.get("name", ""))
        self.property_widgets["name"] = name_edit
        basic_layout.addRow("Name:", name_edit)

        # Add the basic group to main layout
        self.property_layout.addRow(basic_group)

        # Component-specific properties
        specific_group = QGroupBox(f"{component.component_type} Properties")
        specific_layout = QFormLayout(specific_group)

        # Add specific properties based on component type
        if component.component_type == "amf":
            # AMF specific properties
            capacity = QSpinBox()
            capacity.setRange(1, 1000)
            capacity.setValue(properties.get("capacity", 100))
            self.property_widgets["capacity"] = capacity
            specific_layout.addRow("Capacity:", capacity)

            region = QLineEdit(properties.get("region", "region1"))
            self.property_widgets["region"] = region
            specific_layout.addRow("Region:", region)

        elif component.component_type == "smf":
            # SMF specific properties
            upf_selection = QComboBox()
            upf_selection.addItems(["local", "regional", "central"])
            upf_selection.setCurrentText(properties.get("upf_selection", "local"))
            self.property_widgets["upf_selection"] = upf_selection
            specific_layout.addRow("UPF Selection:", upf_selection)

        elif component.component_type == "upf":
            # UPF specific properties
            datapath = QLineEdit(properties.get("datapath", ""))
            self.property_widgets["datapath"] = datapath
            specific_layout.addRow("Datapath ID:", datapath)

            capacity = QSpinBox()
            capacity.setRange(1, 10000)
            capacity.setValue(properties.get("capacity", 1000))
            self.property_widgets["capacity"] = capacity
            specific_layout.addRow("Capacity (Mbps):", capacity)

        elif component.component_type == "gnb":
            # gNB specific properties
            tac = QSpinBox()
            tac.setRange(1, 65535)
            tac.setValue(properties.get("tac", 1))
            self.property_widgets["tac"] = tac
            specific_layout.addRow("TAC:", tac)

            frequency = QComboBox()
            frequency.addItems(["FR1", "FR2"])
            frequency.setCurrentText(properties.get("frequency", "FR1"))
            self.property_widgets["frequency"] = frequency
            specific_layout.addRow("Frequency Range:", frequency)

            power = QSpinBox()
            power.setRange(1, 100)
            power.setValue(properties.get("power", 20))
            self.property_widgets["power"] = power
            specific_layout.addRow("Power (dBm):", power)

        elif component.component_type == "ue":
            # UE specific properties
            imsi = QLineEdit(properties.get("imsi", "001010000000001"))
            self.property_widgets["imsi"] = imsi
            specific_layout.addRow("IMSI:", imsi)

            k = QLineEdit(properties.get("k", "465B5CE8B199B49FAA5F0A2EE238A6BC"))
            self.property_widgets["k"] = k
            specific_layout.addRow("K:", k)

            opc = QLineEdit(properties.get("opc", "E8ED289DEBA952E4283B54E88E6183CA"))
            self.property_widgets["opc"] = opc
            specific_layout.addRow("OPC:", opc)

        elif component.component_type == "switch" or component.component_type == "router":
            # Switch/Router specific properties
            openflow = QComboBox()
            openflow.addItems(["True", "False"])
            openflow.setCurrentText(str(properties.get("openflow", True)))
            self.property_widgets["openflow"] = openflow
            specific_layout.addRow("OpenFlow:", openflow)

            dp_id = QLineEdit(properties.get("dp_id", ""))
            self.property_widgets["dp_id"] = dp_id
            specific_layout.addRow("Datapath ID:", dp_id)

        elif component.component_type == "host":
            # Host specific properties
            ip = QLineEdit(properties.get("ip", ""))
            self.property_widgets["ip"] = ip
            specific_layout.addRow("IP Address:", ip)

            default_gw = QLineEdit(properties.get("default_gw", ""))
            self.property_widgets["default_gw"] = default_gw
            specific_layout.addRow("Default Gateway:", default_gw)

        elif component.component_type == "controller":
            # Controller specific properties
            controller_type = QComboBox()
            controller_type.addItems(["ODL", "ONOS", "Ryu", "Floodlight"])
            controller_type.setCurrentText(properties.get("controller_type", "ODL"))
            self.property_widgets["controller_type"] = controller_type
            specific_layout.addRow("Controller Type:", controller_type)

            port = QSpinBox()
            port.setRange(1, 65535)
            port.setValue(properties.get("port", 6653))
            self.property_widgets["port"] = port
            specific_layout.addRow("Port:", port)

        # Add the specific group to main layout if it has any rows
        if specific_layout.rowCount() > 0:
            specific_group.setLayout(specific_layout)
            self.property_layout.addRow(specific_group)
        else:
            specific_group.deleteLater()

        # Enable the apply button
        self.apply_button.setEnabled(True)

    def apply_properties(self):
        if not self.current_component:
            return

        # Collect property values from widgets
        properties = {}
        for key, widget in self.property_widgets.items():
            if isinstance(widget, QLineEdit):
                properties[key] = widget.text()
            elif isinstance(widget, QSpinBox):
                properties[key] = widget.value()
            elif isinstance(widget, QComboBox):
                properties[key] = widget.currentText()

        # Apply properties to the component
        self.current_component.set_properties(properties)

        # Update the canvas
        self.parent().canvas.scene.update()