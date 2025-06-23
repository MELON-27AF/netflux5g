from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                            QPushButton, QTextEdit, QLineEdit, QLabel, 
                            QSplitter, QGroupBox, QListWidgetItem, QWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor
import subprocess
import threading
import time

class TerminalDialog(QDialog):
    """
    Terminal dialog for container access - similar to MiniEdit's xterm functionality
    """
    
    def __init__(self, container_manager, parent=None):
        super().__init__(parent)
        self.container_manager = container_manager
        self.setWindowTitle("5G Network Container Terminals")
        self.setMinimumSize(1200, 800)
        self.setModal(False)
        
        self.init_ui()
        self.refresh_containers()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_containers)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Left panel - Container list and controls
        left_panel = QVBoxLayout()
        
        # Container list
        containers_group = QGroupBox("5G Network Components")
        containers_layout = QVBoxLayout()
        
        self.container_list = QListWidget()
        self.container_list.itemDoubleClicked.connect(self.open_container_terminal)
        containers_layout.addWidget(self.container_list)
        
        # Container control buttons
        button_layout = QHBoxLayout()
        
        self.terminal_btn = QPushButton("Open Terminal")
        self.terminal_btn.clicked.connect(self.open_selected_terminal)
        button_layout.addWidget(self.terminal_btn)
        
        self.ping_btn = QPushButton("Ping Test")
        self.ping_btn.clicked.connect(self.ping_test)
        button_layout.addWidget(self.ping_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_containers)
        button_layout.addWidget(self.refresh_btn)
        
        containers_layout.addLayout(button_layout)
        containers_group.setLayout(containers_layout)
        left_panel.addWidget(containers_group)
        
        # Command execution panel
        cmd_group = QGroupBox("Execute Commands")
        cmd_layout = QVBoxLayout()
        
        cmd_input_layout = QHBoxLayout()
        cmd_input_layout.addWidget(QLabel("Command:"))
        self.cmd_input = QLineEdit()
        self.cmd_input.returnPressed.connect(self.execute_command)
        cmd_input_layout.addWidget(self.cmd_input)
        
        self.execute_btn = QPushButton("Execute")
        self.execute_btn.clicked.connect(self.execute_command)
        cmd_input_layout.addWidget(self.execute_btn)
        
        cmd_layout.addLayout(cmd_input_layout)
        cmd_group.setLayout(cmd_layout)
        left_panel.addWidget(cmd_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout()
        
        self.ping_all_btn = QPushButton("Ping All Containers")
        self.ping_all_btn.clicked.connect(self.ping_all_containers)
        actions_layout.addWidget(self.ping_all_btn)
        
        self.show_routes_btn = QPushButton("Show IP Routes")
        self.show_routes_btn.clicked.connect(self.show_routes)
        actions_layout.addWidget(self.show_routes_btn)
        
        self.show_interfaces_btn = QPushButton("Show Network Interfaces")
        self.show_interfaces_btn.clicked.connect(self.show_interfaces)
        actions_layout.addWidget(self.show_interfaces_btn)
        
        actions_group.setLayout(actions_layout)
        left_panel.addWidget(actions_group)
        
        # Right panel - Output and logs
        right_panel = QVBoxLayout()
        
        output_group = QGroupBox("Command Output")
        output_layout = QVBoxLayout()
        
        self.output_text = QTextEdit()
        self.output_text.setFont(QFont("Consolas", 10))
        self.output_text.setReadOnly(True)
        output_layout.addWidget(self.output_text)
        
        output_group.setLayout(output_layout)
        right_panel.addWidget(output_group)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_widget.setLayout(QVBoxLayout())
        for i in range(left_panel.count()):
            left_widget.layout().addWidget(left_panel.itemAt(i).widget())
        
        right_widget = QWidget()
        right_widget.setLayout(QVBoxLayout())
        for i in range(right_panel.count()):
            right_widget.layout().addWidget(right_panel.itemAt(i).widget())
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 800])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
    def refresh_containers(self):
        """Refresh the container list"""
        self.container_list.clear()
        
        try:
            containers = self.container_manager.get_all_containers()
            
            for name, container in containers:
                try:
                    container.reload()
                    status = container.status
                    
                    # Get container IP
                    networks = container.attrs['NetworkSettings']['Networks']
                    network_name = self.container_manager.network_name
                    ip = networks.get(network_name, {}).get('IPAddress', 'N/A')
                    
                    # Create list item with status info
                    item_text = f"{name} ({status}) - {ip}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, name)  # Store container name
                    
                    # Color code by status
                    if status == 'running':
                        item.setBackground(Qt.green)
                    elif status == 'exited':
                        item.setBackground(Qt.red)
                    else:
                        item.setBackground(Qt.yellow)
                    
                    self.container_list.addItem(item)
                    
                except Exception as e:
                    item_text = f"{name} (error: {str(e)})"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, name)
                    item.setBackground(Qt.red)
                    self.container_list.addItem(item)
                    
        except Exception as e:
            self.append_output(f"Error refreshing containers: {str(e)}")
    
    def open_selected_terminal(self):
        """Open terminal for selected container"""
        current_item = self.container_list.currentItem()
        if current_item:
            container_name = current_item.data(Qt.UserRole)
            self.open_container_terminal(current_item)
    
    def open_container_terminal(self, item):
        """Open external terminal for container"""
        container_name = item.data(Qt.UserRole)
        
        try:
            self.container_manager.open_container_terminal(container_name)
            self.append_output(f"Opened terminal for {container_name}")
        except Exception as e:
            self.append_output(f"Error opening terminal for {container_name}: {str(e)}")
    
    def execute_command(self):
        """Execute command in selected container"""
        current_item = self.container_list.currentItem()
        command = self.cmd_input.text().strip()
        
        if not current_item or not command:
            return
            
        container_name = current_item.data(Qt.UserRole)
        
        self.append_output(f"\\n$ {container_name}: {command}")
        
        try:
            result = self.container_manager.execute_command_in_container(container_name, command)
            
            if result['exit_code'] == 0:
                self.append_output(result['output'])
            else:
                self.append_output(f"Error (exit code {result['exit_code']}): {result['output']}")
                
        except Exception as e:
            self.append_output(f"Error executing command: {str(e)}")
        
        self.cmd_input.clear()
    
    def ping_test(self):
        """Ping test between selected containers"""
        current_item = self.container_list.currentItem()
        if not current_item:
            return
            
        container_name = current_item.data(Qt.UserRole)
        
        # Get all other containers to ping
        other_containers = []
        for i in range(self.container_list.count()):
            item = self.container_list.item(i)
            if item != current_item:
                other_containers.append(item.data(Qt.UserRole))
        
        if not other_containers:
            self.append_output("No other containers to ping")
            return
        
        self.append_output(f"\\nPing test from {container_name}:")
        
        for target in other_containers:
            try:
                # Get target container IP
                result = self.container_manager.execute_command_in_container(
                    target, "hostname -I | awk '{print $1}'"
                )
                
                if result['exit_code'] == 0:
                    target_ip = result['output'].strip()
                    
                    # Ping target
                    ping_result = self.container_manager.execute_command_in_container(
                        container_name, f"ping -c 1 -W 2 {target_ip}"
                    )
                    
                    if ping_result['exit_code'] == 0:
                        self.append_output(f"  ✓ {target} ({target_ip}): OK")
                    else:
                        self.append_output(f"  ✗ {target} ({target_ip}): FAILED")
                        
            except Exception as e:
                self.append_output(f"  ✗ {target}: Error - {str(e)}")
    
    def ping_all_containers(self):
        """Ping test between all containers"""
        self.append_output("\\n=== Full Network Connectivity Test ===")
        
        try:
            results = self.container_manager.test_connectivity()
            
            success_count = sum(1 for r in results if r['success'])
            total_count = len(results)
            
            self.append_output(f"Total tests: {total_count}, Successful: {success_count}")
            self.append_output(f"Success rate: {(success_count/total_count*100):.1f}%" if total_count > 0 else "0%")
            self.append_output("")
            
            for result in results:
                status = "✓" if result['success'] else "✗"
                self.append_output(f"{status} {result['source']} -> {result['target']} ({result['target_ip']})")
                
        except Exception as e:
            self.append_output(f"Error in connectivity test: {str(e)}")
    
    def show_routes(self):
        """Show IP routes for selected container"""
        current_item = self.container_list.currentItem()
        if not current_item:
            return
            
        container_name = current_item.data(Qt.UserRole)
        
        self.append_output(f"\\nIP Routes for {container_name}:")
        
        try:
            result = self.container_manager.execute_command_in_container(
                container_name, "ip route show"
            )
            self.append_output(result['output'])
        except Exception as e:
            self.append_output(f"Error getting routes: {str(e)}")
    
    def show_interfaces(self):
        """Show network interfaces for selected container"""
        current_item = self.container_list.currentItem()
        if not current_item:
            return
            
        container_name = current_item.data(Qt.UserRole)
        
        self.append_output(f"\\nNetwork Interfaces for {container_name}:")
        
        try:
            result = self.container_manager.execute_command_in_container(
                container_name, "ip addr show"
            )
            self.append_output(result['output'])
        except Exception as e:
            self.append_output(f"Error getting interfaces: {str(e)}")
    
    def append_output(self, text):
        """Append text to output area"""
        self.output_text.append(text)
        
        # Auto-scroll to bottom
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.output_text.setTextCursor(cursor)
    
    def closeEvent(self, event):
        """Clean up when dialog is closed"""
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        super().closeEvent(event)
