from time import sleep
from iqr_pan_tilt import PanTiltDriver

with PanTiltDriver() as ptd:
    yaw, pitch = ptd.get_pose()
    print(yaw, pitch)
    sleep(3)
    ptd.set_pose(yaw=60, pitch=60, speed=30)
    sleep(3)
    yaw, pitch = ptd.get_pose()
    print(yaw, pitch)
    sleep(3)
    ptd.set_pose(yaw=-60, pitch=-60, speed=30)
    sleep(3)
    yaw, pitch = ptd.get_pose()
    print(yaw, pitch)
    print(ptd.getStatus())

print("end")