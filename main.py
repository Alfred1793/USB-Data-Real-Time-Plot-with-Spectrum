import sys
from PySide6 import QtWidgets
from gui.app_window import AppWindow
from usb_reader import USBReader
from signal_generator import SimulatedSignalGenerator
from config import VENDOR_ID, SHOW_CONNECTION_INFO

def main():
    # Attempt to find USB device
    showConnectionInfo=SHOW_CONNECTION_INFO
    try:
        reader = USBReader(VENDOR_ID)
        useSimulatedSignal = False
    except Exception as e:
        print(f"Error initializing USB device: {e}. Starting with simulated signal.")
        reader = SimulatedSignalGenerator()
        useSimulatedSignal = True
        #showConnectionInfo = False

    # Start the reader
    reader.start()

    # Initialize and run the application
    app = QtWidgets.QApplication(sys.argv)
    main_window = AppWindow(reader, useSimulatedSignal, showConnectionInfo)
    main_window.show()

    # Run the application
    app.exec()

    # Clean up
    reader.stop()
    reader.join()

if __name__ == '__main__':
    main()