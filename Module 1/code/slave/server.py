from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartAsyncTcpServer


class ModbusServer:
    def __init__(self):
        # Define a sequential data block
        self.store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, [0] * 100),
            co=ModbusSequentialDataBlock(0, [0] * 100),
            hr=ModbusSequentialDataBlock(0, [0] * 100),
            ir=ModbusSequentialDataBlock(0, [0] * 100))

        self.context = ModbusServerContext(slaves=self.store, single=True)

        # Define Modbus device identification
        self.identity = ModbusDeviceIdentification()
        self.identity.VendorName = 'Wybren Oppedijk'
        self.identity.ProductCode = 'xD'
        self.identity.VendorUrl = 'https://dtu.dk'
        self.identity.ProductName = 'Pump Station'
        self.identity.ModelName = 'Alessandros Magic Pump Station Model'
        self.identity.MajorMinorRevision = '1.0.69'

    async def start_server(self):
        # Start the server
        await StartAsyncTcpServer(context=self.context, identity=self.identity, address=('localhost', 502))

    def write_to_ir(self, start_address: int, values: list):
        """This function writes a value to the input register."""
        fc_as_hex = 4
        self.store.setValues(fc_as_hex, start_address, values)

    def read_ir(self, start_address: int, count: int):
        """This function reads a value from the input register """
        fc_as_hex = 4
        self.store.getValues(fc_as_hex, start_address, count)

    def read_hr(self, start_address: int, count):
        """This function reads a value from the holding register"""
        fc_as_hex = 3
        return self.store.getValues(fc_as_hex, start_address, count)
