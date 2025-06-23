from PyQt5.QtCore import QPointF
from models.component_factory import ComponentFactory
from utils import calculate_latency, calculate_throughput, calculate_resource_utilization
from .container_manager import ContainerManager

class NetworkSimulator:
    def __init__(self, canvas):
        self.canvas = canvas
        self.component_factory = ComponentFactory()
        self.container_manager = ContainerManager()

    def run(self):
        """
        Run the network simulation and return the results
        
        Returns:
            tuple: (success_status, simulation_data)
        """
        try:
            # Get all components and connections from the canvas
            components = self.canvas.components
            connections = self.canvas.connections
            
            print("Starting 5G network simulation...")
            
            # Deploy containers for 5G components
            success, message = self.container_manager.deploy_5g_core(components)
            
            if not success:
                return False, {"error": message}
            
            print(f"Container deployment: {message}")
            
            # Wait a moment for containers to start
            import time
            time.sleep(5)
            
            # Test connectivity
            print("Testing network connectivity...")
            connectivity_results = self.container_manager.test_connectivity()
            
            # Get container status
            container_status = self.container_manager.get_container_status()
            
            # Simulate network traffic and performance (existing logic)
            simulation_data = self._simulate_network(components, connections)
            
            # Add container deployment results
            simulation_data["container_deployment"] = {
                "status": "success",
                "message": message,
                "containers": container_status
            }
            
            simulation_data["connectivity_tests"] = connectivity_results
            
            # Calculate connectivity statistics
            total_tests = len(connectivity_results)
            successful_tests = sum(1 for test in connectivity_results if test['success'])
            
            simulation_data["connectivity_summary"] = {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": f"{(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            }
            
            return True, simulation_data
            
        except Exception as e:
            print(f"Simulation error: {str(e)}")
            return False, {"error": str(e)}
    
    def _simulate_network(self, components, connections):
        """
        Perform the actual network simulation.
        
        Args:
            components: List of network components
            connections: List of connections between components
            
        Returns:
            dict: Simulation data and results
        """
        # Count component types for analysis
        component_counts = {}
        for component in components:
            comp_type = component.component_type
            if comp_type in component_counts:
                component_counts[comp_type] += 1
            else:
                component_counts[comp_type] = 1
        
        # Calculate network metrics based on the topology using utility functions
        latency_metrics = calculate_latency(len(components), len(connections), component_counts)
        throughput_metrics = calculate_throughput(len(components), len(connections), component_counts)
        resource_metrics = calculate_resource_utilization(len(components), len(connections), component_counts)
                
        # Generate simulation data based on topology and calculations
        simulation_data = {
            "network_stats": {
                "Total Components": len(components),
                "Total Connections": len(connections),
                "Component Distribution": component_counts
            },
            "performance_metrics": {
                "Latency": latency_metrics,
                "Throughput": throughput_metrics,
                "Resource Utilization": resource_metrics
            },
            "simulation_time": "00:00:30",
            "component_specific_data": {}
        }
        
        # Add component-specific data based on component type
        for component in components:
            comp_id = component.component_id if hasattr(component, 'component_id') else id(component)
            comp_type = component.component_type if hasattr(component, 'component_type') else "unknown"
            
            # Generate data based on component type
            if "core" in comp_type.lower() or comp_type in ["amf", "smf", "upf", "pcf", "udm", "ausf", "nrf"]:
                # Core network components
                connection_count = sum(1 for c in connections if c.source == component or c.target == component)
                load_percentage = 30 + (connection_count * 5)
                throughput = 100 + (connection_count * 20)
                
                simulation_data["component_specific_data"][comp_id] = {
                    "type": comp_type,
                    "load": f"{min(95, load_percentage)}%",
                    "throughput": f"{throughput} Mbps",
                    "connections": connection_count
                }
                
            elif comp_type in ["gnb", "ue"] or "ran" in comp_type.lower() or "antenna" in comp_type.lower():
                # RAN components
                if comp_type == "gnb":
                    # gNB specific metrics
                    power = component.properties.get("power", 20) if hasattr(component, 'properties') else 20
                    connected_ues = sum(1 for c in connections if (c.source == component and getattr(c.target, 'component_type', '') == "ue") or 
                                       (c.target == component and getattr(c.source, 'component_type', '') == "ue"))
                    
                    simulation_data["component_specific_data"][comp_id] = {
                        "type": comp_type,
                        "signal_power": f"{power} dBm",
                        "connected_ues": connected_ues,
                        "bandwidth": f"{100 + (connected_ues * 20)} MHz"
                    }
                elif comp_type == "ue":
                    # UE specific metrics
                    connected_gnb = next((c for c in connections if 
                                         (c.source == component and getattr(c.target, 'component_type', '') == "gnb") or
                                         (c.target == component and getattr(c.source, 'component_type', '') == "gnb")), None)
                    
                    signal_strength = -70
                    if connected_gnb:
                        # Calculate signal strength based on "distance" (simplified)
                        gnb = c.source if getattr(c.source, 'component_type', '') == "gnb" else c.target
                        power = gnb.properties.get("power", 20) if hasattr(gnb, 'properties') else 20
                        # A very simplified signal strength calculation
                        signal_strength = -70 + (power / 2)
                    
                    simulation_data["component_specific_data"][comp_id] = {
                        "type": comp_type,
                        "signal_strength": f"{signal_strength} dBm",
                        "data_rate": f"{80 + (signal_strength + 100)} Mbps"  # Higher signal = higher data rate
                    }
            
            elif comp_type in ["switch", "router"]:
                # Network infrastructure components
                connection_count = sum(1 for c in connections if c.source == component or c.target == component)
                packet_rate = 1000 * connection_count
                
                simulation_data["component_specific_data"][comp_id] = {
                    "type": comp_type,
                    "packet_rate": f"{packet_rate} pps",
                    "connections": connection_count,
                    "load": f"{min(95, 30 + (connection_count * 10))}%"
                }
        
        return simulation_data

    def stop_simulation(self):
        """Stop the simulation and cleanup containers"""
        try:
            print("Stopping simulation and cleaning up containers...")
            self.container_manager.cleanup()
            return True
        except Exception as e:
            print(f"Error stopping simulation: {e}")
            return False
    
    def open_container_terminal(self, container_name):
        """Open terminal to specific container"""
        self.container_manager.open_terminal_to_container(container_name)

    def load_template(self, template_name):
        """Load a predefined network topology template"""
        print(f"Loading template: {template_name}")
        
        if template_name == "5g_core_test":
            return self.load_5g_core_test_template()
        elif template_name == "5g_ran_test":
            return self.load_5g_ran_test_template()
        elif template_name == "full_5g_network":
            return self.load_full_5g_network_template()
        else:
            print(f"Unknown template: {template_name}")
            return False

    def load_5g_core_test_template(self):
        """
        Create a 5G core network topology for testing all core functions
        This includes all NFs (AMF, SMF, UPF, PCF, UDM, AUSF, NRF)
        """
        # Clear existing network
        self.canvas.clear()
        
        # Create core components with appropriate positioning
        spacing_x = 150
        spacing_y = 150
        base_x = 200
        base_y = 200
        
        # Create NRF at the center (Network Repository Function - service discovery)
        nrf = self.add_component("nrf", QPointF(base_x + spacing_x*2, base_y))
        
        # Create control plane components
        amf = self.add_component("amf", QPointF(base_x, base_y + spacing_y))
        smf = self.add_component("smf", QPointF(base_x + spacing_x, base_y + spacing_y))
        pcf = self.add_component("pcf", QPointF(base_x + spacing_x*2, base_y + spacing_y))
        udm = self.add_component("udm", QPointF(base_x + spacing_x*3, base_y + spacing_y))
        ausf = self.add_component("ausf", QPointF(base_x + spacing_x*4, base_y + spacing_y))
        
        # Create user plane function
        upf = self.add_component("upf", QPointF(base_x + spacing_x, base_y + spacing_y*2))
        
        # Create gNB and UE for testing
        gnb = self.add_component("gnb", QPointF(base_x, base_y + spacing_y*3))
        ue = self.add_component("ue", QPointF(base_x - spacing_x, base_y + spacing_y*3))
        
        # Add external network (represented as a router)
        router = self.add_component("router", QPointF(base_x + spacing_x*3, base_y + spacing_y*2))
        
        # Connect components with links according to 5G architecture
        # NRF connects to all control plane functions for service registration/discovery
        self.add_link(nrf, amf)
        self.add_link(nrf, smf)
        self.add_link(nrf, pcf)
        self.add_link(nrf, udm)
        self.add_link(nrf, ausf)
        
        # AMF connections
        self.add_link(amf, smf)
        self.add_link(amf, ausf)
        
        # SMF connections
        self.add_link(smf, upf)
        self.add_link(smf, pcf)
        
        # UDM connections
        self.add_link(udm, ausf)
        self.add_link(udm, pcf)
        
        # RAN connections
        self.add_link(amf, gnb)
        self.add_link(gnb, ue)
        
        # External network connection
        self.add_link(upf, router)
        
        # Set custom properties for the components
        amf.set_properties({
            "name": "amf-test",
            "capacity": 200,
            "region": "test-region"
        })
        
        smf.set_properties({
            "name": "smf-test",
            "upf_selection": "local"
        })
        
        upf.set_properties({
            "name": "upf-test",
            "capacity": 2000,
            "datapath": "00:00:00:00:00:01"
        })
        
        pcf.set_properties({
            "name": "pcf-test"
        })
        
        udm.set_properties({
            "name": "udm-test"
        })
        
        ausf.set_properties({
            "name": "ausf-test"
        })
        
        nrf.set_properties({
            "name": "nrf-test"
        })
        
        gnb.set_properties({
            "name": "gnb-test",
            "tac": 1,
            "frequency": "FR1",
            "power": 30
        })
        
        ue.set_properties({
            "name": "ue-test",
            "imsi": "001010000000001",
            "k": "465B5CE8B199B49FAA5F0A2EE238A6BC",
            "opc": "E8ED289DEBA952E4283B54E88E6183CA"
        })
        
        router.set_properties({
            "name": "internet-gw",
            "openflow": True
        })
        
        return True

    def load_5g_ran_test_template(self):
        """
        Create a 5G RAN test topology with multiple gNBs and UEs
        """
        # Implementation would be similar to the core test template
        # but focusing on RAN components
        print("RAN test template not implemented yet")
        return False

    def load_full_5g_network_template(self):
        """
        Create a complete 5G network with core and multiple RAN components
        """
        # Implementation would combine core and RAN templates
        # with more complex topology
        print("Full 5G network template not implemented yet")
        return False

    def add_component(self, component_type, position):
        """Add a component to the canvas and return it"""
        component = self.canvas.add_component(component_type, position)
        return component
        
    def add_link(self, source, target):
        """Add a link between two components"""
        link = self.canvas.add_link(source, target)
        return link
