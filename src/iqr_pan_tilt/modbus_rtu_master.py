from serial import Serial
from time import sleep
from threading import Lock
from ctypes import c_uint8, c_uint16

REBACK_SLEEP_MS = 5


class ModbusRTUMaster:
    def __init__(self, port_name: str, baud_rate: int) -> None:
        self._lock = Lock()
        self._com = Serial(port=port_name, baudrate=baud_rate, timeout=0.5)
        if self._com.is_open:
            print(f"Open serial port: {port_name} successful")
        sleep(0.1)

    def __del__(self):
        print("closing")
        self._com.close()

    def set_multiple_registers(self, slave_id: int, address: int, data):  # 0x10 = 16

        if not self._com.is_open:
            print("serial not open!!")
            return 0
        length = len(data)
        with self._lock:
            self._com.flush()
            function_num = 0x10
            send_buffer = []
            send_buffer.append(slave_id)
            send_buffer.append(function_num)
            send_buffer.append(c_uint8((address & 0xff00) >> 8).value)
            send_buffer.append(c_uint8((address & 0x00ff)).value)
            send_buffer.append(c_uint8((length & 0xff00) >> 8).value)
            send_buffer.append(c_uint8((length & 0x00ff)).value)
            send_buffer.append(c_uint8((length & 0x00ff) * 2).value)
            buffer_index = 6
            for d in data:
                send_buffer.append(c_uint8((d & 0xff00) >> 8).value)
                send_buffer.append(c_uint8((d & 0x00ff)).value)
                buffer_index += 2

            crc = ModbusRTUMaster._mod_bus_crc(send_buffer)
            c0 = c_uint8((crc & 0x00ff)).value
            c1 = c_uint8((crc & 0xff00) >> 8).value
            send_buffer.append(c0)
            send_buffer.append(c1)

            buffer_length = buffer_index + 3
            write_length = self._com.write(bytearray(send_buffer))
            if (buffer_length != write_length):
                print("Failed to send message!!")
                self._com.flush()
                return 0

            sleep(REBACK_SLEEP_MS/1000)

            receive_length = 8
            for i in range(3):
                receive_buffer = self._com.read(receive_length)
                if len(receive_buffer) > 0:
                    break
                print(f"try {i}")
                write_length = self._com.write(bytearray(send_buffer))

            if (receive_length != len(receive_buffer)):
                print("Failed to read message!!set")
                self._com.flush()
                return 0
            if (receive_buffer[0] != slave_id):
                print("Message ID error!!")
                self._com.flush()
                return 0
            if (receive_buffer[1] != function_num):
                print("Message fuction number error!!")
                self._com.flush()
                return 0

            temp_address = c_uint16(
                (receive_buffer[2] << 8) | receive_buffer[3]).value
            temp_length = c_uint16((receive_buffer[4] << 8)
                                   | receive_buffer[5]).value

            if (temp_address != address):
                print("Message start address error!!")
                self._com.flush()
                return 0

            if (temp_length != length):
                print("Message read length error!!")
                self._com.flush()
                return 0

            rec_crc = ModbusRTUMaster._mod_bus_crc(
                receive_buffer[:receive_length - 2])
            rec_crc_ = c_uint16((receive_buffer[receive_length - 1] << 8)
                                | (receive_buffer[receive_length - 2])).value

            if (rec_crc != rec_crc_):
                print("Message crc check error!!")
                self._com.flush()
                return 0

            self._com.flush()
        return 1

    def get_multiple_registers(self, slave_id: int, address: int, length: int):  # 0x03 = 03
        if not self._com.is_open:
            print("serial not open!!")
            return []
        with self._lock:
            self._com.flush()

            function_num = 0x03
            send_buffer = [0 for _ in range(8)]

            send_buffer[0] = slave_id
            send_buffer[1] = function_num
            send_buffer[2] = c_uint8((address & 0xff00) >> 8).value
            send_buffer[3] = c_uint8((address & 0x00ff)).value
            send_buffer[4] = c_uint8((length & 0xff00) >> 8).value
            send_buffer[5] = c_uint8((length & 0x00ff)).value
            crc = ModbusRTUMaster._mod_bus_crc(send_buffer[:6])
            send_buffer[6] = c_uint8((crc & 0x00ff)).value
            send_buffer[7] = c_uint8((crc & 0xff00) >> 8).value

            write_length = self._com.write(send_buffer)

            if (write_length != 8):
                print("Failed to send message!!")
                self._com.flush()
                return []

            sleep(REBACK_SLEEP_MS/1000)

            receive_length = (length * 2) + 5
            receive_buffer = self._com.read(receive_length)
            read_length = len(receive_buffer)

            if (receive_length != read_length):
                print("Failed to read message!!get")
                self._com.flush()
                return []

            if (receive_buffer[0] != slave_id):
                print("Message ID error!!")
                self._com.flush()
                return []

            if (receive_buffer[1] != function_num):
                print("Message fuction number error!!")
                self._com.flush()
                return []

            if (receive_buffer[2] != (length * 2)):
                print("Message data length error!!")
                self._com.flush()
                return []

            rec_crc = ModbusRTUMaster._mod_bus_crc(
                receive_buffer[:receive_length - 2])
            rec_crc_ = c_uint16((receive_buffer[receive_length - 1] << 8)
                                | (receive_buffer[receive_length - 2])).value

            if (rec_crc != rec_crc_):
                print("Message crc check error!!")
                self._com.flush()
                return []

            data = []
            for i in range(length):
                data.append(
                    c_uint16((receive_buffer[3 + i * 2] << 8) | (receive_buffer[4 + i * 2])).value)

        self._com.flush()
        return data

    @staticmethod
    def _mod_bus_crc(data):
        crc = 0xFFFF

        for d in data:
            crc = crc ^ d
            for _ in range(8):
                if (crc & 0x0001):
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc = crc >> 1

        return crc
