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

def goal1_gab(obj_info):
    x, y, width, height, label = obj_info
    # real_x, real_y = Detect_marker().get_position(-y,x) #0.2,1)  目标坐标值x＝摄像头返回值-y  y=摄像头返回值x
    if width > 165:
        real_y = grabParams.y_near
    elif 165 >=  width  >= 140:
        real_y = grabParams.y_middle
    else:
        real_y = grabParams.y_far
    print("------------")
    print(real_y)
    print("------------")
    Detect_marker().grab_move(0, real_y)#


if __name__ == '__main__':
    # 初始化所有模块

    # mc = MyCobot(grabParams.usb_dev, grabParams.baudrate)
    # mc.set_color(255,0,0)
    # time.sleep(1)
    # mc.set_color(0,255,0)
    rospy.init_node('send_goals_python',anonymous=True)
    basic = Rob_basic()                                         #调用Basic的Rob_basic类
    move = Movement()                                           #调用movement的Movement类
    # sonor = Sonor()                                             #调用sonor的Sonor类
    Detect = Detect_marker()                                    #调用obj_detect的Detect_marker类
    follow = Follow_object()                                    #调用obj_follow的Follow_object类


    move.moveforward(0.05, 2.5)#0.05,2
    move.moveforward(0.5, 2)
    move.moveforward(0.2,1)

######第一次    
    #移动到目标点
    for _ in range(4):  #6
        distance = Sonor().get_sonor_data()
        print(distance)
        Sonor().sonor_control_goal_3()                      # 超声波精调
    time.sleep(1)
    move.rotate_to_right(0.55,2.7)                          # 右转(0.55,2.7)
    time.sleep(1)
    move.moveforward(0.05,2)  # 补充
    move.moveforward(0.2,1)                                 # 前进(0.1,2)
    move.moveforward(0.05,2.2)  # 补充
    time.sleep(0.5)

    #调整前后距离
    for _ in range(4):  #10
        distance = Sonor().get_sonor_data()
        print(distance)
        Sonor().sonor_control_goal_1()                      # 二次精调
    time.sleep(1)
    basic.move_to_my_angles(grabParams.angles_ready,80,1.5)
    move.rotate_to_left(0.55, 2.7) # (0.55, 2.7)旋转90°      # 左转复位

    time.sleep(1)
    # basic.move_to_my_angles(grabParams.angles_ready,60,0.5)
    move.moveforward(0.02,0.2)
    for _ in range(6):  
        distance = Sonor().get_sonor_data()
        Sonor().sonor_control_goal_2()

    # 机械臂初始化     
    Detect.init_mycobot()

    # 视觉搜索物体
    detect_result = follow.moving_search()
   
    #抓取物体
    goal1_gab(detect_result)
    

   #调整前后距离
    move.moveforward(0.05,1.5)
    for _ in range(5):  #8
        distance = Sonor().get_sonor_data()
        print(distance)
        # Sonor().sonor_control_goal_3()
        Sonor().sonor_control_goal_5()
    move.moveback(0.05,0.5)
    time.sleep(0.5)
    

    # 转身后退到放置位置
    move.rotate_to_right(0.53,2.8)    #
    time.sleep(0.5)

    #后退
    move.backward_trapezoidal(0.55, 0.4, 3)
    # move.moveback(0.05, 1)
    # move.moveback(0.1, 1)
    # move.moveback(0.2, 1)
    # move.moveback(0.15,0.3)
    # move.moveback(0.1, 1)
    # move.moveback(0.05, 1)
    # move.moveback(0.02, 1)

    # 根据物体类型放置
    x, y, width, height, label = detect_result
    if label == "clock":##
        basic.move_to_my_coords(grabParams.coords_place_clock,80,2.5)
        basic.grap(False)
        # basic.move_to_my_coords(grabParams.coords_place_clock2,80,0.5)
    else:
        basic.move_to_my_coords(grabParams.coords_place_apple,80,1.5)
        basic.grap(False)
        # basic.move_to_my_coords(grabParams.coords_place_apple2,80,0.5)



    # 返回准备位置 
    basic.move_to_my_angles(grabParams.angles_ready,60,0.5)   
    move.moveforward(0.05, 1)
    move.moveforward(0.1, 1)
    basic.move_to_my_coords(grabParams.coords_ready,80,0)
    move.moveforward(0.2, 1.5)
    move.moveforward(0.05, 1)
    
    # # 调整姿态准备下一次任务
   
    # move.moveforward(0.05, 1)
    # move.moveforward(0.1, 1)
    # move.moveforward(0.2, 1.5)
    # move.moveforward(0.05, 1)

