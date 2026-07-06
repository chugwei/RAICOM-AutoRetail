#encoding: UTF-8
#!/usr/bin/env python2
from __future__ import print_function
from pymycobot import MyCobot
from pymycobot.genre import Angle
from obj_detect import Detect_marker
from GrabParams import grabParams
import obj_detect, basic
import os
import cv2
import time
import sys
import select  # 添加select模块用于超时检测

# 设置环境变量来抑制警告
os.environ['NO_AT_BRIDGE'] = '1'

def clear_input_buffer():
    """清除输入缓冲区中的所有残留数据"""
    import termios
    termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def get_user_placement_choice(label, default_side):
    """
    获取用户输入决定放置位置，带5秒超时功能
    :param label: 检测到的物体类别
    :param default_side: 程序默认建议的位置（1=左侧，2=右侧）
    :return: 用户选择的位置（0=放弃抓取，1=左侧，2=右侧）
    """
    # 清除输入缓冲区，避免之前的输入残留
    clear_input_buffer()
    
    # 显示提示信息
    print("\n" + "="*50)
    print("检测到物体: {}".format(label))
    print("程序默认建议: {}".format('左侧 (A/C)' if default_side == 1 else '右侧 (B/D)'))
    print("请选择放置位置 (5秒内无输入将使用默认建议):")
    print("0 - 放弃抓取，回到准备姿势")
    print("1 - 左侧 (A/C)")
    print("2 - 右侧 (B/D)")
    print("="*50)
    
    # 设置超时时间（5秒）
    timeout = 5
    start_time = time.time()
    user_choice = None
    
    # 获取用户输入（带超时）
    while time.time() - start_time < timeout:
        # 检查是否有输入可用
        if sys.stdin in select.select([sys.stdin], [], [], timeout - (time.time() - start_time))[0]:
            user_input = sys.stdin.readline().strip()
            try:
                choice = int(user_input)
                if choice in [0, 1, 2]:
                    user_choice = choice
                    break  # 收到有效输入，跳出循环
                else:
                    print("无效输入，请输入0、1或2")
            except ValueError:
                print("无效输入，请输入0、1或2")
    
    # 如果没有收到输入或输入无效，使用默认值
    if user_choice is None:
        print("\n" + "="*50)
        print("5秒内未接收到输入，将使用默认建议: {}".format('左侧 (A/C)' if default_side == 1 else '右侧 (B/D)'))
        print("="*50)
        user_choice = default_side
    
    # 清除输入缓冲区，避免这次输入影响下次
    clear_input_buffer()
    
    return user_choice

