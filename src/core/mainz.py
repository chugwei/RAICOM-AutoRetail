#encoding: UTF-8
#!/usr/bin/env python2

import mobile_to_goal
from Basic import Rob_basic
from GrabParams import grabParams
from movement import Movement
from sonor import Sonor  # 导入Sonor类
from obj_detect import Detect_marker
from obj_follow import Follow_object
from pymycobot.mycobot import MyCobot

import time, rospy, cv2


def goal1_gab(obj_info):
    x, y, width, height, label = obj_info
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
    rospy.init_node('send_goals_python', anonymous=True)
    sonor = Sonor()  # 创建Sonor实例并命名为sonor
    
    try:
        # 初始化所有模块
        basic = Rob_basic()                                         #调用Basic的Rob_basic类
        move = Movement()                                           #调用movement的Movement类
        Detect = Detect_marker()                                    #调用obj_detect的Detect_marker类
        follow = Follow_object()                                    #调用obj_follow的Follow_object类

        move.forward_trapezoidal(1.27, 0.7, 2)

    ######第一次    
        #移动到目标点
        for _ in range(2):  #6
            distance = sonor.get_sonor_data()
            print(distance)
            sonor.sonor_control_goal_3()                   # 超声波精调
        time.sleep(1)
        move.right_trapezoidal(98.23, 0.8, 1.5)
        move.moveforward(0.05, 0.5)
        
        # 根据物体类型放置
        x, y, width, height, label = detect_result
        if label == "clock":##
            basic.move_to_my_coords(grabParams.coords_place_clock, 80, 2.5)
            basic.grap(False)
        else:
            basic.move_to_my_coords(grabParams.coords_place_apple, 80, 1.5)
            basic.grap(False)
            basic.move_to_my_coords(grabParams.coordsplace_apple2, 60, 0)

        time.sleep(1)

        # 返回准备位置 
        basic.move_to_my_angles(grabParams.angles_ready, 60, 0.5)
        move.forward_trapezoidal(0.53, 0.2, 1)   
        basic.move_to_my_coords(grabParams.coords_ready, 80, 0)



    # # # 第四次
        time.sleep(0.5)

        # 超声波精确定位
        for _ in range(2):  
            distance = sonor.get_sonor_data()
            print(distance)
            sonor.sonor_control_goal_1()
        time.sleep(0.5)
        move.left_trapezoidal(98.23, 0.8, 1.5)
        # 打开摄像头并搜索物体
        follow.open_camera()

        # 视觉搜索物体
        detect_result = follow.moving_search()

        # 执行抓取
        goal1_gab(detect_result)

        # 调整前后距离
        move.moveback(0.05, 1.2)
        for _ in range(2):  #8
            distance = sonor.get_sonor_data()    
            print(distance)
            sonor.sonor_control_goal_5()
        time.sleep(0.5)
        move.moveback(0.05, 0.5)
        time.sleep(0.5)
        #转身后退到放置位置
        move.right_trapezoidal(98.23, 0.8, 1.5)
        time.sleep(0.5)
        move.backward_trapezoidal(0.54, 0.4, 3)

        # 根据物体类型放置
        x, y, width, height, label = detect_result
        if label == "clock":##
            basic.move_to_my_coords(grabParams.coords_place_clock, 80, 2.5)
            basic.grap(False)

        else:
            basic.move_to_my_coords(grabParams.coords_place_apple, 80, 1.5)
            basic.grap(False)
            basic.move_to_my_coords(grabParams.coords_place_apple2, 60, 0)

        time.sleep(1)
        # 返回准备位置      
        basic.move_to_my_coords(grabParams.coords_ready, 30, 0)

        # 调整姿态
        #障碍物在右边
        move.moveforward(0.15, 1.2)
        move.left_trapezoidal(280, 0.8, 1)

        # # # 最终导航到目标点
        goal_4 = mobile_to_goal.read_goal("goal_4.txt")
        goal_number = 4
        print("坐标4_初始点接收完毕...")
        mobile_to_goal.send_goal(goal_number, goal_4)
        print("到达坐标4_初始点...")
        time.sleep(0.5)
        for _ in range(2):  
            distance = sonor.get_sonor_data()
            print(distance)
            sonor.sonor_control_goal_4()

        move.right_trapezoidal(102, 0.8, 1.5)
        time.sleep(0.5)
        # 最终超声波定位
        sonor.sonor_control_last()  # 使用实例调用
        
    finally:
        # 清理资源
        cv2.destroyAllWindows()
        if 'follow' in locals() and hasattr(follow, 'cap'):
            follow.cap.release()
        if 'Detect' in locals():
            Detect.mc.release_all_servos()
        rospy.loginfo("Program completed or terminated.")