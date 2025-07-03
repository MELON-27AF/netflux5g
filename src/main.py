#!/usr/bin/env python3
import sys
import traceback
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('netflux5g.log'),
        logging.StreamHandler()
    ]
)

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Show error dialog
    if QApplication.instance():
        QMessageBox.critical(None, "Critical Error", 
                           f"An unexpected error occurred:\n{exc_type.__name__}: {exc_value}")

def main():
    # Set exception handler
    sys.excepthook = handle_exception
    
    try:
        logging.info("Starting NetFlux5G application...")
        
        app = QApplication(sys.argv)
        app.setApplicationName("NetFlux5G")
        app.setOrganizationName("NetFlux")
        
        # Check for required modules
        try:
            from gui.main_window import MainWindow
        except ImportError as e:
            logging.error(f"Failed to import MainWindow: {e}")
            QMessageBox.critical(None, "Import Error", 
                               f"Failed to import required modules:\n{e}")
            return 1
        
        logging.info("Creating main window...")
        window = MainWindow()
        window.show()
        
        logging.info("Application started successfully")
        return app.exec_()
        
    except Exception as e:
        logging.error(f"Error starting application: {e}")
        logging.error(traceback.format_exc())
        if QApplication.instance():
            QMessageBox.critical(None, "Startup Error", 
                               f"Failed to start application:\n{e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())