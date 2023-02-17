from argparse import ArgumentParser
from iqr_pan_tilt import PanTiltDriver


def main():
    parser = ArgumentParser("Command line tool to move")
    parser.add_argument("yaw", type=float)
    parser.add_argument("pitch", type=float)
    parser.add_argument("speed", type=float, default=10)
    args = parser.parse_args()

    with PanTiltDriver(start_identity=False, end_identity=False) as ptd:
        ptd.set_pose(yaw=float(args.yaw), pitch=float(
            args.pitch), speed=int(args.speed))


if __name__ == '__main__':
    main()
