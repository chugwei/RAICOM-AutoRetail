#encoding: UTF-8
#!/usr/bin/env python2
#########################################################################################
# 积木抓取
#########################################################################################
from pymycobot.mycobot import MyCobot
from pymycobot.genre import Coord
from pymycobot.genre import Angle
import time 
import basic
from GrabParams import grabParams

#机械臂上电
mc = MyCobot(grabParams.usb_dev, grabParams.baudrate)
# mc.send_coords(grabParams.coords_grab, 30, 0)
# coords_ready = [-49.9, -92.1, 350, 90.51, 47.11, -7.27]
# coords_grab = [-49.9, -170, 350, 90.51, 47.11, -7.27]
if grabParams.site == "left":

    # mc.send_coord(Coord.Z.value, grabParams.coords_ready[2] + 30, 50)
    # time.sleep(1.5)
    # mc.send_coords(grabParams.coords_ready, 20, 0)
    
    

    # 夹爪前移抓取木块
    # basic.move_to_my_coords2(grabParams.coords_grab,50,4)
    mc.send_coord(Coord.Y.value, grabParams.coords_ready[1] - 92, 30,) # -170
    time.sleep(1.5)
    mc.set_gripper_value(40,50)
    time.sleep(1)
    # 夹爪回到准备动作
    mc.send_angles(grabParams.angles_ready,40)
    # mc.send_coords(grabParams.coords_ready, 40, 0)
    # # mc.send_coord(Coord.Y.value, -120, 20)
    time.sleep(1.5)
    # # 夹爪下移
    mc.send_coord(Coord.Z.value, grabParams.coords_ready[2] - 100,50) # 260 90     mc.send_coord(Coord.Z.value, grabParams.coords_ready[2] - 110, 50) -90
    time.sleep(1)
    # 夹爪前移放置木块
    mc.send_coord(Coord.Y.value, grabParams.coords_ready[1] - 100, 45) # -170  78
    time.sleep(1.5)
    mc.set_gripper_value(255,50) # 255,50
    time.sleep(1.5)
    # 夹爪后移
    mc.send_coord(Coord.Y.value, grabParams.coords_ready[1] - 18, 30) #  -18 -110
    time.sleep(1.5)
    # 夹爪回到准备动作
    # mc.send_coords(grabParams.coords_ready, 50, 0)
    mc.send_angles(grabParams.angles_ready,50)

    
    time.sleep(1.5)
    #mc.send_coords(grabParams.coords_ready1, 40, 0) 

elif grabParams.site == "right":
    # 夹爪前移抓取木块
    mc.send_coord(Coord.Y.value, grabParams.coords_ready[1] + 78, 30) # -170
    time.sleep(1.5)
    mc.set_gripper_value(40,50)
    time.sleep(1)
    # 夹爪回到准备动作
    mc.send_coords(grabParams.coords_ready, 40, 0)
    # mc.send_coord(Coord.Y.value, -120, 20)
    time.sleep(1.5)
    # 夹爪下移
    mc.send_coord(Coord.Z.value, grabParams.coords_ready[2] - 90, 50) # 260  - 90    #mc.send_coord(Coord.Z.value, grabParams.coords_ready[2] - 90, 50)
    time.sleep(1)
    # 夹爪前移放置木块
    mc.send_coord(Coord.Y.value, grabParams.coords_ready[1] + 78, 40) # -170
    time.sleep(1.5)
    mc.set_gripper_value(255,50)
    time.sleep(1.5)
    # 夹爪后移
    mc.send_coord(Coord.Y.value, grabParams.coords_ready[1] + 18, 30) # -110
    time.sleep(1.5)
    # 夹爪回到准备动作
    # mc.send_coords(grabParams.coords_ready, 50, 0)