#encoding: UTF-8
#!/usr/bin/env python2

from obj_detect import Detect_marker
from GrabParams import grabParams
import obj_detect, basic

import cv2, time, random
import sys
import logging

import argparse

# 设置日志配置
logging.basicConfig(filename='your_script.log', level=logging.DEBUG)

def main(data):
    logging.info("Executing script with data: {}".format(data))  # 修改后的代码

if __name__ == "__main__":
    if len(sys.argv) > 1:
        data = sys.argv[1]
        main(data)
    else:
        logging.error("No data provided")
        print("No data provided")
        sys.exit(1)

# def main(data):
#     logging.info("Executing script with data: {}".format(data))  # 修改后的代码
#     num = 0
#     cat_num = 0
#     bird_num = 0
#     # done = False
#     detect = Detect_marker()

#     basic.mc.power_on()
#     time.sleep(1)
#     basic.mc.set_color(0,0,255)
  
#     detect.init_mycobot()


# if __name__ == '__main__':
#     if len(sys.argv) > 1:
#         data = sys.argv[1]
#         main(data)
#     else:
#         logging.error("No data provided")
#         print("No data provided")
#         sys.exit(1)
#     # 





        # 对检测到的物体按 x 坐标排序，以保证先抓取 x 较小的物体
        # detections.sort(key=lambda item: item[0])
        # detections.sort(key=lambda item: item[1], reverse=True)


    #     if detections:
    #         for detection in detections:
    #             x, y, label = detection
    #             if label not in detected_labels:
    #                 detected_labels.add(label)
    #                 count_map[label] = 0  # 初始化计数器
    #             if len(detected_labels) == 2:  # 如果已经检测到两种不同类型的物体
    #                 break

    #         if len(detected_labels) == 2:
    #             target_labels = list(detected_labels)  # 转换为列表方便操作
    #             place_map = {target_labels[0]: positions[0], target_labels[1]: positions[1]}
    #             place_map1 = {target_labels[0]: positions[2], target_labels[1]: positions[3]}
                
    #          # 现在按照排序后的检测列表进行操作
    #             for detection in detections:
    #                 x, y, label = detection
    #                 if label in detected_labels and count_map[label] < 2:  # 确保每种类型的物体不超过两个
    #                     # 计算实际坐标
    #                     real_x, real_y = detect.get_position(x, y)
    #                     # 移动机械臂进行抓取
    #                     detect.grab_move(real_x + grabParams.x_bias, real_y + grabParams.y_bias)
    #                     # 确定放置位置
    #                     if count_map[label] < 1:
    #                         place_position = place_map[label]
    #                     else:
    #                         place_position = place_map1[label]
    #                     # 放置物体到对应位置
    #                     detect.place(place_position)
    #                     count_map[label] += 1
    #                     # 关闭摄像头等待下一个循环
    #                     cap.release()
    #                     time.sleep(1)
    #                     cap = cv2.VideoCapture(grabParams.cap_num)
    #                     time.sleep(0.5)
    #                 if count_map[target_labels[0]] == 2 and count_map[target_labels[1]] == 2:  # 如果已经处理了所有目标物体，退出循环
    #                     grabParams.done = True
    #                     break
    #             if not grabParams.done:
    #                 print("没有检测到所有指定类型的物体。")
    #     else:
    #         print("未检测到任何物体。")

    # cap.release()
    # cv2.destroyAllWindows()
    # basic.mc.set_color(0,255,0)

