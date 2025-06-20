from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
                           QLabel, QPushButton, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

class ComponentPanel(QWidget):
    component_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent  # Store reference to the main window

        self.init_ui()
        self.populate_components()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Instructions
        instructions = QLabel("Drag & drop components to the canvas")
        layout.addWidget(instructions)

        # Component tree
        self.component_tree = QTreeWidget(self)
        self.component_tree.setHeaderLabel("Network Components")
        self.component_tree.setDragEnabled(True)
        self.component_tree.itemDoubleClicked.connect(self.on_component_double_clicked)

        layout.addWidget(self.component_tree)

        # Add component button
        self.add_button = QPushButton("Add Selected Component")
        self.add_button.clicked.connect(self.on_add_button_clicked)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def populate_components(self):
        # 5G Core components
        core_category = QTreeWidgetItem(self.component_tree, ["5G Core Network"])

        amf_item = QTreeWidgetItem(core_category, ["AMF"])
        amf_item.setData(0, Qt.UserRole, "amf")

        smf_item = QTreeWidgetItem(core_category, ["SMF"])
        smf_item.setData(0, Qt.UserRole, "smf")

        upf_item = QTreeWidgetItem(core_category, ["UPF"])
        upf_item.setData(0, Qt.UserRole, "upf")

        pcf_item = QTreeWidgetItem(core_category, ["PCF"])
        pcf_item.setData(0, Qt.UserRole, "pcf")

        udm_item = QTreeWidgetItem(core_category, ["UDM"])
        udm_item.setData(0, Qt.UserRole, "udm")

        ausf_item = QTreeWidgetItem(core_category, ["AUSF"])
        ausf_item.setData(0, Qt.UserRole, "ausf")

        nrf_item = QTreeWidgetItem(core_category, ["NRF"])
        nrf_item.setData(0, Qt.UserRole, "nrf")

        # RAN components
        ran_category = QTreeWidgetItem(self.component_tree, ["Radio Access Network"])

        gnb_item = QTreeWidgetItem(ran_category, ["gNodeB"])
        gnb_item.setData(0, Qt.UserRole, "gnb")

        ue_item = QTreeWidgetItem(ran_category, ["UE"])
        ue_item.setData(0, Qt.UserRole, "ue")

        # Network components
        network_category = QTreeWidgetItem(self.component_tree, ["Network Infrastructure"])

        switch_item = QTreeWidgetItem(network_category, ["Switch"])
        switch_item.setData(0, Qt.UserRole, "switch")

        router_item = QTreeWidgetItem(network_category, ["Router"])
        router_item.setData(0, Qt.UserRole, "router")

        host_item = QTreeWidgetItem(network_category, ["Host"])
        host_item.setData(0, Qt.UserRole, "host")

        controller_item = QTreeWidgetItem(network_category, ["SDN Controller"])
        controller_item.setData(0, Qt.UserRole, "controller")

        # Expand all categories
        self.component_tree.expandAll()

    def on_component_double_clicked(self, item, column):
        component_type = item.data(0, Qt.UserRole)
        if component_type:
            # Use main_window instead of parent()
            self.main_window.canvas.set_mode("add_component", component_type)

    def on_add_button_clicked(self):
        selected_items = self.component_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            component_type = item.data(0, Qt.UserRole)
            if component_type:
                # Use main_window instead of parent()
                self.main_window.canvas.set_mode("add_component", component_type)