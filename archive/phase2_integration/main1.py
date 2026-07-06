#encoding: UTF-8
#!/usr/bin/env python2

from obj_detect import Detect_marker
from GrabParams import grabParams
import obj_detect, basic
import cv2
import time

class OptimizedGrabSystem:
    def __init__(self):
        self.detect = Detect_marker()
        self.num = 0
        self.cat_count = 0
        self.bird_count = 0
        self.positions = ["A", "B", "C", "D"]
        self.grabbed_objects = []
        self.detection_history = []
        self.DETECTION_HISTORY_SIZE = 3
        self.MAX_RETRIES = 3
        self.last_coords = None

    def init_camera(self):
        """初始化摄像头并设置分辨率"""
        self.cap = cv2.VideoCapture(grabParams.cap_num)
        # 设置摄像头分辨率 
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not self.cap.isOpened():
            raise ValueError("无法打开摄像头")

    # 注释掉抓取后验证功能（因摄像头视角问题无法观测放置区域）
    # def verify_grab(self, x, y):
    #     """抓取后验证（视觉确认）"""
    #     time.sleep(1)
    #     ret_grab, frame_grab = self.cap.read()
    #     if not ret_grab:
    #         print("抓取后验证失败")
    #         return False
    #         
    #     post_detection = self.detect.obj_detect(frame_grab)
    #     if post_detection:
    #         post_x, post_y, _ = post_detection
    #         distance = ((x - post_x)**2 + (y - post_y)**2)**0.5
    #         if distance < 15:  # 坐标未明显变化说明抓取失败 
    #             print("抓取失败，跳过计数")
    #             return False
    #     return True

    def process_placement(self):
        """按队列顺序处理放置"""
        while self.grabbed_objects:
            current_label = self.grabbed_objects.pop(0)
            
            # 猫的放置逻辑（左右交替）
            if current_label == "cat":
                if self.cat_count % 2 == 0:
                    self.detect.place(self.positions[0])  # 左边
                else:
                    self.detect.place(self.positions[1])  # 右边
                self.cat_count += 1
            
            # 鸟的放置逻辑（左右交替）
            elif current_label == "bird":
                if self.bird_count % 2 == 0:
                    self.detect.place(self.positions[2])  # 左边
                else:
                    self.detect.place(self.positions[3])  # 右边
                self.bird_count += 1

    def run(self):
        """主程序逻辑"""
        basic.mc.power_on()
        time.sleep(1)
        basic.mc.set_color(0, 0, 255)
        self.detect.init_mycobot()
        self.init_camera()

        while cv2.waitKey(1) < 0 and not grabParams.done:
            try:
                time.sleep(0.5)
                ret, frame = self.cap.read()
                if not ret:
                    continue

                # 多帧一致性检测 
                detection = self.detect.obj_detect(frame)
                if detection is None:
                    self.detection_history = []
                    continue

                x, y, label = detection
                self.detection_history.append((x, y, label))
                
                if len(self.detection_history) > self.DETECTION_HISTORY_SIZE:
                    self.detection_history.pop(0)

                # 标签一致性校验 
                consistent_label = all(item[2] == label for item in self.detection_history)
                if not consistent_label:
                    continue

                # 检测到非目标类别时重启摄像头 
                if label not in ["cat", "bird"]:
                    print(f"检测到非目标类别: {label}，重启摄像头...")
                    self.cap.release()
                    cv2.destroyAllWindows()
                    time.sleep(2)
                    self.init_camera()
                    continue

                # 计算实际坐标
                real_x, real_y = self.detect.get_position(x, y)

                # 移动机械臂进行抓取
                self.detect.grab_move(real_x + grabParams.x_bias, real_y + grabParams.y_bias)

                # 注释掉抓取后验证逻辑，直接认为抓取成功 [[1]]
                # if not self.verify_grab(x, y):
                #     continue

                # 将成功抓取的物体加入队列
                self.grabbed_objects.append(label)
                self.process_placement()

                self.num += 1
                print(f"成功抓取次数: {self.num}, 当前猫计数: {self.cat_count}, 鸟计数: {self.bird_count}")

                # 完成指定次数后退出
                if self.num >= 6:
                    grabParams.done = True
                    basic.mc.set_color(0, 255, 0)
                    break

            except Exception as e:
                print(f"发生错误: {e}")
                retries = getattr(e, 'retries', 0)
                if retries >= self.MAX_RETRIES:
                    print("达到最大重试次数，终止程序")
                    break
                print(f"正在重试... ({retries+1}/{self.MAX_RETRIES})")
                e.retries = retries + 1
                time.sleep(2)

        # 清理资源
        self.cap.release()
        cv2.destroyAllWindows()
        basic.move_to_my_coords(grabParams.coords_ready_1, 60, 2)

if __name__ == '__main__':
    system = OptimizedGrabSystem()
    system.run()