# # # # 第二次
    # 移动到目标点

    time.sleep(0.5)

    # 超声波精确定位
    for _ in range(4):  
        distance = Sonor().get_sonor_data()
        print(distance)
        Sonor().sonor_control_goal_1()
    time.sleep(1)
    move.rotate_to_left(0.55,2.7)
    time.sleep(1)
    # 超声波精确定位（8次调整）
    for _ in range(4):  
        distance = Sonor().get_sonor_data()
        print(distance)
        Sonor().sonor_control_goal_6()   
    time.sleep(0.5)
    # move.moveforward(0.2,0.8)
    # 重新打开摄像头
    follow.open_camera()

    # 视觉搜索物体
    detect_result = follow.moving_search()

    # 执行抓取
    goal1_gab(detect_result)

    #调整前后距离
    move.moveforward(0.05, 1)
    for _ in range(5):  #8
        distance = Sonor().get_sonor_data()
        print(distance)
        # Sonor().sonor_control_goal_3()
        Sonor().sonor_control_goal_5()
    time.sleep(0.5)
    move.moveback(0.05,0.5)

    # 转身后退到放置位置
    move.rotate_to_right(0.53,2.8)    #.5############################右转还是有一点点大
    time.sleep(0.5)

    move.backward_trapezoidal(0.53, 0.4, 3)
    # move.moveback(0.05, 1)
    # move.moveback(0.1, 1)
    # move.moveback(0.2, 1)
    # move.moveback(0.15,0.3)
    # move.moveback(0.1, 0.8)
    # move.moveback(0.05, 1)
    # move.moveback(0.02, 0.8)

    # 根据物体类型放置
    x, y, width, height, label = detect_result
    if label == "clock":##
        basic.move_to_my_coords(grabParams.coords_place_clock,80,2.5)
        basic.grap(False)
        # basic.move_to_my_coords(grabParams.coords_place_clock2,80,0.5)
    else:
        basic.move_to_my_coords(grabParams.coords_place_apple,80,1.5)
        basic.grap(False)
        # basic.move_to_my_coords(grabParams.coords_place_apple2,80,0.5)



    # 返回准备位置 
    basic.move_to_my_angles(grabParams.angles_ready,60,0.5)
    move.moveforward(0.05, 1)
    move.moveforward(0.1, 1)
    basic.move_to_my_coords(grabParams.coords_ready,80,0)
    move.moveforward(0.2, 1.5)
    move.moveforward(0.05, 1)


    # # 调整姿态准备下一次任务

    # move.moveforward(0.05, 1)
    # move.moveforward(0.1, 1)
    # move.moveforward(0.2, 1.5)
    # move.moveforward(0.05, 1)
    # # basic.move_to_my_angles(grabParams.angles_ready,80,2)

 # # # 第三次
    # 移动到目标点
    time.sleep(0.5)
    # 超声波精确定位
    for _ in range(4):  
        distance = Sonor().get_sonor_data()
        print(distance)
        Sonor().sonor_control_goal_1()
    time.sleep(0.5)
    move.rotate_to_left(0.55,2.7)
    # move.moveforward(0.2,1)
    # 打开摄像头并搜索物体
    follow.open_camera()

    # 视觉搜索物体
    detect_result = follow.moving_search()

    # 执行抓取
    goal1_gab(detect_result)


    #调整前后距离
    move.moveback(0.05,1)
    for _ in range(5):  #8
        distance = Sonor().get_sonor_data()
        print(distance)
        # Sonor().sonor_control_goal_3()
        Sonor().sonor_control_goal_5()
    move.moveback(0.05,0.5)
    time.sleep(0.5)

    # 转身后退到放置位置
    move.rotate_to_right(0.53,2.7)    #.5############################右转还是有一点点大
    time.sleep(0.5)
    move.backward_trapezoidal(0.51, 0.4, 3)
    # move.moveback(0.05, 1)
    # move.moveback(0.1, 1)
    # move.moveback(0.2, 1)
    # move.moveback(0.15,0.3)
    # move.moveback(0.1, 0.7)
    # move.moveback(0.05, 0.8)
    # move.moveback(0.02, 0.6)

    # #sipplement with adjustment on June 6th
    # move.moveback(0.05,1)


    # 根据物体类型放置
    x, y, width, height, label = detect_result
    if label == "clock":##
        basic.move_to_my_coords(grabParams.coords_place_clock,80,2.5)
        basic.grap(False)
        # basic.move_to_my_coords(grabParams.coords_place_clock2,80,0.5)
    else:
        basic.move_to_my_coords(grabParams.coords_place_apple,80,1.5)
        basic.grap(False)
        # basic.move_to_my_coords(grabParams.coords_place_apple2,80,0.5)



    # 返回准备位置 
    basic.move_to_my_angles(grabParams.angles_ready,60,0.5)    
    move.moveforward(0.05, 1)
    move.moveforward(0.1, 1)
    basic.move_to_my_coords(grabParams.coords_ready,80,0)
    move.moveforward(0.2, 1.5)
    move.moveforward(0.05, 1)