def wait_for_enter(cap):
    """
    等待用户按下回车键开始任务，同时显示实时画面
    """
    print("\n" + "="*50)
    print("机械臂已到达准备姿态，摄像头已就绪")
    print("请确认机械臂位置正确后按下回车键开始识别抓取")
    print("="*50)

    # 创建窗口
    cv2.namedWindow("Camera Preview", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Camera Preview", 640, 480)
    
    # 显示实时画面直到用户按下回车
    while True:
        ret, frame = cap.read()
        if not ret:
            print("摄像头读取错误，请检查摄像头连接")
            break
        
        # 显示画面
        cv2.imshow("Camera Preview", frame)
        
        # 检查按键输入
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # 回车键的ASCII码
            break
    
    # 关闭预览窗口
    cv2.destroyWindow("Camera Preview")
    print("开始识别抓取任务...")

def initialize_camera():
    """
    初始化摄像头并返回cap对象
    """
    cap = cv2.VideoCapture(grabParams.cap_num)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return None
    return cap

def release_camera(cap):
    """
    释放摄像头资源
    """
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # 初始化检测器和机械臂
    detect = Detect_marker()
    mc = MyCobot("/dev/arm", 115200)
    basic.mc.power_on()
    time.sleep(1)
    basic.mc.set_color(0, 0, 255)  # 设置LED为蓝色（运行中）
    detect.init_mycobot()  # 初始化机械臂位置
    
    # 任务参数设置
    attempts_left = 8  # 最大尝试次数（包含冗余）
    
    # 猫和鸟的抓取计数器（记录成功抓取的次数）
    cats_caught = 0
    birds_caught = 0
    
    # 位置映射：定义左侧和右侧位置
    # 左侧：猫放A，鸟放C
    LEFT_POSITIONS = {"cat": "A", "bird": "C"}
    # 右侧：猫放B，鸟放D
    RIGHT_POSITIONS = {"cat": "B", "bird": "D"}
    
    # 猫和鸟的放置历史（记录上一次成功放置的位置）
    cat_placement_history = []  # 记录猫的放置位置（1=左侧，2=右侧）
    bird_placement_history = []  # 记录鸟的放置位置（1=左侧，2=右侧）
    
    # 移动到准备位置
    time.sleep(0.5)
    basic.move_to_my_coords(grabParams.coords_ready_1, 80, 1) 
    time.sleep(0.5)
    basic.move_to_my_coords(grabParams.coords_ready, 80, 1)    

    # 初始化摄像头
    cap = initialize_camera()
    if cap is None:
        exit(1)
    
    # 等待用户确认并显示实时画面
    wait_for_enter(cap)
    
    # 用于定期重置检测历史
    frame_count = 0
    
    # 主循环：继续直到抓取完所有目标或达到最大尝试次数
    while (cats_caught < 2 or birds_caught < 2) and attempts_left > 0:
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
            print("Camera read error, retrying...")
            continue
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC键退出
            break

        # 进行物体检测（多帧确认）
        detection = detect.obj_detect(frame)
        
        if detection is None:
            print("No confirmed detection, continue...")
            continue
            
        # 解析检测结果
        x, y, label = detection
        print("Confirmed detection: {} at ({}, {})".format(label, x, y))
        
        # 计算物体在机械臂坐标系中的位置
        real_x, real_y = detect.get_position(x, y)

        # 根据检测到的类别执行抓取
        if label == "cat" or label == "bird":
            # 执行抓取动作
            if y > 320:
                detect.grab_move2(real_x + grabParams.x_near, real_y + grabParams.y_bias, grabParams.height_near)
                print("抓近处")
                print(grabParams.x_near, grabParams.height_near)
            else:
                detect.grab_move2(real_x + grabParams.x_far, real_y + grabParams.y_bias, grabParams.height_far)
                print("抓远处")
                print(grabParams.x_far, grabParams.height_far)
            # 抓取后返回准备位置
            basic.move_to_my_coords(grabParams.coords_ready_1, 60, 2)  
            basic.move_to_my_coords(grabParams.coords_ready, 80, 1)
            
            # 关闭摄像头（抓取后关闭）
            release_camera(cap)
            cap = None
            
            # 根据检测到的类别决定放置位置建议
            if label == "cat":
                # 计算程序默认建议的位置 (1=左侧，2=右侧)
                # 猫：交替放置（左-右-左-右）
                if len(cat_placement_history) == 0:
                    # 第一次放置猫，默认左侧
                    default_side = 1
                else:
                    # 获取上一次成功放置的位置
                    last_side = cat_placement_history[-1]
                    # 交替放置：上一次是左侧则这次右侧，上一次是右侧则这次左侧
                    default_side = 2 if last_side == 1 else 1
                
                # 获取用户放置选择（带5秒超时）
                user_choice = get_user_placement_choice("猫", default_side)
                
                if user_choice == 0:  # 用户选择放弃抓取
                    print("放弃抓取猫，回到准备姿势")
                    
                    # 松开夹子
                    basic.grap(False)
                    
                    print("Attempts left: {}".format(attempts_left))
                    # 重新打开摄像头
                    cap = initialize_camera()
                    if cap is None:
                        print("无法重新打开摄像头，退出程序")
                        break
                    continue
                    
                # 根据用户选择确定位置
                if user_choice == 1:
                    placement = LEFT_POSITIONS["cat"]  # A位置
                else:
                    placement = RIGHT_POSITIONS["cat"]  # B位置
                    
                # 执行放置
                detect.place(placement)
                time.sleep(0.5)
                mc.send_angle(Angle.J2.value, 20, 20)
                time.sleep(0.5)
                basic.move_to_my_coords(grabParams.coords_ready_1, 80, 2)  
                basic.move_to_my_coords(grabParams.coords_ready, 80, 1)
                
                # 更新猫计数器
                cats_caught += 1
                # 记录放置位置（仅当成功放置时）
                cat_placement_history.append(user_choice)
                print("Caught cat #{}, placed at {}".format(cats_caught, placement))
                
            elif label == "bird":
                # 计算程序默认建议的位置 (1=左侧，2=右侧)
                # 鸟：交替放置（左-右-左-右）
                if len(bird_placement_history) == 0:
                    # 第一次放置鸟，默认左侧
                    default_side = 1
                else:
                    # 获取上一次成功放置的位置
                    last_side = bird_placement_history[-1]
                    # 交替放置：上一次是左侧则这次右侧，上一次是右侧则这次左侧
                    default_side = 2 if last_side == 1 else 1
                
                # 获取用户放置选择（带5秒超时）
                user_choice = get_user_placement_choice("鸟", default_side)
                
                if user_choice == 0:  # 用户选择放弃抓取
                    print("放弃抓取鸟，回到准备姿势")
                    
                    # 松开夹子
                    basic.grap(False)
                    
                    # 减少尝试次数
                    attempts_left += 1
                    print("Attempts left: {}".format(attempts_left))
                    
                    # 重新打开摄像头
                    cap = initialize_camera()
                    if cap is None:
                        print("无法重新打开摄像头，退出程序")
                        break
                    continue
                    
                # 根据用户选择确定位置
                if user_choice == 1:
                    placement = LEFT_POSITIONS["bird"]  # C位置
                else:
                    placement = RIGHT_POSITIONS["bird"]  # D位置
                    
                # 执行放置
                detect.place(placement)
                time.sleep(0.5)
                mc.send_angle(Angle.J2.value, 20, 20)
                time.sleep(0.5)
                basic.move_to_my_coords(grabParams.coords_ready_1, 80, 2)  
                basic.move_to_my_coords(grabParams.coords_ready, 80, 1)
                
                # 更新鸟计数器
                birds_caught += 1
                # 记录放置位置（仅当成功放置时）
                bird_placement_history.append(user_choice)
                print("Caught bird #{}, placed at {}".format(birds_caught, placement))
            
            # 减少尝试次数
            attempts_left -= 1
            print("Attempts left: {}".format(attempts_left))
            
            # 重新打开摄像头（放置完成后）
            cap = initialize_camera()
            if cap is None:
                print("无法重新打开摄像头，退出程序")
                break
            
        else:
            print("Unhandled object: {}, skipping...".format(label))
            # 对于未处理的对象，减少尝试次数但不增加抓取计数
            attempts_left += 1
            continue
        
        # 如果所有目标都已抓取，提前结束
        if cats_caught >= 2 and birds_caught >= 2:
            print("All targets captured!")
            break
    
    # 任务完成后的清理工作
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()
    
    # 设置完成状态
    if cats_caught >= 2 and birds_caught >= 2:
        grabParams.done = True
        basic.mc.set_color(0, 255, 0)  # 设置LED为绿色（成功）
        print("Mission accomplished!")
    else:
        basic.mc.set_color(255, 0, 0)  # 设置LED为红色（失败")
        print("Mission incomplete. Cats caught: {}, Birds caught: {}".format(cats_caught, birds_caught))