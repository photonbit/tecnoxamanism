import pytest
from unittest.mock import Mock, patch
from channelling_portal.entities import Spirit, SpiritState, Measurement, Quaternion, SerialSpiritCommunication, BLESpiritCommunication, WifiSpiritCommunication


class TestSpirit:
    @pytest.fixture
    def spirit(self):
        conduit_mock = Mock()
        return Spirit(name="Test", color="Blue", conduit=conduit_mock, measurement_count=10)

    def test_measure_invokes_conduit_measure(self, spirit):
        spirit.measure()
        spirit.conduit.measure.assert_called_once()

    def test_connect_invokes_conduit_connect(self, spirit):
        spirit.connect()
        spirit.conduit.connect.assert_called_once()

    def test_disconnect_invokes_conduit_disconnect(self, spirit):
        spirit.disconnect()
        spirit.conduit.disconnect.assert_called_once()

    def test_notify_state_invokes_conduit_notify_state(self, spirit):
        spirit.notify_state()
        spirit.conduit.notify_state.assert_called_once_with(spirit.state)


class TestSerialSpiritCommunication:
    @pytest.fixture
    def comm(self):
        with patch('serial.Serial') as serial_mock:
            return SerialSpiritCommunication(port="COM3", baud_rate=9600)

    def test_connect_opens_serial_port(self, comm):
        comm.connect()
        comm.serial.assert_called_once_with(comm.port, comm.baud_rate)

    def test_disconnect_closes_serial_port(self, comm):
        comm.connect()
        comm.disconnect()
        comm.serial.close.assert_called_once()

class TestBLESpiritCommunication:
    @pytest.fixture
    def comm(self):
        with patch('bluepy.btle.Peripheral') as peripheral_mock:
            return BLESpiritCommunication(mac_address="00:00:00:00:00:00", service_uuid="0000", characteristic_uuid="0000")

    def test_connect_establishes_ble_connection(self, comm):
        comm.connect()
        comm.peripheral.assert_called_once_with(comm.mac_address)

    def test_disconnect_closes_ble_connection(self, comm):
        comm.connect()
        comm.disconnect()
        comm.peripheral.disconnect.assert_called_once()

class TestWifiSpiritCommunication:
    @pytest.fixture
    def comm(self):
        with patch('socket.socket') as socket_mock:
            return WifiSpiritCommunication(ip_address="192.168.1.1", port=8080)

    def test_connect_opens_socket(self, comm):
        comm.connect()
        comm.server_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)

    def test_disconnect_closes_socket(self, comm):
        comm.connect()
        comm.disconnect()
        comm.server_socket.close.assert_called_once()
