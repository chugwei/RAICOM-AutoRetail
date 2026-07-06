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
    time.sleep(0.5)
    basic.mc.set_color(0, 0, 255)  # 设置LED为蓝色（运行中）
    detect.init_mycobot()  # 初始化机械臂位置
    time.sleep(1.5)
    # basic.move_to_my_coords([229.3, 21.9, 185, 175.35, -7.37, -123.24], 60, 1.5)  
    # basic.move_to_my_coords(grabParams.coords_ready, 60, 1)
    
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
    # time.sleep(0.5)
    # basic.move_to_my_coords(grabParams.coords_ready_1, 80, 0.5)   #先回到star
    # time.sleep(0.5)
    # basic.move_to_my_coords(grabParams.coords_ready, 80, 0.5)    
    
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
        time.sleep(0.5)

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

