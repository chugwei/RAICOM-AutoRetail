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

if __name__ == '__main__':
    
    detect = Detect_marker()
    mc = MyCobot("/dev/arm", 115200)
    basic.mc.power_on()
    time.sleep(1)
    basic.mc.set_color(0,0,255)
    detect.init_mycobot()
    positions = ["A", "B", "C", "D"]  # 定义四个放置位置

    manual_arm_control()