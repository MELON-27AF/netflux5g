from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QDockWidget,
                            QToolBar, QMessageBox, QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon

from .canvas import NetworkCanvas
from .component_panel import ComponentPanel
from .property_panel import PropertyPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetFlux5G - 5G Network Topology Designer")
        self.resize(1200, 800)

        self.settings = QSettings()

        self.init_ui()
        self.create_actions()
        self.create_menus()
        self.create_toolbars()
        self.create_statusbar()

        self.load_settings()

    def init_ui(self):
        # Central widget - network canvas
        self.canvas = NetworkCanvas(self)
        self.setCentralWidget(self.canvas)

        # Component panel (left dock)
        self.component_dock = QDockWidget("Network Components", self)
        self.component_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # Pass self (MainWindow) to ComponentPanel
        self.component_panel = ComponentPanel(self)
        self.component_dock.setWidget(self.component_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.component_dock)

        # Properties panel (right dock)
        self.property_dock = QDockWidget("Properties", self)
        self.property_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.property_panel = PropertyPanel(self)
        self.property_dock.setWidget(self.property_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.property_dock)

    def create_actions(self):
        # File actions
        self.new_action = QAction("&New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_project)

        self.open_action = QAction("&Open", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_project)

        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_project)

        self.export_docker_action = QAction("Export to &Docker Compose", self)
        self.export_docker_action.triggered.connect(self.export_to_docker)

        self.export_mininet_action = QAction("Export to &Mininet", self)
        self.export_mininet_action.triggered.connect(self.export_to_mininet)

        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)

        # Simulation actions
        self.simulate_action = QAction("Run &Simulation", self)
        self.simulate_action.setShortcut("F5")
        self.simulate_action.triggered.connect(self.run_simulation)

        # Help actions
        self.about_action = QAction("&About", self)
        self.about_action.triggered.connect(self.show_about)

    def create_menus(self):
        # File menu
        self.file_menu = self.menuBar().addMenu("&File")
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addSeparator()

        # Export submenu
        self.export_menu = self.file_menu.addMenu("&Export")
        self.export_menu.addAction(self.export_docker_action)
        self.export_menu.addAction(self.export_mininet_action)

        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        # Simulation menu
        self.simulation_menu = self.menuBar().addMenu("&Simulation")
        self.simulation_menu.addAction(self.simulate_action)

        # Help menu
        self.help_menu = self.menuBar().addMenu("&Help")
        self.help_menu.addAction(self.about_action)

    def create_toolbars(self):
        # Main toolbar
        self.main_toolbar = self.addToolBar("Main")
        self.main_toolbar.addAction(self.new_action)
        self.main_toolbar.addAction(self.open_action)
        self.main_toolbar.addAction(self.save_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(self.simulate_action)

    def create_statusbar(self):
        self.statusBar().showMessage("Ready")

    def load_settings(self):
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        super().closeEvent(event)

    # Action handlers
    def new_project(self):
        reply = QMessageBox.question(self, "New Project",
                                     "Are you sure you want to create a new project? Unsaved changes will be lost.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.canvas.clear()
            self.statusBar().showMessage("New project created", 3000)

    def open_project(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Project", "", 
                                                 "NetFlux5G Files (*.nfx);;All Files (*)")
        if filename:
            try:
                self.canvas.load_from_file(filename)
                self.statusBar().showMessage(f"Opened {filename}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Open Error", f"Failed to open project: {str(e)}")

    def save_project(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Project", "", 
                                                 "NetFlux5G Files (*.nfx);;All Files (*)")
        if filename:
            try:
                self.canvas.save_to_file(filename)
                self.statusBar().showMessage(f"Saved to {filename}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save project: {str(e)}")

    def export_to_docker(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export to Docker Compose", "", 
                                                 "YAML Files (*.yml *.yaml);;All Files (*)")
        if filename:
            try:
                from export.docker_exporter import DockerExporter
                exporter = DockerExporter(self.canvas)
                exporter.export(filename)
                self.statusBar().showMessage(f"Exported to Docker Compose: {filename}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")

    def export_to_mininet(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export to Mininet", "", 
                                                 "Python Files (*.py);;All Files (*)")
        if filename:
            try:
                from export.mininet_exporter import MininetExporter
                exporter = MininetExporter(self.canvas)
                exporter.export(filename)
                self.statusBar().showMessage(f"Exported to Mininet: {filename}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")

    def run_simulation(self):
        from simulation.simulator import NetworkSimulator

        try:
            simulator = NetworkSimulator(self.canvas)
            result = simulator.run()
            if result:
                self.statusBar().showMessage("Simulation completed successfully", 3000)
            else:
                self.statusBar().showMessage("Simulation completed with errors", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Simulation Error", f"Failed to run simulation: {str(e)}")

    def show_about(self):
        QMessageBox.about(self, "About NetFlux5G",
                         """<b>NetFlux5G</b> v1.0<br><br>
                         A network topology designer for 5G, wireless, and container-based networks.<br><br>
                         Create complex network designs and export them to Docker Compose or Mininet
                         for deployment and testing.<br><br>
                         &copy; 2023 NetFlux Project""")