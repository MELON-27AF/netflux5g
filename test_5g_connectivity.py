#!/usr/bin/env python3
"""
NetFlux5G - End-to-End Connectivity Test Script
This script tests the 5G core network setup for UE connectivity
"""

import sys
import os
import time
import logging

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from simulation.enhanced_container_manager import EnhancedContainerManager

def test_5g_connectivity():
    """Test 5G core network end-to-end connectivity"""
    print("🧪 NetFlux5G - End-to-End Connectivity Test")
    print("=" * 50)
    
    # Initialize container manager
    container_manager = EnhancedContainerManager()
    
    if not container_manager.client:
        print("❌ Docker client not available. Please ensure Docker is running.")
        return False
    
    try:
        # Create a minimal 5G core topology for testing
        print("📦 Creating test 5G core components...")
        
        # Create mock components for testing
        class MockComponent:
            def __init__(self, comp_type, name):
                self.component_type = comp_type
                self.properties = {"name": name}
                self.component_id = f"{comp_type}_test"
        
        # Create test components
        test_components = [
            MockComponent("nrf", "nrf-test"),
            MockComponent("amf", "amf-test"),
            MockComponent("smf", "smf-test"),
            MockComponent("upf", "upf-test"),
            MockComponent("gnb", "gnb-test"),
            MockComponent("ue", "ue-test")
        ]
        
        print(f"Created {len(test_components)} test components")
        
        # Deploy the 5G core
        print("🚀 Deploying 5G core network...")
        success, message = container_manager.deploy_5g_core(test_components)
        
        if not success:
            print(f"❌ Deployment failed: {message}")
            return False
        
        print(f"✅ Deployment successful: {message}")
        
        # Wait for network to stabilize
        print("⏳ Waiting for network to stabilize...")
        time.sleep(60)  # Wait for all services to be ready
        
        # Test connectivity
        print("🔍 Testing network connectivity...")
        connectivity_results = container_manager.test_connectivity()
        
        # Analyze results
        print("\n📊 Connectivity Test Results:")
        print("-" * 40)
        
        total_tests = len(connectivity_results)
        successful_tests = sum(1 for test in connectivity_results if test['success'])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total tests: {total_tests}")
        print(f"Successful tests: {successful_tests}")
        print(f"Success rate: {success_rate:.1f}%")
        
        # Show end-to-end connectivity results
        ue_tests = [test for test in connectivity_results if 'ue' in test.get('source', '').lower()]
        end_to_end_tests = [test for test in ue_tests if 'external' in test.get('target', '') or 'tunnel' in test.get('target', '')]
        
        if end_to_end_tests:
            print("\n🌐 End-to-End UE Connectivity Results:")
            print("-" * 40)
            for test in end_to_end_tests:
                status = "✅ PASS" if test['success'] else "❌ FAIL"
                print(f"{status} {test['source']} -> {test['target']}")
                if not test['success'] and test.get('error'):
                    print(f"   Error: {test['error']}")
        
        # Determine overall success
        ue_external_success = any(test['success'] for test in end_to_end_tests if 'external' in test.get('target', ''))
        
        if ue_external_success:
            print("\n🎉 SUCCESS! UE can ping external networks end-to-end!")
            return True
        else:
            print("\n❌ FAILED! UE cannot reach external networks.")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        try:
            print("\n🧹 Cleaning up test environment...")
            container_manager.cleanup()
            print("✅ Cleanup complete")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")

def main():
    """Main test function"""
    logging.basicConfig(level=logging.INFO)
    
    print("NetFlux5G - 5G Core End-to-End Connectivity Test")
    print("This test will verify that UE can ping external networks through the 5G core")
    print()
    
    # Run the test
    success = test_5g_connectivity()
    
    if success:
        print("\n✅ All tests passed! The 5G core network is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed! Please check the configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
