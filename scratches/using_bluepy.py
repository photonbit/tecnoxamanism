from bluepy.btle import Peripheral, UUID

# Replace with the MAC address of your Adafruit Feather
device_mac_address = "E9:FB:4F:92:B4:53"

# Connect to the device
peripheral = Peripheral(device_mac_address)

# Define the UUID of the BLE UART service and its characteristics
uart_service_uuid = UUID("6e400003-b5a3-f393-e0a9-e50e24dcca9e")
rx_characteristic_uuid = UUID("6e400002-b5a3-f393-e0a9-e50e24dcca9e")
tx_characteristic_uuid = UUID("6e400003-b5a3-f393-e0a9-e50e24dcca9e")

# Get the BLE UART service
uart_service = peripheral.getServiceByUUID(uart_service_uuid)

# Get the RX and TX characteristics
rx_characteristic = uart_service.getCharacteristics(rx_characteristic_uuid)[0]
tx_characteristic = uart_service.getCharacteristics(tx_characteristic_uuid)[0]

# Read data from the RX characteristic
received_data = rx_characteristic.read()

# Print the received data
print("Received Data:", received_data.decode("utf-8"))

# Write data to the TX characteristic
data_to_send = "state:activated"
tx_characteristic.write(data_to_send.encode("utf-8"))

# Disconnect from the device
peripheral.disconnect()
