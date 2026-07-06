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
    # 初始化所有模块

    # mc = MyCobot(grabParams.usb_dev, grabParams.baudrate)
    # mc.set_color(255,0,0)
    # time.sleep(1)
    # mc.set_color(0,255,0)follow.open_camera()

    # 视觉搜索物体
    # detect_result = follow.moving_search()


    rospy.init_node('send_goals_python',anonymous=True)
    basic = Rob_basic()                                         #调用Basic的Rob_basic类
    move = Movement()                                           #调用movement的Movement类
    # sonor = Sonor()                                             #调用sonor的Sonor类
    Detect = Detect_marker()                                    #调用obj_detect的Detect_marker类
    follow = Follow_object()                                    #调用obj_follow的Follow_object类

    move.moveforward(0.15, 1.2)
    #障碍物在左边
    # move.moveforward(0.15, 1.6)
    # time.sleep(0.5)
    move.left_trapezoidal(280,0.8,1)
    # move.left_trapezoidal(100,1,1.5)        #check



    # # # 最终导航到目标点
    # goal_3 = mobile_to_goal.read_goal("goal_3.txt")
    # goal_number = 3
    # print("坐标3_初始点接收完毕...")
    # mobile_to_goal.send_goal(goal_number, goal_3)
    # print("到达坐标3_初始点...")
    # # reach_goal4()
    goal_1 = mobile_to_goal.read_goal("goal_1.txt")
    goal_number = 1
    print("坐标1_初始点接收完毕...")
    mobile_to_goal.send_goal(goal_number, goal_1)
    print("到达坐标1_初始点...")
    time.sleep(0.5)
    for _ in range(2):  
        distance = Sonor().get_sonor_data()
        print(distance)
        Sonor().sonor_control_goal_4()

    move.right_trapezoidal(100, 0.8, 1.5)
    time.sleep(0.5)
    # move.forward_trapezoidal(0.42,0.15,1)

    distance2 = Sonor().get_sonor_data()
    if distance2 > 15:
        lenth = distance2 - 15
        move.forward_trapezoidal(lenth,0.1,1)
        print("moving```")
    else:
        move.stop()

    # Sonor().sonor_control_last()
    time.sleep(0.5)
    for _ in range(2):  #8
        distance = Sonor().get_sonor_data()    
        print(distance)
        
        Sonor().sonor_control_goal_3()