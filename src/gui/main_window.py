from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QDockWidget,
                            QToolBar, QMessageBox, QVBoxLayout, QWidget, QMenu,
                            QDialog, QTextEdit, QTabWidget, QLabel, QGridLayout)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon

from .canvas import NetworkCanvas
from .component_panel import ComponentPanel
from .property_panel import PropertyPanel
from .toolbar import TemplateToolBar
from simulation.simulator import NetworkSimulator

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
        
        # Template actions
        self.load_5g_core_template = QAction("5G Core Test", self)
        self.load_5g_core_template.triggered.connect(lambda: self.load_template("5g_core_test"))
        
        self.load_5g_ran_template = QAction("5G RAN Test", self)
        self.load_5g_ran_template.triggered.connect(lambda: self.load_template("5g_ran_test"))
        
        self.load_full_5g_template = QAction("Complete 5G Network", self)
        self.load_full_5g_template.triggered.connect(lambda: self.load_template("full_5g_network"))

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

        # Templates submenu
        self.templates_menu = self.file_menu.addMenu("Load &Template")
        self.templates_menu.addAction(self.load_5g_core_template)
        self.templates_menu.addAction(self.load_5g_ran_template)
        self.templates_menu.addAction(self.load_full_5g_template)

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
        
        # Templates toolbar
        self.template_toolbar = TemplateToolBar(self)
        self.addToolBar(self.template_toolbar)

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

    def load_template(self, template_name):
        """Load a predefined network topology template"""
        reply = QMessageBox.question(
            self, "Load Template",
            f"Are you sure you want to load the {template_name.replace('_', ' ')} template? This will clear your current network.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                simulator = NetworkSimulator(self.canvas)
                result = simulator.load_template(template_name)
                if result:
                    self.statusBar().showMessage(f"Template {template_name} loaded successfully", 3000)
                else:
                    self.statusBar().showMessage(f"Failed to load template {template_name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Template Error", f"Failed to load template: {str(e)}")

    def run_simulation(self):
        from simulation.simulator import NetworkSimulator

        try:
            simulator = NetworkSimulator(self.canvas)
            result, simulation_data = simulator.run()
            if result:
                self.statusBar().showMessage("Simulation completed successfully", 3000)
                self.show_simulation_results(simulation_data)
            else:
                self.statusBar().showMessage("Simulation completed with errors", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Simulation Error", f"Failed to run simulation: {str(e)}")

    def show_simulation_results(self, simulation_data):
        """Display simulation results in a new window"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Simulation Results")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Create tabs for different types of results
        tabs = QTabWidget()
        
        # Summary tab
        summary_tab = QWidget()
        summary_layout = QGridLayout()
        
        # Add summary information
        summary_layout.addWidget(QLabel("<h2>Simulation Summary</h2>"), 0, 0)
        
        row = 1
        if 'network_stats' in simulation_data:
            stats = simulation_data['network_stats']
            summary_layout.addWidget(QLabel("<b>Network Statistics:</b>"), row, 0)
            row += 1
            for key, value in stats.items():
                summary_layout.addWidget(QLabel(f"{key}:"), row, 0)
                summary_layout.addWidget(QLabel(f"{value}"), row, 1)
                row += 1
        
        summary_tab.setLayout(summary_layout)
        tabs.addTab(summary_tab, "Summary")
        
        # Performance tab
        if 'performance_metrics' in simulation_data:
            perf_tab = QWidget()
            perf_layout = QVBoxLayout()
            perf_text = QTextEdit()
            perf_text.setReadOnly(True)
            
            metrics = simulation_data['performance_metrics']
            perf_content = "<h2>Performance Metrics</h2>"
            
            for category, values in metrics.items():
                perf_content += f"<h3>{category}</h3>"
                perf_content += "<ul>"
                for k, v in values.items():
                    perf_content += f"<li><b>{k}:</b> {v}</li>"
                perf_content += "</ul>"
            
            perf_text.setHtml(perf_content)
            perf_layout.addWidget(perf_text)
            perf_tab.setLayout(perf_layout)
            tabs.addTab(perf_tab, "Performance")
        
        # Raw data tab
        raw_tab = QWidget()
        raw_layout = QVBoxLayout()
        raw_text = QTextEdit()
        raw_text.setReadOnly(True)
        
        # Format the raw data for display
        import json
        raw_text.setText(json.dumps(simulation_data, indent=2))
        
        raw_layout.addWidget(raw_text)
        raw_tab.setLayout(raw_layout)
        tabs.addTab(raw_tab, "Raw Data")
        
        layout.addWidget(tabs)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_about(self):
        QMessageBox.about(self, "About NetFlux5G",
                         """<b>NetFlux5G</b> v1.0<br><br>
                         A network topology designer for 5G, wireless, and container-based networks.<br><br>
                         Create complex network designs and export them to Docker Compose or Mininet
                         for deployment and testing.<br><br>
                         &copy; 2023 NetFlux Project""")