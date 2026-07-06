#encoding: UTF-8
#!/usr/bin/env python2

import basic
from GrabParams import grabParams

import cv2, time, argparse
from opencv_yolo import yolo
from pymycobot.mycobot import MyCobot
import collections  # 替代from collections import Counter

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument("--debug", type=bool, default="True")
args = parser.parse_args()

coords = grabParams.coords_ready
height_far = grabParams.height_far
height_near = grabParams.height_near
##输入尺寸设置
img_size = 320
ratio2 = 640 / img_size
# CLASSES = ("apple", "clock", "banana", "cat", "bird")  # [0,1,2,3,4]
CLASSES = ("cat", "banana", "clock", "apple", "bird")  # [0,1,2,3,4]

class Detect_marker(object):

    def __init__(self):
        super(Detect_marker, self).__init__()
        self.yolo = yolo()
        # 参数，以计算摄像机削波参数
        self.x1 = self.x2 = self.y1 = self.y2 = 0
        # 用于计算立方体和机器人之间的坐标
        self.sum_x1 = self.sum_x2 = self.sum_y2 = self.sum_y1 = 0
        # 立方体相对于机器人的坐标
        self.c_x, self.c_y = grabParams.IMG_SIZE/2, grabParams.IMG_SIZE/2
        self.ratio = grabParams.ratio
        
        # 多帧确认变量
        self.detection_history = []  # 存储最近几帧的检测结果
        self.CONFIRM_FRAMES = 2      # 需要确认的帧数
        self.last_detection = None    # 存储最后一次检测结果

    def init_mycobot(self):
        basic.mc.set_gripper_value(255, 30)
        basic.move_to_my_coords(grabParams.coords_ready, 80, 0.8)        

    def show_image(self, img):
        if grabParams.debug and args.debug:
            cv2.imshow("figure", img)
            cv2.waitKey(50)

    def transform_frame(self, frame):
        frame, ratio, (dw, dh) = self.yolo.letterbox(frame, (grabParams.IMG_SIZE, grabParams.IMG_SIZE))
        return frame

    # 图像处理，适配物体识别
    def transform_frame_128(self, frame):
        # frame, ratio, (dw, dh) = self.yolo.letterbox(frame, (128, 128))
        frame, ratio, (dw, dh) = self.yolo.letterbox(frame, (img_size, img_size))
        return frame

    # 侦测物体（多帧确认版本）
    def obj_detect(self, img, reset=False):
        if reset:
            self.detection_history = []
            self.last_detection = None
            return None
            
        img_ori = img
        img_ori = self.transform_frame(img_ori)
        img = self.transform_frame_128(img)
        # 加载模型
        net = cv2.dnn.readNetFromONNX("/home/robuster/beetle_ai/scripts/best320.onnx")        
        t1 = time.time()
        # 输入数据处理
        # blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (128, 128), [0, 0, 0], swapRB=True, crop=False)
        blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (img_size, img_size), [0, 0, 0], swapRB=True, crop=False)
        net.setInput(blob)    
        # 推理
        outputs = net.forward(net.getUnconnectedOutLayersNames())[0]    
        # 获得识别结果
        boxes, classes, scores = self.yolo.yolov5_post_process_simple(outputs)
        t2 = time.time()

        detection = None
        found_target = None

        if boxes is not None:
            # 遍历所有检测结果
            for i in range(len(boxes)):
                box = boxes[i] * ratio2
                # box = boxes[i] * 2
                cls_id = int(classes[i])
                score = scores[i]
                label = CLASSES[cls_id]
                print("DEBUG: raw cls_id = {}, mapped label = {}".format(cls_id, label))
                if label in ("cat", "bird","apple","banana","clock"):
                    # 找到目标，取第一个（或最高分）
                    found_target = (box, label, score)
                    break  # 取第一个匹配的

            if found_target:
                box, label, score_val = found_target
                left, top, right, bottom = map(int, box)
                cv2.rectangle(img_ori, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(
                    img_ori,
                    "{} {:.2f}".format(label, score_val),
                    (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
                x = int((left + right) / 2)
                y = int((top + bottom) / 2)
                detection = (x, y, label)
                self.last_detection = (x, y, label)
            else:
                # 没有目标类别
                detection = None
                self.last_detection = None
        else:
            detection = None
            self.last_detection = None
        
        # if boxes is not None:
        #     boxes = boxes * 5
        #     self.yolo.draw_single(img_ori, boxes[0], scores[0], classes[0])
        #     left, top, right, bottom = boxes[0]
        #     x = int((left + right) / 2)
        #     y = int((top + bottom) / 2)
        #     label = CLASSES[int(classes[0])]
        #     detection = (x, y, label)
        #     self.last_detection = (x, y, label)  # 更新最后一次检测结果
        
        self.show_image(img_ori)
        print("time: " + str(t2 - t1) + "s")
        self.show_image(img_ori)
        print("time: " + str(t2 - t1) + "s")
        
        # === 新增：高置信度快速确认（单帧即可） ===
        if detection and found_target:
            _, _, score_val = found_target
            if score_val > 0.9:
                # 高置信度，立即返回，不清空历史（可选）
                self.detection_history = []  # 可选：清空避免干扰
                self.last_detection = detection
                return detection  # (x, y, label)
        # ======================================

        # 原有的多帧确认逻辑
        if detection:
            self.detection_history.append(detection)
            
            # 当积累到足够帧数时进行确认
            if len(self.detection_history) >= self.CONFIRM_FRAMES:
                # 获取最近两帧的标签
                last_labels = [d[2] for d in self.detection_history[-self.CONFIRM_FRAMES:]]
                
                # 检查最近两帧是否都是同一个标签
                if last_labels[0] == last_labels[1]:
                    # 两帧是同一个标签，使用最后一次检测到的坐标
                    last_x, last_y, final_label = self.last_detection
                    
                    # 清空历史记录
                    self.detection_history = []
                    
                    return last_x, last_y, final_label
                else:
                    # 两帧标签不一致，重置历史记录
                    print("Label inconsistency detected: %s vs %s" % (last_labels[0], last_labels[1]))
                    self.detection_history = []
                    self.last_detection = None
                    return None
        else:
            # 如果没有检测到物体，重置历史记录
            self.detection_history = []
            self.last_detection = None
        
        return None

    # 计算立方体和机器人之间的坐标
    def get_position(self, x, y):
        wx = wy = 0
        if grabParams.grab_direct == "front":
            wx = (self.c_y - y) * self.ratio
            wy = (self.c_x - x) * self.ratio
        elif grabParams.grab_direct == "right":
            wx = (self.c_x - x) * self.ratio
            wy = (y - self.c_y) * self.ratio
        return wx, wy

    # 抓取动作
    def grab_move(self, x, y ,h):
        coords_target = [coords[0] + int(x), coords[1] + int(y), h, 
                         coords[3], coords[4], coords[5]]
        # coords_target = [coords[0] + int(x), coords[1] + int(y), h, 
        #                 coords[3], coords[4], coords[5]]
        basic.move_to_my_coords(coords_target, 60, 1.3)
        # basic.move_to_target_z_offset (coords_target, 15,30, 3.5)
        basic.grap(True)
        angles = [0, 0, 0, 0, 0, 0]
        basic.mc.send_angles(angles, 70)
        time.sleep(0.5)

    def grab_move2(self, x, y ,h):
        coords_target = [coords[0] + int(x), coords[1] + int(y), h, 
                         coords[3], coords[4], coords[5]]
        # coords_target = [coords[0] + int(x), coords[1] + int(y), h, 
        #                 coords[3], coords[4], coords[5]]
        # basic.move_to_my_coords(coords_target, 30, 3.5)
        basic.move_to_target_z_offset(coords_target, 20 ,40, 2)
        basic.grap(True)
        angles = [0, 0, 0, 0, 0, 0]
        basic.mc.send_angles(angles, 70)
        time.sleep(0.5)

    def place(self, position):
        if position == "A":
            basic.move_to_my_coords(grabParams.coords_ready, 80, 1)
            basic.move_to_my_coords(grabParams.coords_place_A, 80, 1)
            basic.grap(False)
        elif position == "B":
            basic.move_to_my_coords(grabParams.coords_ready, 80, 1)
            basic.move_to_my_coords(grabParams.coords_place_B, 80, 1) 
            basic.grap(False)
        elif position == "C":
            basic.move_to_my_coords(grabParams.coords_ready, 80, 1)
            basic.move_to_my_coords(grabParams.coords_place_C, 80, 1) 
            basic.grap(False)
        elif position == "D":
            basic.move_to_my_coords(grabParams.coords_ready, 80, 1)
            basic.move_to_my_coords(grabParams.coords_place_D, 80, 1) 
            basic.grap(False)
    
    # def place_back(self, x, y):
    #     global height_bias
        
    #     coords_target = [coords[0] + int(x), coords[1] + int(y), height_bias, 
    #                      coords[3], coords[4], coords[5]]
    #     basic.move_to_my_coords(coords_target, 60, 1.5)       
    #     basic.grap(False)