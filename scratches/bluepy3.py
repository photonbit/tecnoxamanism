from bluepy import btle

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        super().__init__()

    def handleNotification(self, cHandle, data):
        # This will be called on notifications from the peripheral
        print("Data received:", data.decode())


def main():
    # Replace with your device's MAC address
    device_mac = "e9:fb:4f:92:b4:53"

    # UART Service UUIDs
    uart_service_uuid = btle.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
    tx_char_uuid = btle.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")  # TX Characteristic (used for receiving data)

    # Connect to the device
    p = btle.Peripheral(device_mac)
    p.setDelegate(MyDelegate())

    # Find the UART service and characteristics
    uart_service = p.getServiceByUUID(uart_service_uuid)
    tx_char = uart_service.getCharacteristics(tx_char_uuid)[0]

    # Enable notifications on the TX characteristic
    p.writeCharacteristic(tx_char.valHandle + 1, b"\x01\x00")

    while True:
        if p.waitForNotifications(1.0):
            # handleNotification() was called
            continue

        print("Waiting...")


if __name__ == "__main__":
    main()
