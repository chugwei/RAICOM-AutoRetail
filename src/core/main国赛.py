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


# def goal1_gab(obj_info):
#     x, y, width, height, label = obj_info
#     if width > 165:
#         real_y = grabParams.y_near
#     elif 165 >=  width  >= 140:
#         real_y = grabParams.y_middle
#     else:
#         real_y = grabParams.y_far
#     print("------------")
#     print(real_y)
#     print("------------")
#     Detect_marker().grab_move(1.6, real_y)#

def goal1_gab(obj_info):
    x, y, width, height, label = obj_info
    
    # 从参数类获取配置
    MODE = grabParams.mapping_mode
    RANGE_MIN = grabParams.linear_range_low
    RANGE_MAX = grabParams.linear_range_high
    STEP_COUNT = grabParams.step_count
    
    # 打印初始参数状态
    print("------------")
    print("参数状态:")
    print("映射模式: " + str(["三段式", "线性映射", "阶梯映射"][MODE]))
    print("宽度区间: [%s, %s]" % (RANGE_MIN, RANGE_MAX))
    print("物体宽度: " + str(width))
    print("距离参数: y_far=%s, y_near=%s" % (grabParams.y_far, grabParams.y_near))
    
    # 确保范围有效
    if abs(RANGE_MAX - RANGE_MIN) < 1e-5:  # 防止除零
        print("错误: 线性范围无效! 最大值等于最小值.")
        real_y = grabParams.y_middle  # 使用中间值作为默认值
    else:
        if width < RANGE_MIN:
            print("宽度(%s) < 下限(%s)，使用最远距离: %s" % (width, RANGE_MIN, grabParams.y_far))
            real_y = grabParams.y_far
        elif width > RANGE_MAX:
            print("宽度(%s) > 上限(%s)，使用最近距离: %s" % (width, RANGE_MAX, grabParams.y_near))
            real_y = grabParams.y_near
        else:
            if MODE == 0:  # 原三段式
                # 计算中间边界
                mid_point = RANGE_MIN + (RANGE_MAX - RANGE_MIN) / 2.0
                if width > mid_point:
                    real_y = grabParams.y_near
                else:
                    real_y = grabParams.y_middle
                    
                print("三段式映射:")
                print("中间点: %.2f" % mid_point)
                print("选择距离: %s" % real_y)
                
            elif MODE == 1:  # 线性映射
                # 确保使用浮点运算
                range_diff = float(RANGE_MAX - RANGE_MIN)
                y_diff = float(grabParams.y_near - grabParams.y_far)
                k = y_diff / range_diff
                b = grabParams.y_far - k * RANGE_MIN
                real_y = k * width + b
                
                print("线性公式: y = %.4f * x + %.4f" % (k, b))
                print("计算值: y = %.4f * %s + %.4f = %.2f" % (k, width, b, real_y))
                
            else:  # MODE == 2 阶梯映射
                width_step = float(RANGE_MAX - RANGE_MIN) / STEP_COUNT
                step_index = min(STEP_COUNT - 1, int((width - RANGE_MIN) / width_step))
                y_step = float(grabParams.y_near - grabParams.y_far) / STEP_COUNT
                real_y = grabParams.y_far + y_step * step_index
                
                print("阶梯映射:")
                print("宽度步长: %.2f, 距离步长: %.2f" % (width_step, y_step))
                print("阶梯索引: %d (共%d阶)" % (step_index, STEP_COUNT))
                print("计算值: %.2f" % real_y)
    
    # 确保在安全范围内
    real_y = max(grabParams.y_far, min(grabParams.y_near, real_y))
    
    # 打印最终结果
    print("最终目标距离参数: " + str(real_y))
    print("------------")
    
    # 移动到目标位置
    Detect_marker().grab_move(1.6, real_y)



if __name__ == '__main__':
    # 初始化所有模块
    rospy.init_node('send_goals_python',anonymous=True)
    basic = Rob_basic()                                         #调用Basic的Rob_basic类
    move = Movement()                                           #调用movement的Movement类
    # sonor = Sonor()                                             #调用sonor的Sonor类
    Detect = Detect_marker()                                    #调用obj_detect的Detect_marker类
    follow = Follow_object()                                    #调用obj_follow的Follow_object类
    mc = MyCobot("/dev/arm", 115200)
    move.moveforward(0.05, 1)
    move.forward_trapezoidal(1.15,1.5,2)

