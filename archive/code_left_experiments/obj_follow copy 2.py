#encoding: UTF-8
#!/usr/bin/env python2

from movement import Movement
from GrabParams import grabParams
from obj_detect import Detect_marker
import collections
import numpy as np  # ===== 新增导入 =====

import rospy, cv2, time
from geometry_msgs.msg import Twist

# done = grabParams.done

class Follow_object(object):

    def __init__(self):
        super(Follow_object, self).__init__()
        self.cap = None
        self.miss_count = 0
        self.max_moves = grabParams.max_moves  # 最大移动次数
        self.move_count = 0  # 移动计数器
        self.open_camera()

    def open_camera(self):
        self.cap = cv2.VideoCapture(grabParams.cap_num)
        if not self.cap.isOpened():
            print("Failed to open camera")

    def close_camera(self):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    # 保证物体在图像中心的方法
    def follow_obj(self, obj_info, back, middle):
        x, y, width, height, label = obj_info
        
        
        if middle + 60 > y > middle:
            move_cmd = Twist()
            move_cmd.linear.x = 0.01
            Movement().pub.publish(move_cmd)
            Movement().rate.sleep()
            return False  # ===== 新增返回 =====   
        
        elif back <=  y <= middle:  #停下
            Movement().stop()
            time.sleep(0.5)
            return True
        
        
        elif y < back:
            move_cmd = Twist()
            move_cmd.linear.x = -0.01
            Movement().pub.publish(move_cmd)
            Movement().rate.sleep()
            return False
        
        else:   #还没到
            move_cmd = Twist()
            move_cmd.linear.x = 0.02
            Movement().pub.publish(move_cmd)
            Movement().rate.sleep()
            return False  # ===== 新增返回 =====
    
    # ===== 新增函数：采集多帧位置数据并平均 =====
    def collect_position_samples(self, num_samples=5):
        """采集多帧位置数据并计算平均值"""
        positions = []  # 存储位置样本 [(x1, y1), (x2, y2), ...]
        valid_samples = 0
        
        # 最多尝试采集num_samples*2次，避免无限循环
        max_attempts = num_samples * 2
        attempts = 0
        
        print("开始采集位置样本，目标样本数:")
        print(num_samples)
        
        while valid_samples < num_samples and attempts < max_attempts:
            ret, frame = self.cap.read()
            if not ret:
                print("采集位置样本时无法读取帧")
                attempts += 1
                continue
            
            # 检测物体
            current_obj = Detect_marker().detect(frame)
            
            if current_obj is None:
                print("采集位置样本时未检测到物体")
                attempts += 1
                time.sleep(0.1)  # 短暂等待
                continue
            
            # 提取位置信息
            x, y, width, height, label = current_obj
            positions.append((x, y))
            valid_samples += 1
            print("采集到位置样本:",x,y)
            
            # 显示当前帧
            if grabParams.debug:
                cv2.imshow("Position Sampling", frame)
                cv2.waitKey(50)
            
            attempts += 1
            time.sleep(0.1)  # 短暂等待
        
        if valid_samples == 0:
            print("警告：未能采集到任何有效位置样本")
            return None, None
        
        # 计算平均值
        avg_x = sum(p[0] for p in positions) / valid_samples
        avg_y = sum(p[1] for p in positions) / valid_samples
        
        print("位置样本采集完成，平均值:")
        print(avg_x, avg_y)
        return avg_x, avg_y

    def moving_search(self):         
        done = False
        obj_info = None
        label_counter = collections.Counter()  # 用于统计标签出现次数
        last_detection = None  # 保存最后一次检测到的完整信息
        final_avg_position = None  # ===== 新增：存储平均位置 =====
        
        while cv2.waitKey(1) < 0 and not done:
            ret, frame = self.cap.read()
            if ret:
                current_obj = Detect_marker().detect(frame)
                if current_obj is None:
                    print("find none")
                    # self.miss_count += 1
                    # if self.miss_count > 20:
                    Movement().moveforward(0.02,0.2)
                        # self.move_count += 1
                        # if self.move_count >= self.max_moves:
                        #     print("Reached maximum move count, stopping search.")
                else:
                    print("find obj")
                    # 更新标签计数和保存最后检测结果
                    x, y, width, height, label = current_obj
                    label_counter[label] += 1
                    last_detection = current_obj
                    
                    # 检查物体是否进入合适位置
                    if self.follow_obj(current_obj, grabParams.stop_back, grabParams.stop_middle):
                        self.miss_count = 0
                        done = True
                        print("物体进入合适位置，开始采集多帧位置数据...")
                        # ===== 新增：采集多帧位置数据并平均 =====
                        avg_x, avg_y = self.collect_position_samples(num_samples=5)
                        final_avg_position = (avg_x, avg_y)  # 保存平均位置
        
        self.close_camera()
        
        # 如果检测到物体，使用出现频率最高的标签更新最后检测结果
        if last_detection and label_counter:
            # 获取出现频率最高的标签
            most_common_label = label_counter.most_common(1)[0][0]
            print("最终采用标签出现次数:")
            print( label_counter)
            print("最终采用标签:")
            print(most_common_label)
            
            # 更新obj_info中的标签为最常出现的标签
            x, y, width, height, _ = last_detection
            
            # ===== 修改：优先使用平均位置 =====
            if final_avg_position:
                avg_x, avg_y = final_avg_position
                print("位置样本采集完成，平均值:")
                print(avg_x,avg_y)
                obj_info = (avg_x, avg_y, width, height, most_common_label)
            else:
                print("使用单帧位置")
                obj_info = (x, y, width, height, most_common_label)
        else:
            obj_info = None
            
        return obj_info