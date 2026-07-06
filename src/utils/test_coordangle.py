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
from pymycobot import MyCobot
from pymycobot.genre import Angle

import time, rospy, cv2


if __name__ == '__main__':
    # 初始化所有模块

    # mc = MyCobot(grabParams.usb_dev, grabParams.baudrate)
    # mc.set_color(255,0,0)
    # time.sleep(1)
    # mc.set_color(0,255,0)
    mc = MyCobot("/dev/arm", 115200)
    rospy.init_node('send_goals_python',anonymous=True)
    basic = Rob_basic()                                         #调用Basic的Rob_basic类
    move = Movement()                                           #调用movement的Movement类
    # sonor = Sonor()                                             #调用sonor的Sonor类
    # Detect = Detect_marker()                                    #调用obj_detect的Detect_marker类
    # follow = Follow_object()   


    basic.move_to_my_angles([-87.36, -64.16, 69.34, 23.46, -2.81, 133.76],70,1.5)
    time.sleep(1)
    basic.move_to_my_angles([3.77, 20.74, -79.1, 65.56, -5.62, 40.25],80,1)
       
    basic.move_to_my_coords([120, -40, 128, -175.85, 0.76, -136.36],40,2)
    # basic.move_to_my_coords(grabParams.coords_ready,60,2)
    time.sleep(2.5)
    print("coords:", mc.get_coords())
    print("angles:", mc.get_angles())
    # basic.move_to_my_angles(grabParams.angles_ready,60,2)
    # # basic.grap(True)
    # time.sleep(0.5)
    # basic.move_to_my_coords(grabParams.coords_ready,60,0)
    # # basic.grap(False)
    # mc.send_coords([-62.1, -179.3, 300, 91.96, 47.9, 2],60,1)
    # time.sleep(3.5)
    # basic.move_to_my_coords(grabParams.coords_ready,60,1)
    # mc.send_angle(Angle.J2.value, 20, 30)
    # time.sleep(1)
    # basic.move_to_my_angles(grabParams.angles_ready,60,2)
    # # basic.move_to_my_coords(grabParams.coords_place_apple,60,3)
    # # basic.grap(False)

    # # # basic.move_to_my_angles(grabParams.angles_ready,20,4)
    # # # time.sleep(1)
    # # basic.move_to_my_coords(grabParams.coords_ready,60,4)
    # # basic.move_to_my_coords(grabParams.coords_place_apple,60,3)
    # # basic.move_to_my_coords(grabParams.coords_ready,60,4)
