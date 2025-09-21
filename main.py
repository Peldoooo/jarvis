#!/usr/bin/env python3
"""
JARVIS Assistant - AI Virtual Assistant
Main application entry point
"""

import tkinter as tk
from tkinter import ttk
import threading
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import JarvisMainWindow
from core.jarvis_core import JarvisCore
from utils.logger import setup_logger

def main():
    """Main application entry point"""
    # Setup logging
    logger = setup_logger()
    logger.info("Starting JARVIS Assistant...")
    
    try:
        # Initialize the core system
        jarvis_core = JarvisCore()
        
        # Create the main window
        root = tk.Tk()
        app = JarvisMainWindow(root, jarvis_core)
        
        # Start the GUI
        logger.info("JARVIS Assistant started successfully")
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Failed to start JARVIS Assistant: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    
    finally:
        logger.info("JARVIS Assistant shutting down...")

if __name__ == "__main__":
    main()
