#encoding: UTF-8
#!/usr/bin/env python2

from movement import Movement
from GrabParams import grabParams
from obj_detect import Detect_marker
import collections

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
    def follow_obj(self, obj_info, top, middle):
        x, y, width, height, label = obj_info
        
        if top <=  y <= middle:  #停下
            Movement().stop()
            time.sleep(0.5)
            return True
        
        elif y < top:
            move_cmd = Twist()
            move_cmd.linear.x = -0.02
            Movement().pub.publish(move_cmd)
            Movement().rate.sleep()
            return False
        
        else:   #还没到
            move_cmd = Twist()
            move_cmd.linear.x = 0.02
            Movement().pub.publish(move_cmd)
            Movement().rate.sleep()
        

        


        # else:  # 图像还在前面，小车要给点前进，并确保物体在图像中心
        #     move_cmd = Twist()
        #     move_cmd.linear.x = 0.02
        #     Movement().pub.publish(move_cmd)
        #     Movement().rate.sleep()
        #     return False
        
    # # 保证物体在图像中心的方法
    # def follow_obj(self, obj_info, top, middle):
    #     x, y, width, height, label = obj_info
    #     if y > top:  #还没到
    #         print("物体的y值:",y)
    #         return False
    #     elif y < middle:  #停下
    #         Movement().stop()
    #         time.sleep(0.5)
    #         return True
    #     # elif y < back:
    #     #     Movement().stop()
    #     #     Movement().moveback(0.03, 0.30)
    #     #     time.sleep(0.5)
    #     # return False
    #     else:  # 图像还在前面，小车要给点前进，并确保物体在图像中心
    #         move_cmd = Twist()
    #         move_cmd.linear.x = 0.02
    #         Movement().pub.publish(move_cmd)
    #         Movement().rate.sleep()
    #         return False



    def moving_search(self):         
        done = False
        obj_info = None
        label_counter = collections.Counter()  # 用于统计标签出现次数
        last_detection = None  # 保存最后一次检测到的完整信息
        
        while cv2.waitKey(1) < 0 and not done:
            ret, frame = self.cap.read()
            if ret:
                current_obj = Detect_marker().detect(frame)
                if current_obj is None:
                    print("find none")
                    self.miss_count += 1
                    if self.miss_count > 20:
                        Movement().moveforward(0.02,0.2)
                        self.move_count += 1
                        if self.move_count >= self.max_moves:
                            print("Reached maximum move count, stopping search.")
                else:
                    print("find obj")
                    # 更新标签计数和保存最后检测结果
                    x, y, width, height, label = current_obj
                    label_counter[label] += 1
                    last_detection = current_obj
                    
                    if self.follow_obj(current_obj, grabParams.stop_top, grabParams.stop_middle):
                        self.miss_count = 0
                        done = True
                    # else:
                    #     self.miss_count += 1
                    #     if self.miss_count > 20:
                    #         Movement().moveforward(0.02,0.1)
                    #         self.move_count += 1
                    #         if self.move_count >= self.max_moves:
                    #             print("Reached maximum move count, stopping search.")
        
        self.close_camera()
        
        # 如果检测到物体，使用出现频率最高的标签更新最后检测结果
        if last_detection and label_counter:
            # 获取出现频率最高的标签
            most_common_label = label_counter.most_common(1)[0][0]
            print(u"最终采用标签出现次数:", label_counter)
            print(u"最终采用标签:", most_common_label)
            
            # 更新obj_info中的标签为最常出现的标签
            x, y, width, height, _ = last_detection
            obj_info = (x, y, width, height, most_common_label)
        else:
            obj_info = None
            
        return obj_info
    
    # # 移动搜索
    # def moving_search(self):         
    #     done = False
    #     obj_info = None
    #     while cv2.waitKey(1) < 0 and not done:
    #         ret, frame = self.cap.read()
    #         # print("ret:",ret)
    #         if ret:
    #             obj_info = Detect_marker().detect(frame)
    #             if obj_info is None:
    #                 print("find none")
    #                 self.miss_count += 1
    #                 if self.miss_count > 20:
    #                     Movement().moveforward(0.02,0.2)
    #                     self.move_count += 1
    #                     if self.move_count >= self.max_moves:
    #                         print("Reached maximum move count, stopping search.")
    #             else:
    #                 print("find obj") 
    #                 if self.follow_obj(obj_info, grabParams.stop_top, grabParams.stop_middle):
    #                     self.miss_count = 0
    #                     done = True
    #                     # print("查看done状态：",done)
    #                 else:
    #                     self.miss_count += 1
    #                     if self.miss_count > 20:
    #                         Movement().moveforward(0.02,0.1)
    #                         self.move_count += 1
    #                         if self.move_count >= self.max_moves:
    #                             print("Reached maximum move count, stopping search.")
    #     self.close_camera()  # 搜索结束后关闭摄像头
    #     return obj_info

        
    # def get_average_position(self):
    #     """进行3次检测并计算平均位置"""
    #     position_sum = [0, 0]  # [x_sum, y_sum]
    #     valid_detections = 0
        
    #     for _ in range(5):
    #         ret, frame = self.cap.read()
    #         if not ret:
    #             continue
                
    #         obj_info = Detect_marker().detect(frame)
    #         if obj_info:
    #             x, y, width, height, label = obj_info
    #             position_sum[0] += x
    #             position_sum[1] += y
    #             valid_detections += 1
    #         time.sleep(0.1)  # 短暂间隔
        
    #     if valid_detections == 0:
    #         print("警告：三次检测均未发现物体")
    #         return None
            
    #     avg_x = position_sum[0] / valid_detections
    #     avg_y = position_sum[1] / valid_detections
    #     print("平均位置计算完成")
        
    #     # 返回平均位置（使用最后一次检测的width/height/label）
    #     return (avg_x, avg_y, obj_info[2], obj_info[3], obj_info[4])

    # def moving_search(self):         
    #     done = False
    #     final_obj_info = None
        
    #     while cv2.waitKey(1) < 0 and not done:
    #         ret, frame = self.cap.read()
    #         if ret:
    #             obj_info = Detect_marker().detect(frame)
    #             if obj_info is None:
    #                 self.miss_count += 1
    #                 if self.miss_count > 20:
    #                     Movement().moveforward(0.02,0.2)
    #                     self.move_count += 1
    #                     if self.move_count >= self.max_moves:
    #                         print("达到最大移动次数，停止搜索")
    #             else:
    #                 if self.follow_obj(obj_info, grabParams.stop_top, grabParams.stop_middle):
    #                     self.miss_count = 0
    #                     done = True
    #                     time.sleep(3)
    #                     # 到达位置后进行三次检测
    #                     final_obj_info = self.get_average_position()
    #                 else:
    #                     self.miss_count += 1
    #                     if self.miss_count > 20:
    #                         Movement().moveforward(0.02,0.1)
    #                         self.move_count += 1
        
    #     self.close_camera()
    #     return final_obj_info  # 返回平均位置信息