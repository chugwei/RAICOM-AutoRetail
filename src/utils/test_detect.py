#encoding: UTF-8
#!/usr/bin/env python2

from Basic import Rob_basic
from GrabParams import grabParams
from obj_detect import Detect_marker
import cv2
import time
import signal
import sys

# 用于优雅退出
def signal_handler(sig, frame):
    print("\n接收到中断信号，正在退出...")
    sys.exit(0)

if __name__ == '__main__':
    # 注册 Ctrl+C 信号处理
    signal.signal(signal.SIGINT, signal_handler)
    
    # 初始化机械臂
    basic = Rob_basic()
    
    # 移动到准备角度（不移动底盘）
    print("移动机械臂到准备姿态...")
    basic.move_to_my_angles(grabParams.angles_ready, 80, 1.5)
    time.sleep(1.5)
    
    # 初始化检测器
    detect = Detect_marker()
    detect.init_mycobot()  # 确保夹爪打开等
    
    # 初始化摄像头
    cap = cv2.VideoCapture(grabParams.cap_num)
    if not cap.isOpened():
        print("错误: 无法打开摄像头")
        exit(1)
    
    print("开始持续原地识别（不移动、不抓取）...")
    print("按 Ctrl+C 退出程序\n")
    
    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("摄像头读取失败，重试...")
                time.sleep(0.5)
                continue
                
            # 执行识别
            result = detect.detect(frame)
            
            frame_count += 1
            print("=== 第 {} 帧 ===".format(frame_count))
            
            if result is not None:
                x, y, width, height, label = result
                print("检测到目标!")
                print("  类别: {}".format(label))
                print("  中心: ({}, {})".format(x, y))
                print("  尺寸: {} x {}".format(width, height))
            else:
                print("未检测到目标")
                
            print("------------------------")
            time.sleep(0.1)  # 控制帧率，避免刷屏过快
            
    except KeyboardInterrupt:
        pass
    finally:
        # 清理资源
        cap.release()
        cv2.destroyAllWindows()
        print("\n程序已退出。")