# Installation Guide

## Prerequisites

Before installing the dependencies, ensure you have Python 3.7 or later installed on your system.

## Installing Dependencies

1. Clone the repository or download the source code.

2. Navigate to the project directory in your terminal or command prompt.

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

## Special Instructions for pyusb

The pyusb package requires additional setup beyond a simple pip installation:

### On Windows:

1. Install the appropriate USB driver for your device. This might be:
   - WinUSB
   - libusb-win32
   - libusbK

2. You may need to use Zadig (http://zadig.akeo.ie/) to install the driver for your specific USB device.

### On Linux:

1. Install libusb:
   ```bash
   sudo apt-get install libusb-1.0-0
   ```

2. You may need to add udev rules to allow non-root access to the USB device. Create a file `/etc/udev/rules.d/99-myusb.rules` with content similar to:
   ```
   SUBSYSTEM=="usb", ATTRS{idVendor}=="XXXX", ATTRS{idProduct}=="YYYY", MODE="0666"
   ```
   Replace XXXX and YYYY with your device's vendor and product IDs.

3. Reload udev rules:
   ```bash
   sudo udevadm control --reload-rules && sudo udevadm trigger
   ```

### On macOS:

1. Install libusb using Homebrew:
   ```bash
   brew install libusb
   ```

After setting up libusb, you should be able to use pyusb successfully.

## Verifying the Installation

After installing all dependencies, you can verify the installation by running a simple Python script that imports the required libraries:

```python
import pyusb
import PySide6
import matplotlib

print("All libraries installed successfully!")
```

If this script runs without any errors, your installation is complete and ready for use.