######第一次    
    #移动到目标点
    # for _ in range(2):  #6
    #     distance = Sonor().get_sonor_data()
    #     print(distance)
    #     Sonor().sonor_control_goal_3()                      # 超声波精调
    time.sleep(1)
    move.right_trapezoidal(98.23, 0.8, 1.5)
    time.sleep(1)
    move.forward_trapezoidal(0.41,0.2,0.8)
    # move.moveforward(0.05,2)  # 补充
    # move.moveforward(0.2,1)                                 # 前进(0.1,2)
    # move.moveforward(0.05,2.2)  # 补充
    time.sleep(0.5)

    #调整前后距离
    for _ in range(2):  #10
        distance = Sonor().get_sonor_data()
        print(distance)
        Sonor().sonor_control_goal_1()                      # 二次精调
    time.sleep(1)
    basic.move_to_my_angles(grabParams.angles_ready,80,1.5)
    move.left_trapezoidal(98.0, 0.8, 1.5)
    time.sleep(1)

    move.backward_trapezoidal(0.05,0.06,1)

    # 机械臂初始化     
    Detect.init_mycobot()

    # 视觉搜索物体
    detect_result = follow.moving_search()
   
    #抓取物体
    goal1_gab(detect_result)
    

   #调整前后距离
    move.moveforward(0.05,1.5)
    for _ in range(2):  #8
        distance = Sonor().get_sonor_data()
        print(distance)
        Sonor().sonor_control_goal_5()
    move.moveback(0.05,0.5)
    time.sleep(0.5)
    

    # 转身后退到放置位置
    move.right_trapezoidal(98.8, 0.8, 1.5)
    time.sleep(1)

    #后退
    move.backward_trapezoidal(0.57, 0.6, 3)

    # 根据物体类型放置
    x, y, width, height, label = detect_result
    if label == "clock":##
        basic.move_to_my_coords(grabParams.coords_place_clock,80,2)
        basic.grap(False)
        time.sleep(0.5)
        mc.send_angle(Angle.J2.value, 20, 30)
    else:
        basic.move_to_my_coords(grabParams.coords_place_apple,80,1)
        basic.grap(False)
        time.sleep(0.5)
        mc.send_angle(Angle.J2.value, 20, 30)

    time.sleep(0.5)

    # 返回准备位置 
    basic.move_to_my_angles(grabParams.angles_ready,60,0.5)
    move.forward_trapezoidal(0.53,0.2,1)   
    basic.move_to_my_coords(grabParams.coords_ready,80,0)

    

# # # # 第二次
    # 移动到目标点

    time.sleep(0.5)

    # 超声波精确定位
    for _ in range(2):  
        distance = Sonor().get_sonor_data()
        print(distance)
        Sonor().sonor_control_goal_1()
    time.sleep(1)
    move.left_trapezoidal(98.0, 0.8, 1.5)

    time.sleep(1)
    move.backward_trapezoidal(0.06,0.06,0.5)
    # # 超声波精确定位（8次调整）
    # for _ in range(2):  
    #     distance = Sonor().get_sonor_data()
    #     print(distance)
    #     Sonor().sonor_control_goal_6()   
    # time.sleep(0.5)

    # move.backward_trapezoidal(0.05,0.15,1.5)
    # move.moveforward(0.2,0.8)
    # 重新打开摄像头
    follow.open_camera()

    # 视觉搜索物体
    detect_result = follow.moving_search()

    # 执行抓取
    goal1_gab(detect_result)

    #调整前后距离
    move.moveforward(0.05, 1)
    time.sleep(1)
    for _ in range(2):  #8
        distance = Sonor().get_sonor_data()
        print(distance)
        Sonor().sonor_control_goal_5()
    time.sleep(0.5)
    move.backward_trapezoidal(0.1, 0.4, 3)
    # move.moveback(0.05,0.5)

    # 转身后退到放置位置
    move.right_trapezoidal(98.23, 0.8, 1.5)
    time.sleep(1)

    move.backward_trapezoidal(0.55, 0.6, 3)

    # 根据物体类型放置
    x, y, width, height, label = detect_result
    if label == "clock":##
        basic.move_to_my_coords(grabParams.coords_place_clock,80,2)
        basic.grap(False)
        time.sleep(0.5)
        mc.send_angle(Angle.J2.value, 20, 30)
    else:
        basic.move_to_my_coords(grabParams.coords_place_apple,80,1)
        basic.grap(False)
        time.sleep(0.5)
        mc.send_angle(Angle.J2.value, 20, 30)

    time.sleep(0.5)

    # 返回准备位置 
    basic.move_to_my_angles(grabParams.angles_ready,60,0.5)
    move.forward_trapezoidal(0.53,0.2,1)   
    basic.move_to_my_coords(grabParams.coords_ready,80,0)



 # # # 第三次
    # 移动到目标点
    time.sleep(0.5)
    # 超声波精确定位
    for _ in range(2):  
        distance = Sonor().get_sonor_data()
        print(distance)
        Sonor().sonor_control_goal_1()
    time.sleep(0.5)
    move.left_trapezoidal(98.0 ,0.8, 1.5)
    time.sleep(1)


    # for _ in range(2):  
    #     distance = Sonor().get_sonor_data()
    #     print(distance)
    #     Sonor().sonor_control_goal_6()

    # 打开摄像头并搜索物体
    follow.open_camera()

    # 视觉搜索物体
    detect_result = follow.moving_search()

    # 执行抓取
    goal1_gab(detect_result)


    #调整前后距离
    time.sleep(0.5)
    for _ in range(2):  #8
        distance = Sonor().get_sonor_data()
        print(distance)
        # Sonor().sonor_control_goal_3()
        Sonor().sonor_control_goal_5()
    move.backward_trapezoidal(0.15,0.08,0.5)
    # move.moveback(0.05,0.5)
    time.sleep(0.5)

    # 转身后退到放置位置
    move.right_trapezoidal(99, 0.8, 1.5)
    time.sleep(1)
    move.backward_trapezoidal(0.55, 0.6, 3)


    # 根据物体类型放置
    x, y, width, height, label = detect_result
    if label == "clock":##
        basic.move_to_my_coords(grabParams.coords_place_clock,80,2)
        basic.grap(False)
        time.sleep(0.5)
        mc.send_angle(Angle.J2.value, 20, 30)
    else:
        basic.move_to_my_coords(grabParams.coords_place_apple,80,1)
        basic.grap(False)
        time.sleep(0.5)
        mc.send_angle(Angle.J2.value, 20, 30)

    time.sleep(0.5)

    # 返回准备位置 
    basic.move_to_my_angles(grabParams.angles_ready,60,1.5)
    move.forward_trapezoidal(0.53,0.2,1)   
    basic.move_to_my_coords(grabParams.coords_ready,80,0)



