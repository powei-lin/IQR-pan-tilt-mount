from time import sleep
from pan_tilt_driver import PanTiltDriver

with PanTiltDriver() as ptd:
    yaw, pitch = ptd.getPose()
    print(yaw, pitch)
    sleep(3)
    ptd.setPose(yaw=60, pitch=60, speed=30)
    sleep(3)
    yaw, pitch = ptd.getPose()
    print(yaw, pitch)
    sleep(3)
    ptd.setPose(yaw=-60, pitch=-60, speed=30)
    sleep(3)
    yaw, pitch = ptd.getPose()
    print(yaw, pitch)
    print(ptd.getStatus())

print("end")