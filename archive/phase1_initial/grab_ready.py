#! /usr/bin/env python
#coding=UTF-8
#########################################################################################
# 积木抓取
#########################################################################################
from pymycobot.mycobot import MyCobot
from pymycobot.genre import Coord
from pymycobot.genre import Angle
import time, rospy

from GrabParams import grabParams
from movement import Movement
import basic

if __name__ == '__main__':
    if grabParams.site == "left":
        rospy.init_node('Grab_ready',anonymous=True)
        move = Movement()
        #机械臂上电
        mc = MyCobot(grabParams.usb_dev, grabParams.baudrate)
        mc.power_on()
        time.sleep(1)
        # 抓取准备
        mc.set_gripper_value(255,50)
        
        mc.send_angles(grabParams.angles_ready, 60)
        # mc.send_coords(grabParams.coords_ready, 60, 0)
        
        # move.moveforward(0.21, 4)
        # move.rotate_to_left(0.55, 2.7) # 这里要旋转90°

    elif grabParams.site == "right":
        rospy.init_node('Grab_ready',anonymous=True)
        move = Movement()
        #机械臂上电
        mc = MyCobot(grabParams.usb_dev, grabParams.baudrate)
        mc.power_on()
        time.sleep(1)
        # 抓取准备
        mc.set_gripper_value(255,50)
        # mc.send_angles(grabParams.angles_ready, 60)
        # time.sleep(1.5)
        mc.send_coords(grabParams.coords_ready, 60, 0)
        
        # move.moveforward(0.21, 4)
        # move.rotate_to_left(0.55, 2.7) # 这里要旋转90°