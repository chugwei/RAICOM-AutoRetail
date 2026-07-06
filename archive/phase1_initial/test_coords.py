#! /usr/bin/env python
#coding=UTF-8
#########################################################################################
# 积木抓取
#########################################################################################

from pymycobot.mycobot import MyCobot
from pymycobot.genre import Coord
from pymycobot.genre import Angle
from GrabParams import grabParams
import time 

# coords_ready = [-62.1, -79.3, 264.1, 91.96, 47.9, 0.48]
# coords_grap = [-49.9, -170, 350, 90.51, 47.11, -7.27]
# #机械臂上电[-39.9, -174.9, 260.1, 100.4, 51.93, 0.53]
mc = MyCobot("/dev/arm",115200)
mc.power_on()
time.sleep(1)

# mc.set_gripper_value(255,50)
# mc.send_coords(coords_ready, 20, 0)
# time.sleep(4)

# mc.send_coord(Coord.Y.value, -170, 30)
# time.sleep(2)
# mc.set_gripper_value(40,50)
# time.sleep(1)
# mc.send_coords(coords_ready, 40, 0)
# # mc.send_coord(Coord.Y.value, -120, 20)
# time.sleep(2)
# mc.send_coord(Coord.Z.value, 265, 20)
# time.sleep(2)
# mc.send_coord(Coord.Y.value, -170, 30)
# time.sleep(2)
# mc.set_gripper_value(255,50)
# time.sleep(2)
# mc.send_coord(Coord.Y.value, -110, 30)
# time.sleep(2)
mc.send_angles(grabParams.angles_ready,30)
# mc.send_coords(grabParams.coords_ready, 50, 0)
# mc.release_servo(5)
# time.sleep(10)
# mc.focus_servo(5)
