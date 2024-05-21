import asyncio
from bleak import BleakClient

device_address = "E9:FB:4F:92:B4:53"
characteristic_uuid = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

activate = bytearray("state:activated\n", 'utf-8')
interested = bytearray("state:interested\n", 'utf-8')
integrated = bytearray("state:integrated\n", 'utf-8')


def notification_handler(sender: str, data: bytearray):
    print(f"Received: {data} from {sender}")


async def write_to_characteristic(address, char_uuid):
    async with BleakClient(address) as client:
        await client.write_gatt_char(char_uuid, integrated)
        await asyncio.sleep(5.0)
        await client.write_gatt_char(char_uuid, activate)
        await asyncio.sleep(5.0)
        await client.write_gatt_char(char_uuid, integrated)
        await asyncio.sleep(5.0)
        print(f"Written to {char_uuid}")


async def subscribe_to_uart(address, char_uuid):
    await write_to_characteristic(address, char_uuid)

asyncio.run(subscribe_to_uart(device_address, characteristic_uuid))
