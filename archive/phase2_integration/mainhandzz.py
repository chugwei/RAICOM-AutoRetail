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
import fcntl
import errno

# 设置环境变量来抑制警告
os.environ['NO_AT_BRIDGE'] = '1'

def clear_input_buffer():
    """清除输入缓冲区中的所有残留数据"""
    try:
        # 针对Linux系统
        fd = sys.stdin.fileno()
        old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        # 设置文件描述符为非阻塞
        fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
        try:
            # 循环读取直到没有数据
            while True:
                try:
                    # 尝试读取1024字节
                    data = os.read(fd, 1024)
                    if not data:
                        break
                except OSError as e:
                    if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                        # 没有数据了
                        break
                    else:
                        # 其他错误，抛出
                        raise
        finally:
            # 恢复文件描述符的状态
            fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)
    except Exception as e:
        # 发生异常，忽略
        print("清空输入缓冲区时发生异常: {}".format(e))

def get_user_placement_choice(label, default_side, disable_timeout=False):
    """
    获取用户输入决定放置位置，带超时功能（可禁用）
    :param label: 检测到的物体类别
    :param default_side: 程序默认建议的位置（1=左侧，2=右侧）
    :param disable_timeout: 是否禁用超时（禁用时无限等待）
    :return: 用户选择的位置（0=放弃抓取，1=左侧，2=右侧）
    """
    # 清除输入缓冲区，避免之前的输入残留
    clear_input_buffer()
    
    # 显示提示信息
    print("\n" + "="*50)
    print("检测到物体: {}".format(label))
    print("程序默认建议: {}".format('左侧 (A/C)' if default_side == 1 else '右侧 (B/D)'))
    print("请选择放置位置{}:".format("" if disable_timeout else " (5秒内无输入将使用默认建议)"))
    print("0 - 放弃抓取，回到准备姿势")
    print("1 - 左侧 (A/C)")
    print("2 - 右侧 (B/D)")
    print("="*50)
    
    # 禁用超时的处理
    if disable_timeout:
        while True:
            try:
                # 获取输入前先清空缓冲区
                clear_input_buffer()
                choice = int(raw_input("请输入选择 (0/1/2): "))
                if choice in [0, 1, 2]:
                    return choice
                else:
                    print("无效输入，请输入0、1或2")
            except ValueError:
                print("无效输入，请输入0、1或2")
    
    # 设置超时时间（5秒）
    timeout = 5
    start_time = time.time()
    user_choice = None
    
    # 获取用户输入（带超时）
    while time.time() - start_time < timeout:
        # 检查是否有输入可用
        if sys.stdin in select.select([sys.stdin], [], [], timeout - (time.time() - start_time))[0]:
            try:
                user_input = sys.stdin.readline().strip()
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
    # 左侧：猫放A，鸟放C，其他物体放A
    LEFT_POSITIONS = {"cat": "A", "bird": "C", "unknown": "A"}
    # 右侧：猫放B，鸟放D，其他物体放B
    RIGHT_POSITIONS = {"cat": "B", "bird": "D", "unknown": "B"}
    
    # 猫和鸟的放置历史（记录上一次成功放置的位置）
    cat_placement_history = []  # 记录猫的放置位置（1=左侧，2=右侧）
    bird_placement_history = []  # 记录鸟的放置位置（1=左侧，2=右侧）
    
    # 手动模式标志（一旦出现非猫鸟物体抓取，后续都使用手动模式）
    manual_mode = False
    
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

        # 执行抓取动作
        if y > 320:
            detect.grab_move(real_x + grabParams.x_near, real_y + grabParams.y_bias, grabParams.height_near)
            print("抓近处")
            print(grabParams.x_near, grabParams.height_near)
        else:
            detect.grab_move(real_x + grabParams.x_far, real_y + grabParams.y_bias, grabParams.height_far)
            print("抓远处")
            print(grabParams.x_far, grabParams.height_far)
    
        # 抓取后返回准备位置
        basic.move_to_my_coords(grabParams.coords_ready_1, 60, 2)  
        basic.move_to_my_coords(grabParams.coords_ready, 80, 1)
        
        # 关闭摄像头（抓取后关闭）
        release_camera(cap)
        cap = None
        
        # 确定物体类别标签
        if label == "cat":
            display_label = "猫"
            obj_type = "cat"
        elif label == "bird":
            display_label = "鸟"
            obj_type = "bird"
        else:
            display_label = "未知物体"
            obj_type = "unknown"
            # 进入手动模式
            manual_mode = True
            print("已进入手动模式，后续操作需要用户确认")
        
        # 计算放置位置建议
        if obj_type == "cat" or obj_type == "unknown":
            # 对于猫或未知物体，使用猫的放置策略
            if len(cat_placement_history) == 0:
                # 第一次放置，默认左侧
                default_side = 1
            else:
                # 获取上一次成功放置的位置
                last_side = cat_placement_history[-1]
                # 交替放置：上一次是左侧则这次右侧，上一次是右侧则这次左侧
                default_side = 2 if last_side == 1 else 1
        else:  # 鸟
            if len(bird_placement_history) == 0:
                # 第一次放置鸟，默认左侧
                default_side = 1
            else:
                # 获取上一次成功放置的位置
                last_side = bird_placement_history[-1]
                # 交替放置：上一次是左侧则这次右侧，上一次是右侧则这次左侧
                default_side = 2 if last_side == 1 else 1
        
        # 获取用户放置选择（手动模式下禁用超时）
        user_choice = get_user_placement_choice(display_label, default_side, disable_timeout=manual_mode)
        
        if user_choice == 0:  # 用户选择放弃抓取
            print("放弃抓取{}，回到准备姿势".format(display_label))
            
            # 松开夹子
            basic.grap(False)
            
            # 减少尝试次数
            attempts_left += 1
            print("剩余尝试次数: {}".format(attempts_left))
            
            # 重新打开摄像头
            cap = initialize_camera()
            if cap is None:
                print("无法重新打开摄像头，退出程序")
                break
            continue
            
        # 根据用户选择确定位置
        if user_choice == 1:
            placement = LEFT_POSITIONS[obj_type]
        else:
            placement = RIGHT_POSITIONS[obj_type]
            
        # 执行放置
        detect.place(placement)
        time.sleep(0.5)
        mc.send_angle(Angle.J2.value, 20, 20)
        time.sleep(0.5)
        basic.move_to_my_coords(grabParams.coords_ready_1, 80, 2)  
        basic.move_to_my_coords(grabParams.coords_ready, 80, 1)
        
        # 更新计数器（只记录猫和鸟）
        if obj_type == "cat":
            cats_caught += 1
            # 记录放置位置
            cat_placement_history.append(user_choice)
            print("抓到猫 #{}, 放在位置 {}".format(cats_caught, placement))
        elif obj_type == "bird":
            birds_caught += 1
            # 记录放置位置
            bird_placement_history.append(user_choice)
            print("抓到鸟 #{}, 放在位置 {}".format(birds_caught, placement))
        else:
            print("放置了未知物体到位置 {}".format(placement))
        
        # 减少尝试次数
        attempts_left -= 1
        print("剩余尝试次数: {}".format(attempts_left))
        
        # 重新打开摄像头（放置完成后）
        cap = initialize_camera()
        if cap is None:
            print("无法重新打开摄像头，退出程序")
            break
        
        # 如果所有目标都已抓取，提前结束
        if cats_caught >= 2 and birds_caught >= 2:
            print("所有目标已完成抓取!")
            break
    
    # 任务完成后的清理工作
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()
    
    # 设置完成状态
    if cats_caught >= 2 and birds_caught >= 2:
        grabParams.done = True
        basic.mc.set_color(0, 255, 0)  # 设置LED为绿色（成功）
        print("任务完成!")
    else:
        basic.mc.set_color(255, 0, 0)  # 设置LED为红色（失败")
        print("任务未完成. 猫抓取: {}, 鸟抓取: {}".format(cats_caught, birds_caught))

