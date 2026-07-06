#encoding: UTF-8
#!/usr/bin/env python2
from pymycobot import MyCobot
from pymycobot.genre import Angle
from obj_detect import Detect_marker
from GrabParams import grabParams
import obj_detect, basic
import os
import cv2
import time

# 设置环境变量来抑制警告
os.environ['NO_AT_BRIDGE'] = '1'

if __name__ == '__main__':
    # 初始化检测器和机械臂
    detect = Detect_marker()
    mc = MyCobot("/dev/arm", 115200)
    basic.mc.power_on()
    time.sleep(1)
    basic.mc.set_color(0, 0, 255)  # 设置LED为蓝色（运行中）
    detect.init_mycobot()  # 初始化机械臂位置
    
    # 任务参数设置
    attempts_left = 6  # 最大尝试次数（包含冗余）
    
    # 猫和鸟的抓取计数器（记录成功抓取的次数）
    cats_caught = 0
    birds_caught = 0
    
    # 位置映射：定义左侧和右侧位置
    # 左侧：猫放A，鸟放C
    LEFT_POSITIONS = {"cat": "A", "bird": "C"}
    # 右侧：猫放B，鸟放D
    RIGHT_POSITIONS = {"cat": "B", "bird": "D"}
    
    # 移动到准备位置
    time.sleep(0.5)
    basic.move_to_my_coords(grabParams.coords_ready_1, 80, 0.5) 
    time.sleep(0.5)
    basic.move_to_my_coords(grabParams.coords_ready, 80, 0.5)    
    
    # 初始化摄像头
    cap = cv2.VideoCapture(grabParams.cap_num)
    if not cap.isOpened():
        print ("Error: Could not open camera")
        exit(1)
    
    # 用于定期重置检测历史
    frame_count = 0
    
    # 主循环：继续直到抓取完所有目标或达到最大尝试次数
    while (cats_caught < 3 or birds_caught < 3) and attempts_left > 0:
        frame_count += 1
        
        # 每10帧重置一次检测历史
        if frame_count % 10 == 0:
            detect.obj_detect(None, reset=True)
            frame_count = 0
        
        # 降低循环速度，给机械臂和摄像头响应时间
        time.sleep(0.3)

        # 读取摄像头帧
        ret, frame = cap.read()
        if not ret:
            print ("Camera read error, retrying...")
            continue

        # 进行物体检测（多帧确认）
        detection = detect.obj_detect(frame)
        
        if detection is None:
            print ("No confirmed detection, continue...")
            continue
            
        # 解析检测结果
        x, y, label = detection
        print ("Confirmed detection: %s at (%d, %d)" % (label, x, y))
        
        # 计算物体在机械臂坐标系中的位置
        real_x, real_y = detect.get_position(x, y)

        # 根据检测到的类别决定放置位置
        if label == "cat":
            # 根据猫的抓取次数决定放置位置（交替放置）
            if cats_caught % 2 == 0:  # 第1、3只猫放左边
                placement = LEFT_POSITIONS["cat"]
            else:  # 第2、4只猫放右边
                placement = RIGHT_POSITIONS["cat"]
                
            # 执行抓取和放置
            if y > 320:
                detect.grab_move(real_x + grabParams.x_near, real_y + grabParams.y_bias, grabParams.height_near)
                print("抓近处")
                print(grabParams.x_near,grabParams.height_near)
            else:
                detect.grab_move(real_x + grabParams.x_far, real_y + grabParams.y_bias, grabParams.height_far)
                print("抓远处")
                print(grabParams.x_far,grabParams.height_far)
            detect.place(placement)
            time.sleep(0.5)
            mc.send_angle(Angle.J2.value, 80, 60)
            time.sleep(0.5)
            
            # 更新猫计数器
            cats_caught += 1
            print ("Caught cat #%d, placed at %s" % (cats_caught, placement))
            
        elif label == "bird":
            # 根据鸟的抓取次数决定放置位置（交替放置）
            if birds_caught % 2 == 0:  # 第1、3只鸟放左边
                placement = LEFT_POSITIONS["bird"]
            else:  # 第2、4只鸟放右边
                placement = RIGHT_POSITIONS["bird"]
                
            # 执行抓取和放置
                       # 执行抓取动作
            if y > 320:
                detect.grab_move(real_x + grabParams.x_near, real_y + grabParams.y_bias, grabParams.height_near)
                print("抓近处")
                print(grabParams.x_near,grabParams.height_near)
            else:
                detect.grab_move(real_x + grabParams.x_far, real_y + grabParams.y_bias, grabParams.height_far)
                print("抓远处")
                print(grabParams.x_far,grabParams.height_far)
            detect.place(placement)
            time.sleep(0.5)
            mc.send_angle(Angle.J2.value, 80, 60)
            time.sleep(0.5)
            
            # 更新鸟计数器
            birds_caught += 1
            print ("Caught bird #%d, placed at %s" % (birds_caught, placement))
            
        else:
            print ("Unhandled object: %s, skipping..." % label)
            # 对于未处理的对象，减少尝试次数但不增加抓取计数
            attempts_left += 1
        
        # 减少尝试次数
        attempts_left -= 1
        print ("Attempts left: %d" % attempts_left)
        
        # 抓取后返回准备位置
        cap.release()
        cv2.destroyAllWindows()
        basic.move_to_my_coords(grabParams.coords_ready_1, 80, 2)  
        basic.move_to_my_coords(grabParams.coords_ready, 80, 1)
        cap = cv2.VideoCapture(grabParams.cap_num)
        
        # 如果所有目标都已抓取，提前结束
        if cats_caught >= 2 and birds_caught >= 2:
            print ("All targets captured!")
            break
    
    # 任务完成后的清理工作

    
    
    # 设置完成状态
    if cats_caught >= 2 and birds_caught >= 2:
        grabParams.done = True
        basic.mc.set_color(0, 255, 0)  # 设置LED为绿色（成功）
        print ("Mission accomplished!")
    else:
        basic.mc.set_color(255, 0, 0)  # 设置LED为红色（失败）
        print ("Mission incomplete. Cats caught: %d, Birds caught: %d" % (cats_caught, birds_caught))