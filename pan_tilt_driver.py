from time import sleep
from dataclasses import dataclass
from threading import Thread, Lock
from modbus_rtu_master import ModbusRTUMaster, UINT16, UINT8


@dataclass
class PanTiltStatus:
    # offect
    id: int = 0  # 0
    serial_num: str = ""  # 1
    hw_version: str = ""  # 2
    bd_version: str = ""  # 3
    sw_version: str = ""  # 4
    set_zero: int = 0  # 5
    speed: int = 0  # 6
    yaw_goal: float = 0.0  # 7
    pitch_goal: float = 0.0  # 8
    reserved: int = 0  # 9
    driver_ec: int = 0  # 10
    encoder_ec: int = 0  # 11
    yaw_now: float = 0.0  # 12
    pitch_now: float = 0.0  # 13
    yaw_temp: float = 0.0  # 14
    pitch_temp: float = 0.0  # 15
    yaw_raw: int = 0  # 16
    pitch_raw: int = 0  # 17
    loop_ec: int = 0  # 18
    loop_time: int = 0  # 19


class PanTiltDriver:
    def __enter__(self):
        self.start()
        return self
    def __exit__(self, type, value, traceback):
        self.set_pose(0, 0, 10)
        self._stop()

    def __init__(self, port_name :str = "/dev/pan_tilt") -> None:
        self._id = 1
        self._master = ModbusRTUMaster(port_name, 115200)
        self._read_flag = True
        self._lock = Lock()
        self._st = PanTiltStatus()
        sleep(0.5)
        self.set_pose(0.02, 0.0, 10)
    
    def start(self):
        self.td = Thread(target=self._run)
        self.td.start()

    def __del__(self):
        self._stop()

    def getStatus(self) -> PanTiltStatus:
        return self._st

    def get_pose(self) -> tuple:
        with self._lock:
            yaw = self._st.yaw_now
            pitch = self._st.pitch_now
        return yaw, pitch

    def set_pose(self, yaw:float, pitch:float, speed:int):
        if yaw < -60.0 or yaw > 60.0:
            print("yaw !!")
            return
        if pitch < -60.0 or pitch > 60.0:
            print("yaw !!")
            return
        if speed < 1 or speed > 30:
            print("speed !!!")
            return
    
        with self._lock:
            sendBuf = [speed, int(yaw*100.0), int(pitch*100)]
            self._master.set_multiple_registers(self._id, 0x0006, sendBuf)

    def _run(self):
        while (self._read_flag):
            with self._lock:
                rcvdBuf = self._master.GetMultipleRegisters(self._id, 0x0000, 20)
                if (rcvdBuf):
                    self._st.id = rcvdBuf[0]
                    self._st.serial_num = f"SN{int(rcvdBuf[1])}"
                    self._st.hw_version = f"v{int((rcvdBuf[2] & 0xff00) >> 8)}.{int(rcvdBuf[2] & 0x00ff)}"
                    self._st.bd_version = f"v{int((rcvdBuf[3] & 0xff00) >> 8)}.{int(rcvdBuf[3] & 0x00ff)}"
                    self._st.sw_version = f"v{int((rcvdBuf[4] & 0xf000) >> 12)}.{int((rcvdBuf[4] & 0x0f00) >> 8)}.{int(rcvdBuf[4] & 0x00ff)}"
                    self._st.set_zero = rcvdBuf[5]
                    self._st.speed = rcvdBuf[6]
                    self._st.yaw_goal = int(rcvdBuf[7]) / 100.0
                    self._st.pitch_goal = int(rcvdBuf[8]) / 100.0
                    self._st.reserved = rcvdBuf[9]
                    self._st.driver_ec = rcvdBuf[10]
                    self._st.encoder_ec = rcvdBuf[11]
                    self._st.yaw_now = int(rcvdBuf[12]) / 100.0
                    self._st.pitch_now = int(rcvdBuf[13]) /100.0
                    self._st.yaw_temp = int(rcvdBuf[14]) / 10.0
                    self._st.pitch_temp = int(rcvdBuf[15]) /10.0
                    self._st.yaw_raw = int(rcvdBuf[16])
                    self._st.pitch_raw = int(rcvdBuf[17])
                    self._st.loop_ec = rcvdBuf[18]
                    self._st.loop_time = rcvdBuf[19]
            sleep(0.1)
    def _stop(self):
        if self._read_flag:
            with self._lock:
                self._read_flag = False
        if self.td:
            self.td.join()