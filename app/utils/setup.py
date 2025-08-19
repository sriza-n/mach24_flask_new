"""
Setup and initialization utilities.
"""

import os
import time
import webbrowser
import threading
import logging

logger = logging.getLogger(__name__)


def display_banner():
    """Display the ASCII art banner."""
    print("\n" * 2)
    print("███╗   ███╗ █████╗  ██████╗██╗  ██╗  ██████╗ ██╗  ██╗")
    print("████╗ ████║██╔══██╗██╔════╝██║  ██║  ╚════██╗██║  ██║")
    print("██╔████╔██║███████║██║     ███████║  █████╔╝ ███████║")
    print("██║╚██╔╝██║██╔══██║██║     ██╔══██║  ██╔═══╝ ╚════██║")
    print("██║ ╚═╝ ██║██║  ██║╚██████╗██║  ██║  ███████╗     ██║")
    print("╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝  ╚══════╝     ╚═╝")
    print()
    print(" ██████╗ ██████╗ ██████╗ ██╗████████╗ █████╗ ██╗     ███████╗")
    print("██╔═══██╗██╔══██╗██╔══██╗██║╚══██╔══╝██╔══██╗██║     ██╔════╝")
    print("██║   ██║██████╔╝██████╔╝██║   ██║   ███████║██║     ███████╗")
    print("██║   ██║██╔══██╗██╔══██╗██║   ██║   ██╔══██║██║     ╚════██║")
    print("╚██████╔╝██║  ██║██████╔╝██║   ██║   ██║  ██║███████╗███████║")
    print(" ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝")
    print()
    print("                                               by Srijan Koju")
    print()


def launch_browser():
    """Launch browser after a short delay to ensure server is running"""
    def open_browser():
        time.sleep(1.5)  # Give the server time to start
        url = "http://localhost:5000"
        try:
            webbrowser.open(url)
            logger.info(f"Browser launched with URL: {url}")
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
    
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()


def setup_data_acquisition():
    """Setup data acquisition mode selection."""
    print("=" * 60)
    print("DATA ACQUISITION MODE SELECTION")
    print("=" * 60)
    print("1. Serial Communication (USB/COM Port)")
    print("2. Wireless Communication (Network/API)")
    print("-" * 60)
    
    while True:
        try:
            choice = input("Select data acquisition mode (1-2): ").strip()
            if choice == "1":
                print(f"✓ Selected: Serial Communication")
                return "serial"
            elif choice == "2":
                print(f"✓ Selected: Wireless Communication")
                return "wireless"
            else:
                print("❌ Invalid choice. Please enter 1 or 2.")
        except KeyboardInterrupt:
            print("\n❌ Setup cancelled by user.")
            exit(1)
        except Exception as e:
            print(f"❌ Error: {e}. Please try again.")


def display_setup_summary(data_acquisition_mode, selected_database, current_database):
    """Display the final setup summary."""
    print("\n" + "=" * 60)
    print("SETUP SUMMARY")
    print("=" * 60)
    print(f"Data Acquisition Mode: {data_acquisition_mode.upper()}")
    print(f"Database: {selected_database}")
    print(f"Database Path: {current_database['path']}")
    print("=" * 60)
    print("✓ Setup completed successfully!")
    print("🚀 Starting Mach24 server...")
    print("-" * 60)
    print("📡 Server will be available at:")
    print("   • Local:    http://127.0.0.1:5000")
    print("   • Local:    http://localhost:5000")
    print("-" * 60)
    print("📋 Available endpoints:")
    print("   • Home:     http://127.0.0.1:5000/home")
    print("   • Database: http://127.0.0.1:5000/page/database")
    print("   • Dashboard: http://127.0.0.1:5000/page/dash1")
    print("   • API Status: http://127.0.0.1:5000/serial_status")
    print("=" * 60)
