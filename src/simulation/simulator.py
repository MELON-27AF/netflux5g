from PyQt5.QtCore import QPointF
from models.component_factory import ComponentFactory

class NetworkSimulator:
    def __init__(self, canvas):
        self.canvas = canvas
        self.component_factory = ComponentFactory()

    def run(self):
        """
        Run the network simulation and return the results
        
        Returns:
            tuple: (success_status, simulation_data)
        """
        # This is a placeholder for the actual simulation logic
        # In a real implementation, you would:
        # 1. Analyze the network topology from the canvas
        # 2. Run simulations based on the topology
        # 3. Collect performance metrics and statistics
        # 4. Return the results
        
        try:
            # Get all components and connections from the canvas
            components = self.canvas.components
            connections = self.canvas.connections
            
            # Simulate network traffic and performance
            simulation_data = self._simulate_network(components, connections)
            
            return True, simulation_data
        except Exception as e:
            print(f"Simulation error: {str(e)}")
            return False, {}
    
    def _simulate_network(self, components, connections):
        """
        Perform the actual network simulation.
        
        Args:
            components: List of network components
            connections: List of connections between components
            
        Returns:
            dict: Simulation data and results
        """
        # Generate some sample simulation data
        # This should be replaced with actual simulation logic
        
        # Count component types
        component_counts = {}
        for component in components:
            comp_type = component.component_type
            if comp_type in component_counts:
                component_counts[comp_type] += 1
            else:
                component_counts[comp_type] = 1
                
        # Generate sample metrics based on topology
        simulation_data = {
            "network_stats": {
                "Total Components": len(components),
                "Total Connections": len(connections),
                "Component Distribution": component_counts
            },
            "performance_metrics": {
                "Latency": {
                    "Average End-to-End": f"{50 + (len(components) * 2)} ms",
                    "Core Network": f"{20 + (len(connections) // 2)} ms",
                    "RAN": f"{15 + (len(components) // 3)} ms"
                },
                "Throughput": {
                    "Aggregate": f"{(len(components) * 100) // 2} Mbps",
                    "Per User": f"{100 - (len(components) * 2)} Mbps"
                },
                "Resource Utilization": {
                    "CPU": f"{30 + (len(components) * 3)}%",
                    "Memory": f"{25 + (len(components) * 2)}%"
                }
            },
            "simulation_time": "00:00:30",
            "component_specific_data": {}
        }
        
        # Add some sample data for specific components
        for component in components:
            comp_id = component.id if hasattr(component, 'id') else id(component)
            comp_type = component.component_type if hasattr(component, 'component_type') else "unknown"
            
            # Generate some fake data based on component type
            if "core" in comp_type.lower():
                simulation_data["component_specific_data"][comp_id] = {
                    "type": comp_type,
                    "load": f"{30 + (hash(comp_id) % 50)}%",
                    "connections": sum(1 for c in connections if c.source == component or c.target == component)
                }
            elif "ran" in comp_type.lower() or "antenna" in comp_type.lower():
                simulation_data["component_specific_data"][comp_id] = {
                    "type": comp_type,
                    "signal_strength": f"{-70 - (hash(comp_id) % 30)} dBm",
                    "users": hash(comp_id) % 10 + 1
                }
        
        return simulation_data

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
