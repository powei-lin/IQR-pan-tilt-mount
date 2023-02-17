from serial import Serial
from time import sleep
from threading import Lock


REBACK_SLEEP_MS = 5
UINT8 = 2**8
UINT16 = 2**16


class ModbusRTUMaster:
    def __init__(self, port_name: str, baud_rate: int) -> None:
        self._lock = Lock()
        self._com = Serial(port=port_name, baudrate=baud_rate, timeout=0.5)
        if self._com.is_open:
            print(f"open serial port: {port_name} successful!!")
        sleep(0.5)

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
            send_buffer.append(((address & 0xff00) >> 8) % UINT8)
            send_buffer.append(((address & 0x00ff)) % UINT8)
            send_buffer.append(((length & 0xff00) >> 8) % UINT8)
            send_buffer.append(((length & 0x00ff)) % UINT8)
            send_buffer.append(((length & 0x00ff) * 2) % UINT8)
            buffer_index = 6
            self._com.write(bytearray(send_buffer))
            for d in data:
                send_buffer.append(((d & 0xff00) >> 8) % UINT8)
                send_buffer.append(((d & 0x00ff)) % UINT8)
                buffer_index += 2

            crc = ModbusRTUMaster._ModBusCRC(send_buffer)
            c0 = ((crc & 0x00ff)) % UINT8
            c1 = ((crc & 0xff00) >> 8) % UINT8
            send_buffer.append(c0)
            send_buffer.append(c1)

            buffer_length = buffer_index + 3
            write_length = self._com.write(bytearray(send_buffer))
            if (buffer_length != write_length):
                print("Failed to send message!!")
                self._com.flush()
                return 0

            sleep(REBACK_SLEEP_MS/1000)
            
            write_length = self._com.write(bytearray(send_buffer))
            receive_length = 8
            receive_buffer = self._com.read(receive_length)

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

            temp_address = (
                (receive_buffer[2] << 8) | receive_buffer[3]) % UINT16
            temp_length = ((receive_buffer[4] << 8)
                           | receive_buffer[5]) % UINT16

            if (temp_address != address):
                print("Message start address error!!")
                self._com.flush()
                return 0

            if (temp_length != length):
                print("Message read length error!!")
                self._com.flush()
                return 0

            rec_crc = ModbusRTUMaster._ModBusCRC(
                receive_buffer[:receive_length - 2])
            rec_crc_ = ((receive_buffer[receive_length - 1] << 8)
                        | (receive_buffer[receive_length - 2])) % UINT16

            if (rec_crc != rec_crc_):
                print("Message crc check error!!")
                self._com.flush()
                return 0

            self._com.flush()
        return 1

    def GetMultipleRegisters(self, slave_id: int, address: int, length: int):  # 0x03 = 03
        if not self._com.is_open:
            print("serial not open!!")
            return []
        with self._lock:
            self._com.flush()

            function_num = 0x03
            send_buffer = [0 for _ in range(8)]

            send_buffer[0] = slave_id
            send_buffer[1] = function_num
            send_buffer[2] = ((address & 0xff00) >> 8)%UINT8
            send_buffer[3] = ((address & 0x00ff))%UINT8
            send_buffer[4] = ((length & 0xff00) >> 8)%UINT8
            send_buffer[5] = ((length & 0x00ff))%UINT8
            crc = ModbusRTUMaster._ModBusCRC(send_buffer[:6])
            send_buffer[6] = ((crc & 0x00ff))%UINT8
            send_buffer[7] = ((crc & 0xff00) >> 8)%UINT8

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

            rec_crc = ModbusRTUMaster._ModBusCRC(receive_buffer[:receive_length - 2])
            rec_crc_ = ((receive_buffer[receive_length - 1] << 8) | (receive_buffer[receive_length - 2]))%UINT16

            if (rec_crc != rec_crc_):
                print("Message crc check error!!")
                self._com.flush()
                return []

            data = []
            for i in range(length):
                data.append(((receive_buffer[3 + i * 2] << 8) | (receive_buffer[4 + i * 2]))%UINT16)

        self._com.flush()
        return data

    @staticmethod
    def _ModBusCRC(data):
        crc = 0xFFFF

        for d in data:
            crc = crc ^ d
            for _ in range(8):
                if (crc & 0x0001):
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc = crc >> 1

        return crc