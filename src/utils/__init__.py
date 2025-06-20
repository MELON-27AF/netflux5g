"""
Utility functions for network simulation calculations
"""

def calculate_latency(component_count, connection_count, component_types):
    """
    Calculate network latency based on topology characteristics
    
    Args:
        component_count: Number of components in the network
        connection_count: Number of connections between components
        component_types: Dictionary of component types and their counts
        
    Returns:
        dict: Dictionary containing latency metrics
    """
    # Base latency values in milliseconds
    core_base = 15
    ran_base = 12
    
    # Calculate core network latency - affected by core network functions
    core_components = sum(component_types.get(ct, 0) for ct in ['amf', 'smf', 'upf', 'pcf', 'udm', 'ausf', 'nrf'])
    core_latency = core_base + (core_components * 1.5) + (connection_count * 0.5)
    
    # Calculate RAN latency - affected by RAN components
    ran_components = sum(component_types.get(ct, 0) for ct in ['gnb', 'ue'])
    ran_latency = ran_base + (ran_components * 2)
    
    # Total end-to-end latency
    e2e_latency = core_latency + ran_latency + 10  # Extra 10ms for additional processing
    
    return {
        "Average End-to-End": f"{round(e2e_latency, 1)} ms",
        "Core Network": f"{round(core_latency, 1)} ms",
        "RAN": f"{round(ran_latency, 1)} ms"
    }

def calculate_throughput(component_count, connection_count, component_types):
    """
    Calculate network throughput based on topology characteristics
    
    Args:
        component_count: Number of components in the network
        connection_count: Number of connections between components
        component_types: Dictionary of component types and their counts
        
    Returns:
        dict: Dictionary containing throughput metrics
    """
    # Base throughput values in Mbps
    base_throughput = 400
    
    # Calculate aggregate throughput
    # More UPFs and gNBs increase capacity
    upf_count = component_types.get('upf', 0)
    gnb_count = component_types.get('gnb', 0)
    ue_count = component_types.get('ue', 0) or 1  # Avoid division by zero
    
    aggregate = base_throughput + (upf_count * 150) + (gnb_count * 100)
    per_user = max(10, aggregate / ue_count)  # Minimum 10 Mbps per user
    
    return {
        "Aggregate": f"{round(aggregate)} Mbps",
        "Per User": f"{round(per_user)} Mbps"
    }

def calculate_resource_utilization(component_count, connection_count, component_types):
    """
    Calculate resource utilization based on topology characteristics
    
    Args:
        component_count: Number of components in the network
        connection_count: Number of connections between components
        component_types: Dictionary of component types and their counts
        
    Returns:
        dict: Dictionary containing resource utilization metrics
    """
    # Base utilization percentages
    base_cpu = 20
    base_memory = 15
    
    # Each component adds load
    cpu_utilization = base_cpu + (component_count * 2) + (connection_count * 1)
    memory_utilization = base_memory + (component_count * 1.5) + (connection_count * 0.5)
    
    # Cap at reasonable values
    cpu_utilization = min(95, cpu_utilization)
    memory_utilization = min(90, memory_utilization)
    
    return {
        "CPU": f"{round(cpu_utilization)}%",
        "Memory": f"{round(memory_utilization)}%"
    }
