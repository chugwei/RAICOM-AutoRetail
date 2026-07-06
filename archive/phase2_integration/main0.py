#encoding: UTF-8
#!/usr/bin/env python2

from obj_detect import Detect_marker
from GrabParams import grabParams
import obj_detect, basic

import cv2, time, random

if __name__ == '__main__':
    
    detect = Detect_marker()

    basic.mc.power_on()
    time.sleep(1)
    basic.mc.set_color(0,0,255)
    detect.init_mycobot()

    num = 0
    cat_count = 0
    bird_count = 0
    positions = ["A", "B", "C", "D"]  # 定义四个放置位置

    cap = cv2.VideoCapture(grabParams.cap_num)
    while cv2.waitKey(1) < 0 and not grabParams.done:
                
        
        time.sleep(0.5)

        ret, frame = cap.read()
        if not ret:
            continue

        time.sleep(2) #2s等待摄像头稳定
        detection = detect.obj_detect(frame)  # 获取所有检测到的物体位置和识别类型的列表
        if detection is None:           
            continue
        else:   
            x, y, label = detection
            # print(detection)      
            real_x, real_y = detect.get_position(x, y)

            coords_now = basic.get_coords()
            if len(coords_now) == 6:
                coords = coords_now

                #time.sleep(3)


            # 移动机械臂进行抓取
            detect.grab_move(real_x + grabParams.x_bias, real_y + grabParams.y_bias)
            # 根据label进行处理
            if label == "cat":
                if cat_count % 2 == 0:
                    detect.place(positions[0])
                else:
                    detect.place(positions[1])
                cat_count += 1
            elif label == "bird":
                if bird_count % 2 == 0:
                    detect.place(positions[2])
                else:
                    detect.place(positions[3])
                bird_count += 1
            else:

                detect.place_back(real_x, real_y)
            num += 1
            print("num: ", num)

            cap.release()
            cv2.destroyAllWindows()

            basic.move_to_my_coords(grabParams.coords_ready_1, 60, 2)   

            detect.init_mycobot()
            cap = cv2.VideoCapture(grabParams.cap_num)
            # 如果已经成功检测和抓取4次，则结束循环
            if num >= 6:
                grabParams.done = True
                basic.mc.set_color(0,255,0)



