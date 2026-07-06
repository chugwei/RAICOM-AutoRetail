#encoding: UTF-8
#!/usr/bin/env python2

import mobile_to_goal, sonor
from Basic import Rob_basic
from GrabParams import grabParams
from movement import Movement
from sonor import Sonor
from obj_detect import Detect_marker
from obj_follow import Follow_object
from pymycobot.mycobot import MyCobot

import time, rospy, cv2
import math

if __name__ == '__main__':
    # 初始化所有模块

    # mc = MyCobot(grabParams.usb_dev, grabParams.baudrate)
    # mc.set_color(255,0,0)
    # time.sleep(1)
    # mc.set_color(0,255,0)follow.open_camera()

    # 视觉搜索物体
    # detect_result = follow.moving_search()
    # 初始化节点

    rospy.init_node('send_goals_python',anonymous=True)
    basic = Rob_basic()                                         #调用Basic的Rob_basic类
    move = Movement()                                           #调用movement的Movement类
    # sonor = Sonor()                                             #调用sonor的Sonor类
    Detect = Detect_marker()                                    #调用obj_detect的Detect_marker类
    follow = Follow_object()                                    #调用obj_follow的Follow_object类

    for _ in range (4):
        move.right_trapezoidal(196.5, 0.8, 1.5)
        time.sleep(0.5)


    # # 梯形控制左转90度，最大角速度0.4rad/s，减速时间1.5秒
    # move.left_trapezoidal(96, 0.6, 1.5)

    # # 梯形控制右转180度，最大角速度0.3rad/s，减速时间2.0秒
    # move.right_trapezoidal(188, 0.6, 1.5)

    # # 梯形控制左转90度，最大角速度0.4rad/s，减速时间1.5秒
    # move.left_trapezoidal(96, 0.6, 1.5)