# # # 第四次

    time.sleep(0.5)

    # 超声波精确定位
    for _ in range(4):  
        distance = Sonor().get_sonor_data()
        print(distance)
        Sonor().sonor_control_goal_1()
    time.sleep(0.5)
    move.rotate_to_left(0.55,2.7)
    # 打开摄像头并搜索物体
    follow.open_camera()

    # 视觉搜索物体
    detect_result = follow.moving_search()

    # 执行抓取
    goal1_gab(detect_result)

    # 调整前后距离
    move.moveback(0.05,1.2)
    for _ in range(8):  #8
        distance = Sonor().get_sonor_data()    
        print(distance)
        
        Sonor().sonor_control_goal_5()
    time.sleep(0.5)
    move.moveback(0.05,0.5)
    time.sleep(0.5)
    #转身后退到放置位置
    move.rotate_to_right(0.55,2.7)#.5
    time.sleep(0.5)
    move.backward_trapezoidal(0.51, 0.4, 3)
    # move.moveback(0.05, 1)
    # move.moveback(0.1, 1)
    # move.moveback(0.2, 1.5)
    # move.moveback(0.15,0.3)
    # move.moveback(0.1, 0.65)
    # move.moveback(0.05, 0.8)
    # move.moveback(0.02, 0.6)
    # time.sleep(0.5)
    # move.rotate_to_right(0.08,0.5)

    # 根据物体类型放置
    x, y, width, height, label = detect_result
    if label == "clock":##
        basic.move_to_my_coords(grabParams.coords_place_clock,80,2.5)
        basic.grap(False)
        # basic.move_to_my_coords(grabParams.coords_place_clock2,80,0.5)
    else:
        basic.move_to_my_coords(grabParams.coords_place_apple,80,1.5)
        basic.grap(False)
        # basic.move_to_my_coords(grabParams.coords_place_apple2,80,0.5)

    # 返回准备位置      
    basic.move_to_my_coords(grabParams.coords_ready,30,0)

    # 调整姿态
    #障碍物在右边
    move.moveforward(0.15, 1.2)
    #障碍物在左边
    move.moveforward(0.15, 1.6)
    # time.sleep(0.5)
    move.rotate_to_left(1, 4.3)


    # # 最终导航到目标点
    goal_3 = mobile_to_goal.read_goal("goal_3.txt")
    goal_number = 3
    print("坐标3_初始点接收完毕...")
    mobile_to_goal.send_goal(goal_number, goal_3)
    print("到达坐标3_初始点...")
    # reach_goal4()
    goal_4 = mobile_to_goal.read_goal("goal_4.txt")
    goal_number = 4
    print("坐标4_初始点接收完毕...")
    mobile_to_goal.send_goal(goal_number, goal_4)
    print("到达坐标4_初始点...")
    time.sleep(0.5)
    for _ in range(10):  
        distance = Sonor().get_sonor_data()
        print(distance)
        Sonor().sonor_control_goal_4()

    move.rotate_to_right(0.55,2.7)
    
    for _ in range(8):  #8
        distance = Sonor().get_sonor_data()    
        print(distance)
        
        Sonor().sonor_control_goal_3()
