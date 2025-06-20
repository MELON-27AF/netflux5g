from PyQt5.QtWidgets import QToolBar, QAction, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os

class TemplateToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__("Templates", parent)
        
        # Label
        self.addWidget(QLabel("Templates: "))
        
        # 5G Core Test
        self.core_action = QAction("5G Core Test", self)
        self.core_action.triggered.connect(lambda: parent.load_template("5g_core_test"))
        self.addAction(self.core_action)
        
        # 5G RAN Test
        self.ran_action = QAction("5G RAN Test", self)
        self.ran_action.triggered.connect(lambda: parent.load_template("5g_ran_test"))
        self.addAction(self.ran_action)
        
        # Full 5G Network
        self.full_action = QAction("Complete 5G Network", self)
        self.full_action.triggered.connect(lambda: parent.load_template("full_5g_network"))
        self.addAction(self.full_action)
