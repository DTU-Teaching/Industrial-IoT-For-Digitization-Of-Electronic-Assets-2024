import logging
import struct
import time

from pymodbus.client import ModbusTcpClient

logging.basicConfig(level=logging.INFO)


class ModbusPumpstationClient:

    def __init__(self, host, port):
        self.client = ModbusTcpClient(host, port)
        self.CONTROL_IR = 0
        self.P1_SPEED_IR = 1
        self.P1_POWER_IR = 3
        self.P1_OUTFLOW_IR = 5
        self.P2_SPEED_IR = 7
        self.P2_POWER_IR = 9
        self.P2_OUTFLOW_IR = 11

        self.CONTROL_HR = 0
        self.P1_SPEED_HR = 1
        self.P2_SPEED_HR = 3

    def _convert_to_32_bit_integer(self, registers):
        handle = [struct.pack('>H', p) for p in registers]
        binary_string = b''.join(handle)
        return struct.unpack('!I', binary_string)[0]

    def convert_to_32_bit_float(self, registers):
        handle = [struct.pack('>H', p) for p in registers]
        binary_string = b''.join(handle)
        return struct.unpack('!f', binary_string)[0]

    def encode_32_bit_integer(self, value):
        byte_value = struct.pack('>I', int(value))
        return struct.unpack('>HH', byte_value)

    def _get_bool(self, pos):
        if not self.client.connected:
            self.client.connect()
        return self.client.read_input_registers(pos, 1).registers[0]

    def _get_float(self, pos):
        if not self.client.connected:
            self.client.connect()
        return self.convert_to_32_bit_float(self.client.read_input_registers(pos, 2).registers)

    def _get_int(self, pos):
        if not self.client.connected:
            self.client.connect()
        return self._convert_to_32_bit_integer(self.client.read_input_registers(pos, 2).registers)

    def in_control(self) -> int:
        return self._get_bool(self.CONTROL_IR)

    def get_p1_speed(self) -> int:
        return self._get_int(self.P1_SPEED_IR)

    def get_p2_speed(self) -> int:
        return self._get_int(self.P2_SPEED_IR)

    def get_p1_outflow(self) -> int:
        return self._get_float(self.P1_OUTFLOW_IR)

    def get_p2_outflow(self) -> int:
        return self._get_float(self.P2_OUTFLOW_IR)

    def get_p1_power(self) -> int:
        return self._get_float(self.P1_POWER_IR)

    def get_p2_power(self) -> int:
        return self._get_float(self.P2_POWER_IR)

    def toggle_control(self):
        if not self.client.connected:
            self.client.connect()
        self.client.write_register(self.CONTROL_HR, 1 if self.in_control() == 0 else 0)

    def set_p1_speed(self, speed):
        if not self.client.connected:
            self.client.connect()
        self.client.write_registers(self.P1_SPEED_HR, self.encode_32_bit_integer(speed))

    def set_p2_speed(self, speed):
        if not self.client.connected:
            self.client.connect()
        self.client.write_registers(self.P2_SPEED_HR, self.encode_32_bit_integer(speed))


if __name__ == '__main__':
    pc = ModbusPumpstationClient('127.0.0.1', 502)

    while True:
        logging.info(pc.client.read_input_registers(0, 12).registers)
        control = pc.in_control()
        p1_speed = pc.get_p1_speed()
        p2_speed = pc.get_p2_speed()
        p1_outflow = pc.get_p1_outflow()
        p2_outflow = pc.get_p2_outflow()
        p1_power = pc.get_p1_power()
        p2_power = pc.get_p2_power()
        logging.info(f"Control: {control}, P1 Speed: {p1_speed}, P2 Speed: {p2_speed}, P1 Outflow: {p1_outflow}, "
                     f"P2 Outflow: {p2_outflow}, P1 Power: {p1_power}, P2 Power: {p2_power}")
        time.sleep(1)
