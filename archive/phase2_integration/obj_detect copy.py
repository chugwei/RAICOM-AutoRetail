#encoding: UTF-8
#!/usr/bin/env python2

import basic
from GrabParams import grabParams

import cv2, time, argparse
from opencv_yolo import yolo
from pymycobot.mycobot import MyCobot

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument("--debug", type=bool, default="True")
# parser.add_argument("--debug", action="store_true")
args = parser.parse_args()

coords = grabParams.coords_ready
height_bias = grabParams.height_bias

CLASSES = ("apple", "clock", "banana","cat","bird") #[0,1,2,3,4]

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

    def init_mycobot(self):
        basic.mc.set_gripper_value(255,30)
        basic.move_to_my_coords(grabParams.coords_ready, 60, 2)        

    def show_image(self,img):
        if grabParams.debug and args.debug:
            cv2.imshow("figure", img)
            cv2.waitKey(50)

    def transform_frame(self,frame):
        frame, ratio, (dw, dh) = self.yolo.letterbox(frame, (grabParams.IMG_SIZE, grabParams.IMG_SIZE))
        return frame

    #图像处理，适配物体识别
    def transform_frame_128(self,frame):
        frame, ratio, (dw, dh) = self.yolo.letterbox(frame, (128, 128))
        return frame

    # 侦测物体
    def obj_detect(self,img):
        x=y=0
        detections = []  # 存储所有检测到的物体位置和识别类型     
        img_ori = img
        img_ori = self.transform_frame(img)
        img = self.transform_frame_128(img)
        #加载模型
        net = cv2.dnn.readNetFromONNX("/home/robuster/beetle_ai/scripts/best.onnx")        
        t1 = time.time()
        #输入数据处理
        blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (128, 128), [0, 0, 0], swapRB=True, crop=False)
        net.setInput(blob)    
        #推理
        outputs = net.forward(net.getUnconnectedOutLayersNames())[0]    
        # #获得识别结果
        # boxes, classes, scores = self.yolo.yolov5_post_process_simple(outputs)
        # t2 = time.time()
        # if boxes is not None:
        #     boxes = boxes * 5
        #     for i in range(len(boxes)):
        #         left, top, right, bottom = boxes[i]
        #         x = int((left + right) / 2)
        #         y = int((top + bottom) / 2)
        #         label = CLASSES[int(classes[i])]  # 获取物体的识别类型
        #         detections.append((x, y, label))  # 将物体的位置和识别类型添加到列表中, label
        #         # 在原始图像上框出物体并标注识别类型
        #         self.yolo.draw_single(img_ori, boxes[i], scores[i], classes[i])
        #获得识别结果
        boxes, classes, scores = self.yolo.yolov5_post_process_simple(outputs)
        t2 = time.time()

        # img_0 = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        if boxes is not None:
            boxes = boxes*5
            self.yolo.draw_single(img_ori, boxes[0], scores[0], classes[0])
            left, top, right, bottom = boxes[0]
            x = int((left+right)/2)
            y = int((top+bottom)/2)
            label = CLASSES[int(classes[0])]  # 获取物体的识别类型
            # detections.append((x, y, label))  # 将物体的位置和识别类型添加到列表中, label
        self.show_image(img_ori)
        # 打印推理时间
        print("time: " + str(t2 - t1) + "s")
        if x+y > 0:
            return x, y, label
        else:
            return None
        # return detections

    #  计算立方体和机器人之间的坐标
    def get_position(self,x, y):
            wx = wy = 0  # 如果变量在条件块（如 if 语句）中被赋值，请确保在所有可能的执行路径中都对其赋值
            if grabParams.grab_direct == "front":
                wx = (self.c_y - y) * self.ratio
                wy = (self.c_x - x) * self.ratio
            elif grabParams.grab_direct == "right":
                wx = (self.c_x - x) * self.ratio
                wy = (y - self.c_y) * self.ratio
            return wx, wy

    # 抓取动作，有两个全局变量 height_bias, done
    def grab_move(self, x, y):
        global height_bias
        
        coords_target = [coords[0]+int(x), coords[1]+int(y), height_bias, coords[3], coords[4], coords[5]]
        basic.move_to_my_coords(coords_target, 70, 2)   #30,2
        basic.grap(True)
        angles = [0, 0, 0, 0, 0, 0]
        basic.mc.send_angles(angles,30)
        time.sleep(1)
        # basic.mc.set_color(0,255,0) # 绿色抓取结束

    def place(self, position):
        if (position == "A"):
            basic.move_to_my_coords(grabParams.coords_ready, 70, 1)
            basic.move_to_my_coords(grabParams.coords_place_A, 80, 1)
            basic.grap(False)
            # basic.move_to_my_coords(grabParams.coords_ready, 40, 2)       

        elif(position == "B"):
            basic.move_to_my_coords(grabParams.coords_ready, 70, 1)
            basic.move_to_my_coords(grabParams.coords_place_B, 80, 1) 
            basic.grap(False)           
            # basic.move_to_my_coords(grabParams.coords_ready, 40, 2)

        elif(position == "C"):
            basic.move_to_my_coords(grabParams.coords_ready, 70, 1)
            basic.move_to_my_coords(grabParams.coords_place_C, 80, 1) 
            basic.grap(False)           
            # basic.move_to_my_coords(grabParams.coords_ready, 40, 2)
        
        elif(position == "D"):
            basic.move_to_my_coords(grabParams.coords_ready, 70, 1)
            basic.move_to_my_coords(grabParams.coords_place_D, 80, 1) 
            # basic.move_to_my_coords(grabParams.coords_ready, 20, 1.5)
            # basic.move_to_my_coords(grabParams.coords_place_D, 40, 2.5) 
            basic.grap(False)           
            # basic.move_to_my_coords(grabParams.coords_ready, 40, 2)
    
    def place_back(self, x, y):
        global height_bias
        
        coords_target = [coords[0]+int(x), coords[1]+int(y), height_bias, coords[3], coords[4], coords[5]]
        basic.move_to_my_coords(coords_target, 60, 1.5)       
        basic.grap(False)

