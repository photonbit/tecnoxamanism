from bluepy import btle


class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self.data = ""

    def handleNotification(self, cHandle, data):
        decoded = data.decode()
        print(f"Data received: {decoded}")
        if "|" not in decoded:
            self.data += decoded
        else:
            self.data += decoded.split("|")[0]
            print(f"Data clean: {self.data}")
            self.data = decoded.split("|")[1]


# Replace with your device's MAC address and specific UUIDs
DEVICE_MAC_ADDRESS = "e9:fb:4f:92:b4:53"
UART_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
UART_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"


# Connect to the device
print(f"Connecting to device at {DEVICE_MAC_ADDRESS}")
device = btle.Peripheral(DEVICE_MAC_ADDRESS, "random")
device.setDelegate(MyDelegate())

# Find the UART service and characteristic
uart_service = device.getServiceByUUID(UART_SERVICE_UUID)
notify = uart_service.getCharacteristics(UART_CHAR_UUID)[0]


device.writeCharacteristic(notify.valHandle+1, b"\x01\x00")

# Read and write to the characteristic
try:
    while True:
        if device.waitForNotifications(1.0):
            # handleNotification() was called
            continue
finally:
    device.disconnect()
