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

if __name__ == '__main__':
    # mc = MyCobot(grabParams.usb_dev, grabParams.baudrate)
    # mc.set_color(255,0,0)
    # time.sleep(1)
    # mc.set_color(0,255,0)
    rospy.init_node('send_goals_python',anonymous=True)
    basic = Rob_basic()
    move = Movement()
    # sonor = Sonor()
    Detect = Detect_marker()
    follow = Follow_object()


    move.moveback(0.25,1)
    