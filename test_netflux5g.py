#!/usr/bin/env python3
"""
NetFlux5G Test Runner
Test basic functionality of the application
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 import successful")
    except ImportError as e:
        print(f"❌ PyQt5 import failed: {e}")
        return False
    
    try:
        import docker
        print("✅ Docker import successful")
    except ImportError as e:
        print(f"❌ Docker import failed: {e}")
        print("Install with: pip install docker")
        return False
        
    try:
        from gui.main_window import MainWindow
        print("✅ MainWindow import successful")
    except ImportError as e:
        print(f"❌ MainWindow import failed: {e}")
        return False
        
    try:
        from simulation.enhanced_container_manager import EnhancedContainerManager
        print("✅ EnhancedContainerManager import successful")
    except ImportError as e:
        print(f"❌ EnhancedContainerManager import failed: {e}")
        return False
        
    return True

def test_docker_connection():
    """Test Docker connection"""
    print("\nTesting Docker connection...")
    
    try:
        import docker
        client = docker.from_env()
        info = client.info()
        print(f"✅ Docker connected - version: {info.get('ServerVersion', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ Docker connection failed: {e}")
        print("Make sure Docker Desktop is running")
        return False

def run_basic_test():
    """Run basic application test"""
    print("\nRunning basic application test...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication([])
        
        from gui.main_window import MainWindow
        window = MainWindow()
        
        print("✅ Application window created successfully")
        
        # Don't show the window in test mode
        return True
        
    except Exception as e:
        print(f"❌ Application test failed: {e}")
        return False

def main():
    print("NetFlux5G Test Suite")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Docker Connection Test", test_docker_connection),
        ("Basic Application Test", run_basic_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 20)
        if test_func():
            passed += 1
        
    print(f"\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready to run.")
        print("\nTo start NetFlux5G:")
        print("  Windows: run_netflux5g.bat")
        print("  Linux/Mac: ./netflux5g.sh")
        print("  Python: cd src && python main.py")
    else:
        print("❌ Some tests failed. Please fix the issues before running the application.")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
