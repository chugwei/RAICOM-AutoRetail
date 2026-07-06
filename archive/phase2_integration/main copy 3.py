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
    detect = Detect_marker()
    mc = MyCobot("/dev/arm", 115200)
    basic.mc.power_on()
    time.sleep(1)
    basic.mc.set_color(0, 0, 255)
    detect.init_mycobot()
    num = 6
    cat_count = 0
    bird_count = 0
    positions = ["A", "B", "C", "D"]  # 定义四个放置位置
    time.sleep(0.5)
    basic.move_to_my_coords(grabParams.coords_ready_1, 80, 0) 
    time.sleep(0.5)
    basic.move_to_my_coords(grabParams.coords_ready, 80, 0)    
    cap = cv2.VideoCapture(grabParams.cap_num)
    
    # 用于定期重置检测历史
    frame_count = 0
    
    while cv2.waitKey(1) < 0 and not grabParams.done:
        frame_count += 1
        
        # 每10帧重置一次检测历史
        if frame_count % 10 == 0:
            detect.obj_detect(None, reset=True)
            frame_count = 0
        
        time.sleep(0.5)

        ret, frame = cap.read()
        if not ret:
            continue

        # 进行物体检测（多帧确认）
        detection = detect.obj_detect(frame)
        
        if detection is None:
            print("No confirmed detection, continue...")
            continue
            
        else:
            x, y, label = detection
            print("Confirmed detection: %s at (%d, %d)" % (label, x, y))
            
            real_x, real_y = detect.get_position(x, y)

            coords_now = basic.get_coords()

            # 根据label进行处理
            if label == "cat":
                # 移动机械臂进行抓取
                detect.grab_move(real_x + grabParams.x_bias, real_y + grabParams.y_bias)
                if cat_count % 2 == 0:
                    detect.place(positions[0])
                    time.sleep(0.5)
                    mc.send_angle(Angle.J2.value, 80, 60)
                    time.sleep(0.5)
                else:
                    detect.place(positions[1])
                    time.sleep(0.5)
                    mc.send_angle(Angle.J2.value, 80, 60)
                    time.sleep(0.5)
                cat_count -= 1
            elif label == "bird":
                # 移动机械臂进行抓取
                detect.grab_move(real_x + grabParams.x_bias, real_y + grabParams.y_bias)
                if bird_count % 2 == 0:
                    detect.place(positions[2])
                    time.sleep(0.5)
                    mc.send_angle(Angle.J2.value, 80, 60)
                    time.sleep(0.5)
                else:
                    detect.place(positions[3])
                    time.sleep(0.5)
                    mc.send_angle(Angle.J2.value, 80, 60)
                    time.sleep(0.5)
                bird_count -= 1
            else:
                print("Unhandled object: %s" % label)
                
            num -= 1
            print("num: %d" % num)

            cap.release()
            cv2.destroyAllWindows()
  
            basic.move_to_my_coords(grabParams.coords_ready_1, 60, 2)  

            detect.init_mycobot()
            cap = cv2.VideoCapture(grabParams.cap_num)
            
            # 如果已经成功检测和抓取4次，则结束循环
            if num <= 0:
                grabParams.done = True
                basic.mc.set_color(0, 255, 0)