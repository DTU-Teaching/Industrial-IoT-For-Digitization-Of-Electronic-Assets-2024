import asyncio
import logging
import struct
import threading

import numpy as np

from pump_station_data_generator import PumpSignalGenerator
from server import ModbusServer

logging.basicConfig(level=logging.INFO)


class PumpStation:

    def __init__(self):
        self.server: ModbusServer = ModbusServer()
        PUMP_SWITCHING_INTERVAL_SECONDS = 240
        self.CONTROL_HR = 0
        self.ERROR_HR = 1
        self.P1_SPEED_HR = 1
        self.P2_SPEED_HR = 3
        self.START_ADDRESS_HR = 0

        self.was_in_control = False

        self.START_IR = 0

        self.pg = PumpSignalGenerator(PUMP_SWITCHING_INTERVAL_SECONDS)
        self.local_control = True

    def start_modbus_server(self, loop):
        asyncio.set_event_loop(loop)
        asyncio.run(self.server.start_server())
        loop.run_forever()

    def run(self):
        loop = asyncio.new_event_loop()
        t = threading.Thread(target=self.start_modbus_server, args=(loop,))
        t.start()
        while True:
            if 0 == self.server.read_hr(self.CONTROL_HR, 1)[0]:
                if self.was_in_control:
                    self.was_in_control = False
                    self.pg.reset()
                values = [0] + self.get_16_bit_signals()
                logging.info(f"Writing {values} to {self.START_IR}")
                self.server.write_to_ir(self.START_IR,
                                        values)
            else:
                p1_speed = self.decode_to_32_bit_integer(self.server.read_hr(self.P1_SPEED_HR, 2)) + np.random.normal(
                    0, 0.1)
                p2_speed = self.decode_to_32_bit_integer(self.server.read_hr(self.P2_SPEED_HR, 2)) + np.random.normal(
                    0, 0.1)
                p1_speed, p2_speed = self.check_speed(p1_speed, p2_speed)
                self.server.write_to_ir(self.START_IR,
                                        [1] + self.get_16_bit_signals_external_control(p1_speed, p2_speed))
                self.was_in_control = True

    def get_16_bit_signals(self):
        p1_speed, p1_power, p1_outflow, p2_speed, p2_power, p2_outflow = self.pg.generate_signal()
        p1_speed = self.encode_32_bit_integer(p1_speed)
        p1_power = self.encode_32_bit_float(p1_power)
        p1_outflow = self.encode_32_bit_float(p1_outflow)
        p2_speed = self.encode_32_bit_integer(p2_speed)
        p2_power = self.encode_32_bit_float(p2_power)
        p2_outflow = self.encode_32_bit_float(p2_outflow)
        return list(p1_speed + p1_power + p1_outflow + p2_speed + p2_power + p2_outflow)

    def get_16_bit_signals_external_control(self, p1_speed, p2_speed):
        p1_speed, p1_power, p1_outflow, p2_speed, p2_power, p2_outflow = self.pg.apply_signals(p1_speed, p2_speed)
        p1_speed = self.encode_32_bit_integer(p1_speed)
        p1_power = self.encode_32_bit_float(p1_power)
        p1_outflow = self.encode_32_bit_float(p1_outflow)
        p2_speed = self.encode_32_bit_integer(p2_speed)
        p2_power = self.encode_32_bit_float(p2_power)
        p2_outflow = self.encode_32_bit_float(p2_outflow)
        return list(p1_speed + p1_power + p1_outflow + p2_speed + p2_power + p2_outflow)

    def check_speed(self, p1, p2):
        if p1 > 1500:
            p1 = 1500
        if p2 > 1500:
            p2 = 1500
        if p1 < 0:
            p1 = 0
        if p2 < 0:
            p2 = 0
        return p1, p2

    @staticmethod
    def encode_32_bit_integer(value):
        byte_value = struct.pack('>I', int(value))
        return struct.unpack('>HH', byte_value)

    @staticmethod
    def encode_32_bit_float(value):
        byte_value = struct.pack('>f', float(value))
        return struct.unpack('>HH', byte_value)

    @staticmethod
    def decode_to_32_bit_integer(registers):
        handle = [struct.pack('>H', p) for p in registers]
        binary_string = b''.join(handle)
        return struct.unpack('!I', binary_string)[0]

    @staticmethod
    def decode_to_32_bit_float( registers):
        handle = [struct.pack('>H', p) for p in registers]
        binary_string = b''.join(handle)
        return struct.unpack('!f', binary_string)[0]


if __name__ == '__main__':
    logging.info("Test")
    pump_station = PumpStation()
    pump_station.run()
