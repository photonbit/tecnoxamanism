import asyncio
from bleak import BleakClient

# Replace with your device's MAC address
device_mac = "e9:fb:4f:92:b4:53"

# UART Service UUIDs
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # TX Characteristic (used for receiving data)


def notification_handler(sender, data):
    """Simple notification handler which prints the data received."""
    print(data.decode(), end="")


async def main():
    async with BleakClient(device_mac) as client:
        connected = await client.is_connected()
        if connected:
            print("Connected to the device!")

            # Enabling notifications
            await client.start_notify(TX_CHAR_UUID, notification_handler)

            # Keep the program running to listen for notifications
            print("Listening for notifications...")
            await asyncio.sleep(30)  # Adjust the sleep time as needed

            # Disable notifications
            await client.stop_notify(TX_CHAR_UUID)
        else:
            print("Failed to connect.")


if __name__ == "__main__":
    asyncio.run(main())
