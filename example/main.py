from iqr_pan_tilt import PanTiltDriver

with PanTiltDriver() as ptd:
    ptd.set_pose(yaw=60, pitch=60, speed=30, block=True)
    ptd.set_pose(yaw=50, pitch=40, speed=30, block=True)
    ptd.set_pose(yaw=30, pitch=20, speed=30, block=True)
    ptd.set_pose(yaw=-30, pitch=-20, speed=30, block=True)
    print(ptd.get_status())

print("end")