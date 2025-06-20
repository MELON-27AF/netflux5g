from PyQt5.QtCore import QPointF
from models.component_factory import ComponentFactory

class NetworkSimulator:
    def __init__(self, canvas):
        self.canvas = canvas
        self.component_factory = ComponentFactory()

    def run(self):
        """Run the simulation on the current network"""
        # Here we would add actual simulation logic
        print("Running simulation on network...")
        return True

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
