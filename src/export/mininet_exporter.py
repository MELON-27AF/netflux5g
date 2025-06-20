class MininetExporter:
    def __init__(self, canvas):
        self.canvas = canvas

    def export(self, filename):
        """Export the network topology to a Mininet Python script."""

        # Generate Mininet script
        script = self._generate_mininet_script()

        # Write to file
        with open(filename, 'w') as file:
            file.write(script)

    def _generate_mininet_script(self):
        """Generate the Mininet Python script content."""

        script = """#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
import os
import sys

def create_network():
    # Create network
    net = Mininet(controller=None, switch=OVSSwitch, link=TCLink)

    # Add controllers
"""

        # Add controllers
        controllers = [c for c in self.canvas.components if c.component_type == "controller"]
        if not controllers:
            script += "    # No SDN controllers defined, using default controller\n"
            script += "    c0 = net.addController('c0')\n"
        else:
            for controller in controllers:
                name = controller.properties.get("name", f"c{controller.component_id}")
                controller_type = controller.properties.get("controller_type", "ODL")
                port = controller.properties.get("port", 6653)

                script += f"    # Adding {controller_type} controller\n"
                script += f"    {name} = net.addController('{name}', controller=RemoteController, ip='127.0.0.1', port={port})\n"

        script += "\n    # Add switches\n"

        # Add switches
        switches = [c for c in self.canvas.components if c.component_type == "switch"]
        for switch in switches:
            name = switch.properties.get("name", f"s{switch.component_id}")
            openflow = switch.properties.get("openflow", True)

            script += f"    {name} = net.addSwitch('{name}'"
            if openflow:
                script += f", protocols='OpenFlow13'"
            script += ")\n"

        script += "\n    # Add routers (implemented as switches with routing capabilities)\n"

        # Add routers
        routers = [c for c in self.canvas.components if c.component_type == "router"]
        for router in routers:
            name = router.properties.get("name", f"r{router.component_id}")
            script += f"    {name} = net.addSwitch('{name}', cls=OVSSwitch)\n"

        script += "\n    # Add hosts\n"

        # Add hosts
        hosts = [c for c in self.canvas.components if c.component_type == "host"]
        for host in hosts:
            name = host.properties.get("name", f"h{host.component_id}")
            ip = host.properties.get("ip", "")

            if ip:
                script += f"    {name} = net.addHost('{name}', ip='{ip}')\n"
            else:
                script += f"    {name} = net.addHost('{name}')\n"

        script += "\n    # Add 5G Core components as hosts\n"

        # Add 5G Core components as hosts
        core_components = [c for c in self.canvas.components if c.component_type in 
                         ["amf", "smf", "upf", "pcf", "udm", "ausf", "nrf"]]

        for component in core_components:
            name = component.properties.get("name", f"{component.component_type}{component.component_id}")
            script += f"    {name} = net.addHost('{name}')\n"

        script += "\n    # Add RAN components as hosts\n"

        # Add RAN components as hosts
        ran_components = [c for c in self.canvas.components if c.component_type in ["gnb", "ue"]]

        for component in ran_components:
            name = component.properties.get("name", f"{component.component_type}{component.component_id}")
            script += f"    {name} = net.addHost('{name}')\n"

        script += "\n    # Add links\n"

        # Add links
        for link in self.canvas.links:
            source_name = link.source.properties.get("name", f"{link.source.component_type}{link.source.component_id}")
            target_name = link.target.properties.get("name", f"{link.target.component_type}{link.target.component_id}")

            # Check if bandwidth property exists
            bandwidth = link.properties.get("bandwidth", None)
            if bandwidth:
                script += f"    net.addLink({source_name}, {target_name}, bw={bandwidth})\n"
            else:
                script += f"    net.addLink({source_name}, {target_name})\n"

        # Complete the script with the main function
        script += """
    # Start network
    net.build()
    net.start()

    # Configure 5G components (example script)
    print("Configuring 5G network components...")

    # Start CLI
    CLI(net)

    # Cleanup on exit
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_network()
"""

        return script