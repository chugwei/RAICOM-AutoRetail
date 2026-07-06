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
img_size = 320
ratio2 = 640 / img_size
coords = grabParams.coords_ready
height_bias = grabParams.height_bias
# done = grabParams.done
CLASSES = ("cat", "banana", "clock", "apple", "bird")  # [0,1,2,3,4]

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
        frame, ratio, (dw, dh) = self.yolo.letterbox(frame, (img_size, img_size))
        return frame

    # 侦测物体
    def detect(self,img):
        x=y=width=height=0  # 如果变量在条件块（如 if 语句）中被赋值，请确保在所有可能的执行路径中都对其赋值 
        label = None     
        img_ori = img
        img_ori = self.transform_frame(img)
        img = self.transform_frame_128(img)
        #加载模型
        net = cv2.dnn.readNetFromONNX("/home/robuster/beetle_ai/scripts/best320s.onnx")         
        t1 = time.time()
        #输入数据处理
        blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (img_size, img_size), [0, 0, 0], swapRB=True, crop=False)
        net.setInput(blob)    
        #推理
        outputs = net.forward(net.getUnconnectedOutLayersNames())[0]    
        #获得识别结果
        boxes, classes, scores = self.yolo.yolov5_post_process_simple(outputs)
        t2 = time.time()

        # >>>>>>>>>> 从这里开始替换（删除旧代码，粘贴新代码） <<<<<<<<<<
        found_target = None
        if boxes is not None:
            # 遍历所有检测结果，寻找目标
            for i in range(len(boxes)):
                box = boxes[i] * ratio2
                cls_id = int(classes[i])
                score = scores[i]
                if score < 0.85:
                    continue
                if cls_id < len(CLASSES) and CLASSES[cls_id] in ("apple","clock"):
                    found_target = (box, CLASSES[cls_id], score)
                    break  # 取第一个匹配的目标

            if found_target:
                box, label, score_val = found_target
                left, top, right, bottom = map(int, box)
                x = int((left + right) / 2)
                y = int((top + bottom) / 2)
                width = right - left
                height = bottom - top

                # === 自定义绘图（避免 yolo.draw_single 的类别错误） ===
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
                # ======================================================

                # 打印坐标、宽度、高度和类型信息
                print("x:", x, "y:", y, "width:", width, "height:", height, "label:", label)
        # >>>>>>>>>> 替换结束 <<<<<<<<<<
        
        self.show_image(img_ori)
        # 打印推理时间
        print("time: " + str(t2 - t1) + "s")
        # 返回坐标、宽度、高度和类型信息
        if x + y > 0:
            return x, y, width, height, label
        else:
            return None

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
        

