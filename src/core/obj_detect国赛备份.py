#encoding: UTF-8
#!/usr/bin/env python2

from Basic import Rob_basic
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
# done = grabParams.done
CLASSES = ("apple", "clock", "banana","cat ","bird ") #[0,1,2,3,4]

class Detect_marker(object):

    # 初始化检测参数
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
        Rob_basic().mc.set_gripper_value(255,30)
        Rob_basic().move_to_my_coords(grabParams.coords_ready, 80, 1.5)#45,2.5

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
    def detect(self, img):
        x = y = width = height = 0
        label = None
        img_ori = img
        img_ori = self.transform_frame(img)
        img = self.transform_frame_128(img)

        net = cv2.dnn.readNetFromONNX("/home/robuster/beetle_ai/scripts/beetle_obj.onnx")
        t1 = time.time()

        blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (128, 128), [0, 0, 0], swapRB=True, crop=False)
        net.setInput(blob)
        outputs = net.forward(net.getUnconnectedOutLayersNames())[0]

        boxes, classes, scores = self.yolo.yolov5_post_process_simple(outputs)
        t2 = time.time()

        if boxes is not None:
            boxes *= 5                     # 把 128 映射回 640
            # ========== 1. 过滤类别和置信度 ==========
            valid_idx = []
            for i, (cls, scr) in enumerate(zip(classes, scores)):
                if int(cls) < len(CLASSES) and CLASSES[int(cls)] in ("apple", "clock") and scr >= 0.70:
                    valid_idx.append(i)
            if not valid_idx:              # 没有符合要求的框
                self.show_image(img_ori)
                print("time: {:.3f}s".format(t2 - t1))
                return None

            # 只取第一个有效框（如果你想取最大的，可再排序）
            idx = valid_idx[0]
            box = boxes[idx]
            score = scores[idx]
            cls = classes[idx]

            # 画框（可选）
            self.yolo.draw_single(img_ori, box, score, cls)

            left, top, right, bottom = box
            x = int((left + right) / 2)
            y = int((top + bottom) / 2)
            width  = right - left
            height = bottom - top
            label  = CLASSES[int(cls)]
            print("x:", x, "y:", y, "width:", width, "height:", height,
                  "label:", label, "conf:", score)

        self.show_image(img_ori)
        print("time: {:.3f}s".format(t2 - t1))

        return (x, y, width, height, label) if x + y > 0 else None

    #  计算立方体和机器人之间的坐标
    def get_position(self,x, y):
            wx = wy = 0  # 如果变量在条件块（如 if 语句）中被赋值，请确保在所有可能的执行路径中都对其赋值
            if grabParams.grab_direct == "front":
                wx = (self.c_y - y) * self.ratio
                wy = (-(self.c_x - x)) * self.ratio
            elif grabParams.grab_direct == "right":
                wx = (self.c_x - x) * self.ratio
                wy = (y - self.c_y) * self.ratio
            return wx, wy

    # 抓取动作，有两个全局变量 height_bias, done
    def grab_move(self, x, y):
        # global height_bias, done
        coords_target = [coords[0]+int(x), coords[1]+int(y), height_bias, coords[3], coords[4], coords[5]]
        Rob_basic().move_to_my_coords(coords_target, 25,3)      
        Rob_basic().grap(True)
        coords_finish = grabParams.coords_finish
        Rob_basic().move_to_my_coords(coords_finish, 60, 1.5) 

        done = True
        print("Done")
        Rob_basic().mc.set_color(0,255,0) # 绿色抓取结束
        

