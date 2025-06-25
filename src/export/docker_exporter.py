import yaml
import os

class DockerExporter:
    def __init__(self, canvas):
        self.canvas = canvas

    def export(self, filename):
        """Export the network topology to a Docker Compose file."""

        # Prepare Docker Compose structure
        compose = {
            "version": "3",
            "services": {},
            "networks": {
                "5gnet": {
                    "driver": "bridge"
                }
            }
        }

        # Process components
        for component in self.canvas.components:
            service_name = component.properties.get("name", f"{component.component_type}_{component.component_id}")

            # Configure service based on component type
            service = {
                "container_name": service_name,
                "networks": ["5gnet"]
            }

            # Set component-specific configuration
            if component.component_type == "amf":
                service["image"] = "openverso/open5gs:latest"
                service["environment"] = [
                    f"AMF_NAME={service_name}",
                    f"CAPACITY={component.properties.get('capacity', 100)}",
                    f"REGION={component.properties.get('region', 'region1')}"
                ]

            elif component.component_type == "smf":
                service["image"] = "openverso/open5gs:latest"
                service["environment"] = [
                    f"SMF_NAME={service_name}",
                    f"UPF_SELECTION={component.properties.get('upf_selection', 'local')}"
                ]

            elif component.component_type == "upf":
                service["image"] = "openverso/open5gs:latest"
                service["environment"] = [
                    f"UPF_NAME={service_name}",
                    f"CAPACITY={component.properties.get('capacity', 1000)}"
                ]
                service["cap_add"] = ["NET_ADMIN"]
                service["privileged"] = True

            elif component.component_type == "pcf":
                service["image"] = "openverso/open5gs:latest"
                service["environment"] = [
                    f"PCF_NAME={service_name}"
                ]

            elif component.component_type == "udm":
                service["image"] = "openverso/open5gs:latest"
                service["environment"] = [
                    f"UDM_NAME={service_name}"
                ]

            elif component.component_type == "ausf":
                service["image"] = "openverso/open5gs:latest"
                service["environment"] = [
                    f"AUSF_NAME={service_name}"
                ]

            elif component.component_type == "nrf":
                service["image"] = "openverso/open5gs:latest"
                service["environment"] = [
                    f"NRF_NAME={service_name}"
                ]

            elif component.component_type == "gnb":
                service["image"] = "openverso/ueransim:latest"
                service["environment"] = [
                    f"GNB_NAME={service_name}",
                    f"TAC={component.properties.get('tac', 1)}",
                    f"FREQUENCY={component.properties.get('frequency', 'FR1')}",
                    f"POWER={component.properties.get('power', 20)}"
                ]
                service["cap_add"] = ["NET_ADMIN"]
                service["privileged"] = True

            elif component.component_type == "ue":
                service["image"] = "openverso/ueransim:latest"
                service["environment"] = [
                    f"UE_NAME={service_name}",
                    f"IMSI={component.properties.get('imsi', '001010000000001')}",
                    f"KEY={component.properties.get('k', '465B5CE8B199B49FAA5F0A2EE238A6BC')}",
                    f"OPC={component.properties.get('opc', 'E8ED289DEBA952E4283B54E88E6183CA')}"
                ]
                service["cap_add"] = ["NET_ADMIN"]
                service["privileged"] = True

            elif component.component_type == "switch":
                service["image"] = "openflow/ovs:latest"
                service["environment"] = [
                    f"SWITCH_NAME={service_name}",
                    f"OPENFLOW={component.properties.get('openflow', True)}"
                ]
                service["cap_add"] = ["NET_ADMIN"]
                service["privileged"] = True

            elif component.component_type == "router":
                service["image"] = "frrouting/frr:latest"
                service["environment"] = [
                    f"ROUTER_NAME={service_name}"
                ]
                service["cap_add"] = ["NET_ADMIN"]
                service["privileged"] = True

            elif component.component_type == "host":
                service["image"] = "ubuntu:latest"
                service["command"] = "sleep infinity"
                if "ip" in component.properties:
                    service["environment"] = [
                        f"IP_ADDRESS={component.properties.get('ip')}",
                        f"DEFAULT_GW={component.properties.get('default_gw', '')}"
                    ]

            elif component.component_type == "controller":
                controller_type = component.properties.get("controller_type", "ODL")

                if controller_type == "ODL":
                    service["image"] = "opendaylight/odl:latest"
                elif controller_type == "ONOS":
                    service["image"] = "onosproject/onos:latest"
                elif controller_type == "Ryu":
                    service["image"] = "osrg/ryu:latest"
                elif controller_type == "Floodlight":
                    service["image"] = "floodlight/floodlight:latest"

                service["ports"] = [f"{component.properties.get('port', 6653)}:{component.properties.get('port', 6653)}"]

            # Add the service to the compose file
            compose["services"][service_name] = service

        # Add links as dependencies
        for link in self.canvas.links:
            source_name = link.source.properties.get("name", f"{link.source.component_type}_{link.source.component_id}")
            target_name = link.target.properties.get("name", f"{link.target.component_type}_{link.target.component_id}")

            # Add depends_on relationships
            if "depends_on" not in compose["services"][source_name]:
                compose["services"][source_name]["depends_on"] = []

            compose["services"][source_name]["depends_on"].append(target_name)

        # Write the Docker Compose file
        with open(filename, 'w') as file:
            yaml.dump(compose, file, default_flow_style=False)