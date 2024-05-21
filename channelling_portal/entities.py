import enum
import time
from collections import deque
from typing import Protocol, Optional
import socket
import numpy as np

import serial
from bluepy import btle
from pydantic import BaseModel, Field
from dtaidistance import dtw


class SpiritState(str, enum.Enum):
    inert = "inert"
    dormant = "dormant"
    interested = "interested"
    awakened = "awakened"
    interconnected = "interconnected"


class Quaternion(BaseModel):
    qw: float = Field(..., ge=-1, le=1)
    qx: float = Field(..., ge=-1, le=1)
    qy: float = Field(..., ge=-1, le=1)
    qz: float = Field(..., ge=-1, le=1)

    def y_rotation(self) -> float:
        return np.arcsin(2.0 * (self.qw*self.qy - self.qx*self.qz))


class Measurement(BaseModel):
    timestamp: int
    quaternion: Quaternion


class SpiritCommunication(Protocol):
    def measure(self) -> Measurement:
        ...

    def connect(self):
        ...

    def disconnect(self):
        ...

    def notify_state(self, state: SpiritState):
        ...


class SerialSpiritCommunication(BaseModel):
    port: str
    baud_rate: int
    serial = serial.Serial

    def measure(self) -> Measurement:
        while not self.serial.in_waiting:
            time.sleep(0.01)
        line = self.serial.readline().decode('utf-8').rstrip()
        data = list(map(float, line.split(',')))
        return Measurement(
            timestamp=data[0],
            quaternion=Quaternion(qw=data[1], qx=data[2], qy=data[3], qz=data[4])
        )

    def connect(self):
        self.serial = serial.Serial(self.port, self.baud_rate)

    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.serial.close()

    def notify_state(self, state: SpiritState):
        self.serial.write(f"state:{state}\n".encode())


class BLESpiritCommunication(BaseModel):
    mac_address: str
    service_uuid: str
    characteristic_uuid: str
    peripheral: btle.Peripheral = None
    characteristic: btle.Characteristic = None
    buffer: str = ""

    def connect(self):
        self.peripheral = btle.Peripheral(self.mac_address)
        service = self.peripheral.getServiceByUUID(self.service_uuid)
        self.characteristic = service.getCharacteristics(self.characteristic_uuid)[0]

    def disconnect(self):
        if self.peripheral:
            self.peripheral.disconnect()

    def measure(self) -> Measurement:
        if not self.characteristic:
            raise Exception("Not connected to a BLE device")

        while True:
            data_part = self.characteristic.read().decode('utf-8')

            end_idx = data_part.find('\n')
            if end_idx != -1:
                self.buffer += data_part[:end_idx]
                remaining = data_part[end_idx+1:]
                break
            else:
                self.buffer += data_part

        complete_data = self.buffer
        self.buffer = remaining

        data = list(map(float, complete_data.split(',')))
        return Measurement(
            timestamp=data[0],
            quaternion=Quaternion(qw=data[1], qx=data[2], qy=data[3], qz=data[4]),
        )

    def notify_state(self, state: SpiritState):
        if not self.characteristic:
            raise Exception("Not connected to a BLE device")
        self.characteristic.write(str(state).encode())


class WifiSpiritCommunication(BaseModel):
    ip_address: str
    port: int
    server_socket: Optional[socket.socket] = None
    client_socket: Optional[socket.socket] = None
    address: Optional[tuple] = None

    def connect(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip_address, self.port))
        self.server_socket.listen(1)  # Listen for a single connection
        print(f"Listening on {self.ip_address}:{self.port}")

        # Blocking call, waits for a connection
        self.client_socket, self.address = self.server_socket.accept()
        print(f"Connected to {self.address}")

    def disconnect(self):
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()

    def measure(self) -> Measurement:
        if not self.client_socket:
            raise Exception("No client connected")

        data = self.client_socket.recv(1024).decode('utf-8').strip()
        if not data:
            raise Exception("No data received")

        data = list(map(float, data.split(',')))
        return Measurement(
            timestamp=data[0],
            quaternion=Quaternion(qw=data[1], qx=data[2], qy=data[3], qz=data[4]),
        )

    def notify_state(self, state: SpiritState):
        if not self.client_socket:
            raise Exception("No client connected")
        self.client_socket.send(f"state:{state}\n".encode())


def rotation_function_ms(times, rotation_duration=1000, pause_duration=100):
    # Calculate cycle length in milliseconds directly
    cycle_length_ms = 2 * rotation_duration + 2 * pause_duration

    # Initialize the result array
    angles = np.zeros_like(times, dtype=float)

    # Compute the ends of each phase within the cycle
    left_rotation_end_ms = rotation_duration
    first_pause_end_ms = left_rotation_end_ms + pause_duration
    right_rotation_end_ms = first_pause_end_ms + rotation_duration

    # Rates of rotation per millisecond
    left_rate = np.radians(180) / rotation_duration  # Positive rate for left rotation
    right_rate = -np.radians(180) / rotation_duration  # Negative rate for right rotation

    for i, t in enumerate(times):
        # Normalize time to the current cycle in milliseconds
        cycle_time_ms = t % cycle_length_ms

        if cycle_time_ms <= left_rotation_end_ms:
            # Left rotation
            angles[i] = left_rate * cycle_time_ms
        elif cycle_time_ms <= first_pause_end_ms:
            # First pause - keep the angle constant at 180 degrees (in radians)
            angles[i] = np.radians(180)
        elif cycle_time_ms <= right_rotation_end_ms:
            # Right rotation
            angles[i] = np.radians(180) + right_rate * (cycle_time_ms - first_pause_end_ms)
        else:
            # Second pause - angle goes back to 0
            angles[i] = 0

    return angles


class Spirit(BaseModel):
    name: str
    color: str
    conduit: SpiritCommunication
    measurements: deque[Measurement]
    state: SpiritState = SpiritState.inert
    time_zero: int = 0
    gauge: int = 0

    def __init__(self, name, color, conduit, measurement_count, **kwargs):
        self.name = name
        self.color = color
        self.conduit = conduit
        self.measurements = deque(maxlen=measurement_count)
        super().__init__(**kwargs)

    def dtw(self) -> float:
        times = [m.timestamp - self.time_zero for m in self.measurements]
        y_rotations = [m.quaternion.y_rotation() for m in self.measurements]
        test_values = rotation_function_ms(times)
        return dtw.distance_fast(test_values, y_rotations)

    def measure(self):
        measurement = self.conduit.measure()
        distance = self.dtw()
        self.measurements.append(measurement)

        if distance < 0.1:
            self.gauge += 1
        else:
            self.gauge = 0
            self.time_zero = self.measurements[0].timestamp

    def connect(self):
        self.conduit.connect()

    def disconnect(self):
        self.conduit.disconnect()

    def determine_state(self) -> SpiritState:
        if len(self.measurements) < self.measurements.maxlen:
            return SpiritState.inert
        if self.gauge < 10:
            return SpiritState.dormant
        if self.gauge < 40:
            return SpiritState.interested
        if self.gauge >= 40:
            return SpiritState.awakened

    def notify_state(self):
        self.conduit.notify_state(self.state)

    def dance(self):
        self.connect()
        try:
            while True:
                self.measure()
                state = self.determine_state()
                if state != self.state:
                    self.state = state
                    self.notify_state()
        finally:
            self.disconnect()