# # # 第四次

    time.sleep(0.5)

    # 超声波精确定位
    for _ in range(2):  
        distance = Sonor().get_sonor_data()
        print(distance)
        Sonor().sonor_control_goal_1()
    time.sleep(0.5)
    move.left_trapezoidal(98, 0.8, 1.5)
    move.forward_trapezoidal(0.3,0.05,0.5)
    # move.rotate_to_left(0.55,2.7)
    # 打开摄像头并搜索物体
    follow.open_camera()

    # 视觉搜索物体
    detect_result = follow.moving_search()

    # 执行抓取
    goal1_gab(detect_result)

    # 调整前后距离
    move.moveback(0.05,1.2)
    time.sleep(0.8)
    for _ in range(2):  #8
        distance = Sonor().get_sonor_data()    
        print(distance)
        
        Sonor().sonor_control_goal_5()
    time.sleep(0.5)
    move.backward_trapezoidal(0.12,0.08,0.5)
    time.sleep(0.5)
    #转身后退到放置位置
    move.right_trapezoidal(99, 0.8, 1.5)
    # move.rotate_to_right(0.55,2.7)#.5
    time.sleep(1)
    move.backward_trapezoidal(0.54, 0.6, 3)

    # 根据物体类型放置
    x, y, width, height, label = detect_result
    if label == "clock":##
        basic.move_to_my_coords(grabParams.coords_place_clock,80,2)
        basic.grap(False)
        time.sleep(0.5)
        mc.send_angle(Angle.J2.value, 20, 30)
    else:
        basic.move_to_my_coords(grabParams.coords_place_apple,80,1)
        basic.grap(False)
        time.sleep(0.5)
        mc.send_angle(Angle.J2.value, 20, 30)

    time.sleep(0.5)
    # 返回准备位置      
    basic.move_to_my_coords(grabParams.coords_ready,30,0)

    # 调整姿态
    #障碍物在右边
    move.moveforward(0.15, 1.2)
    #障碍物在左边
    # move.moveforward(0.15, 1.6)
    # time.sleep(0.5)
    move.right_trapezoidal(98.8, 0.8, 1.5)
    # move.left_trapezoidal(100,1,1.5)        #check



    # # # 最终导航到目标点
    # goal_3 = mobile_to_goal.read_goal("goal_3.txt")
    # goal_number = 3
    # print("坐标3_初始点接收完毕...")
    # mobile_to_goal.send_goal(goal_number, goal_3)
    # print("到达坐标3_初始点...")
  
    for _ in range(4):
        goal_6 = mobile_to_goal.read_goal("goal_6.txt")
        goal_number = 6
        print("坐标6_初始点接收完毕...")
        mobile_to_goal.send_goal(goal_number, goal_6)
        print("到达坐标6_初始点...")
        time.sleep(0.5)
        for _ in range(2):  
            distance = Sonor().get_sonor_data()
            print(distance)
            Sonor().sonor_control_goal_4()
        time.sleep(0.8)
        move.left_trapezoidal(98.23, 0.8, 1.5)


        goal_4 = mobile_to_goal.read_goal("goal_4.txt")
        goal_number = 4
        print("坐标4_初始点接收完毕...")
        mobile_to_goal.send_goal(goal_number, goal_4)
        print("到达坐标4_初始点...")
        time.sleep(0.5)
        for _ in range(8):  
            distance = Sonor().get_sonor_data()
            print(distance)
            Sonor().sonor_control_goal_4()
        time.sleep(12)

    # move.right_trapezoidal(102, 0.8, 1.5)
    # time.sleep(0.5)
    # move.forward_trapezoidal(0.42,0.15,1)
    # sonor.sonor_control_last()

    # for _ in range(2):  #8
    #     distance = Sonor().get_sonor_data()    
    #     print(distance)
        
    #     Sonor().sonor_control_goal_3()