# 新增调试交互功能
def start_debug_interaction():
    """
    启动调试交互界面
    """
    print("="*50)
    print("进入调试模式")
    print("1 - 手动控制机械臂移动")
    print("2 - 相机检测测试")
    print("3 - 抓取测试")
    print("4 - 放置测试")
    print("5 - 退出调试模式")
    print("="*50)
    
    choice = int(raw_input("请选择调试功能: "))
    
    if choice == 1:
        manual_arm_control()
    elif choice == 2:
        camera_test()
    elif choice == 3:
        grab_test()
    elif choice == 4:
        place_test()
    elif choice == 5:
        print("退出调试模式")
        return
    
    # 递归调用，直到用户选择退出
    start_debug_interaction()

def manual_arm_control():
    """
    手动控制机械臂移动
    """
    print("="*50)
    print("手动控制机械臂移动")
    print("可用指令：")
    print("x <值> - 调整X坐标")
    print("y <值> - 调整Y坐标")
    print("z <值> - 调整Z坐标")
    print("rx <值> - 调整RX角度")
    print("ry <值> - 调整RY角度")
    print("rz <值> - 调整RZ角度")
    print("g - 抓取")
    print("r - 释放")
    print("a - 查看当前角度")
    print("c - 查看当前坐标")
    print("s - 保存当前位置到参数")
    print("b - 返回调试主菜单")
    print("="*50)
    
    # 获取当前位置
    current_coords = basic.mc.get_coords()
    
    while True:
        cmd = raw_input("输入指令: ").split()
        if not cmd:
            continue
            
        action = cmd[0].lower()
        
        if action == 'x' and len(cmd) == 2:
            try:
                new_value = float(cmd[1])
                current_coords[0] = new_value
                basic.move_to_my_coords(current_coords, 30, 0)
                print("X坐标已设置为 {}".format(new_value))
            except ValueError:
                print("无效输入")
                
        elif action == 'y' and len(cmd) == 2:
            try:
                new_value = float(cmd[1])
                current_coords[1] = new_value
                basic.move_to_my_coords(current_coords, 30, 0)
                print("Y坐标已设置为 {}".format(new_value))
            except ValueError:
                print("无效输入")
                
        elif action == 'z' and len(cmd) == 2:
            try:
                new_value = float(cmd[1])
                current_coords[2] = new_value
                basic.move_to_my_coords(current_coords, 30, 0)
                print("Z坐标已设置为 {}".format(new_value))
            except ValueError:
                print("无效输入")
                
        elif action == 'rx' and len(cmd) == 2:
            try:
                new_value = float(cmd[1])
                current_coords[3] = new_value
                basic.move_to_my_coords(current_coords, 30, 0)
                print("RX角度已设置为 {}".format(new_value))
            except ValueError:
                print("无效输入")
                
        elif action == 'ry' and len(cmd) == 2:
            try:
                new_value = float(cmd[1])
                current_coords[4] = new_value
                basic.move_to_my_coords(current_coords, 30, 0)
                print("RY角度已设置为 {}".format(new_value))
            except ValueError:
                print("无效输入")
                
        elif action == 'rz' and len(cmd) == 2:
            try:
                new_value = float(cmd[1])
                current_coords[5] = new_value
                basic.move_to_my_coords(current_coords, 30, 0)
                print("RZ角度已设置为 {}".format(new_value))
            except ValueError:
                print("无效输入")
                
        elif action == 'g':
            basic.grap(True)
            print("执行抓取动作")
            
        elif action == 'r':
            basic.grap(False)
            print("执行释放动作")
            
        elif action == 'a':
            angles = basic.mc.get_angles()
            print("当前关节角度: {}".format(angles))
            
        elif action == 'c':
            print("当前坐标: {}".format(current_coords))
            
        elif action == 's':
            param_name = raw_input("请输入保存位置参数名称: ")
            if hasattr(grabParams, param_name):
                setattr(grabParams, param_name, current_coords[:])
                print("已保存当前位置到 {}".format(param_name))
            else:
                print("参数 {} 不存在".format(param_name))
                
        elif action == 'b':
            break
            
    # 返回调试菜单
    start_debug_interaction()

# 其他调试函数
def camera_test():
    """相机测试功能"""
    cap = initialize_camera()
    if not cap:
        return
        
    print("相机测试 - 按ESC退出")
    cv2.namedWindow("Camera Test", cv2.WINDOW_NORMAL)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        cv2.imshow("Camera Test", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break
            
    cv2.destroyAllWindows()
    cap.release()
    
def grab_test():
    """抓取测试功能"""
    print("执行抓取测试...")
    # 移动到抓取位置
    basic.move_to_my_coords(grabParams.coords_above_grab, 50, 1)
    basic.move_to_my_coords(grabParams.coords_grab, 20, 1)
    # 执行抓取
    basic.grap(True)
    # 抬起
    basic.move_to_my_coords(grabParams.coords_above_grab, 50, 1)
    # 返回准备位置
    basic.move_to_my_coords(grabParams.coords_ready, 50, 1)
    
def place_test():
    """放置测试功能"""
    target = raw_input("输入放置位置 (A/B/C/D): ").upper()
    if target not in ['A', 'B', 'C', 'D']:
        print("无效位置")
        return
        
    print("执行放置测试到位置 {}".format(target))
    detect = Detect_marker()
    detect.place(target)