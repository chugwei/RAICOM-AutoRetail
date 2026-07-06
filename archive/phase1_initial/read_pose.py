#!/usr/bin/env python2
# coding: UTF-8
# 先解锁手动摆位，再读取当前关节角和末端坐标

from pymycobot.mycobot import MyCobot
import time
from GrabParams import grabParams


def wait_input(prompt):
    """兼容 Python2/3 的输入函数。"""
    try:
        return raw_input(prompt)
    except NameError:
        return input(prompt)


def read_six_values(getter, retry_times=6, retry_delay=0.05):
    """读取 6 维数据（角度或坐标），失败时短暂重试。"""
    values = []
    count = 0
    while len(values) < 6 and count < retry_times:
        values = getter() or []
        if len(values) == 6:
            return [round(v, 2) for v in values]
        time.sleep(retry_delay)
        count += 1
    return values


def focus_all_servos(mc):
    """逐个关节锁轴（BR280 文档接口：focus_servo(1~6)）。"""
    for servo_id in range(1, 7):
        mc.focus_servo(servo_id)
        time.sleep(0.05)


def main():
    # 串口参数与项目配置保持一致
    mc = MyCobot(grabParams.usb_dev, grabParams.baudrate)
    mc.power_on()
    time.sleep(1)

    # BR280 文档：release_all_servos() 进入自由移动模式（可手动摆动）
    mc.release_all_servos()
    print("机械臂已解锁（自由移动模式）。")
    print("请手动调整到目标姿态。")

    cmd = wait_input("调整完成后按回车开始读取；输入 q 回车退出：").strip().lower()
    if cmd == "q":
        print("已退出。")
        return

    # 可选锁轴：减少读取时姿态漂移
    lock_cmd = wait_input("读取前是否锁轴？(Y/n，默认Y)：").strip().lower()
    if lock_cmd in ("", "y", "yes"):
        focus_all_servos(mc)
        time.sleep(0.3)
        print("已锁轴，开始实时读取。")
    else:
        print("保持解锁状态，开始实时读取。")

    print("按 Ctrl+C 结束。")

    while True:
        angles = read_six_values(mc.get_angles)
        coords = read_six_values(mc.get_coords)

        if len(angles) == 6:
            print("angles_ready = {}".format(angles))
        else:
            print("angles_ready = <invalid: {}>".format(angles))

        if len(coords) == 6:
            print("coords_ready = {}".format(coords))
        else:
            print("coords_ready = <invalid: {}>".format(coords))

        print("-" * 50)
        time.sleep(0.2)  # 5Hz


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
