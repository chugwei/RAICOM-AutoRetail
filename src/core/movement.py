#!/usr/bin/env python2
# encoding: UTF-8

import rospy
from geometry_msgs.msg import Twist
import math

class Movement(object):
    def __init__(self):
        super(Movement, self).__init__()
        self.pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)
        self.rate = rospy.Rate(20)  # 20Hz
        self.TIME_STEP = 0.05  # 50ms
    
    # 小车停止（保持不变）
    def stop(self):
        print("stopping...")
        move_cmd = Twist()
        self.pub.publish(move_cmd)
        self.rate.sleep()
    
    # 小车后退（简单控制，保持不变）
    def moveback(self, vel, time_seconds):
        print("backward...")
        count = 20*time_seconds
        move_cmd = Twist()
        while count > 0:
            move_cmd.linear.x = -vel
            self.pub.publish(move_cmd)
            self.rate.sleep()
            count -= 1
    
    # 小车前进（简单控制，保持不变）
    def moveforward(self, vel, time_seconds):     
        print("forward...")
        count = 20*time_seconds
        move_cmd = Twist()
        while count > 0:
            move_cmd.linear.x = vel
            self.pub.publish(move_cmd)
            self.rate.sleep()
            count -= 1
    
    # 小车右转（简单控制，保持不变）
    def rotate_to_right(self, vel, time_seconds):
        print("rotate_to_right...")
        count = 20*time_seconds
        move_cmd = Twist()
        while count > 0:
            move_cmd.angular.z = -vel
            self.pub.publish(move_cmd)
            self.rate.sleep()
            count -= 1
    
    # 小车左转（简单控制，保持不变）
    def rotate_to_left(self, vel, time_seconds):
        print("rotate_to_left...")
        count = 20*time_seconds
        move_cmd = Twist()
        while count > 0:
            move_cmd.angular.z = vel
            self.pub.publish(move_cmd)
            self.rate.sleep()            
            count -= 1
    
    # ======================================
    # 以下为梯形速度控制的专用方法
    # ======================================
    
    # 梯形速度控制的前进运动
    def forward_trapezoidal(self, distance, max_vel, decel_time):
        """
        梯形速度控制前进
        :param distance: 前进距离 (米)
        :param max_vel: 最大速度 (m/s, 正值)
        :param decel_time: 减速到零的持续时间 (秒)
        """
        print("trapezoidal forward motion...")
        if distance < 0:
            rospy.logwarn("Forward distance cannot be negative. Using positive value.")
            distance = -distance
        self._trapezoidal_movement(max_vel, decel_time, distance, is_linear=True)
    
    # 梯形速度控制的后退运动
    def backward_trapezoidal(self, distance, max_vel, decel_time):
        """
        梯形速度控制后退
        :param distance: 后退距离 (米)
        :param max_vel: 最大速度 (m/s, 正值)
        :param decel_time: 减速到零的持续时间 (秒)
        """
        print("trapezoidal backward motion...")
        if distance < 0:
            rospy.logwarn("Backward distance cannot be negative. Using positive value.")
            distance = -distance
        self._trapezoidal_movement(-max_vel, decel_time, -distance, is_linear=True)
    
    # 梯形速度控制的左转运动
    def left_trapezoidal(self, degrees, max_vel, decel_time):
        """
        梯形速度控制左转
        :param degrees: 左转角度 (度)
        :param max_vel: 最大角速度 (rad/s, 正值)
        :param decel_time: 减速到零的持续时间 (秒)
        """
        print("trapezoidal left rotation:" ,degrees)
        radians = math.radians(degrees)
        if radians < 0:
            rospy.logwarn("Left rotation cannot be negative. Using positive value.")
            radians = -radians
        self._trapezoidal_movement(max_vel, decel_time, radians, is_linear=False)
    
    # 梯形速度控制的右转运动
    def right_trapezoidal(self, degrees, max_vel, decel_time):
        """
        梯形速度控制右转
        :param degrees: 右转角度 (度)
        :param max_vel: 最大角速度 (rad/s, 正值)
        :param decel_time: 减速到零的持续时间 (秒)
        """
        print("trapezoidal right rotation:", degrees)
        radians = math.radians(degrees)
        if radians < 0:
            rospy.logwarn("Right rotation cannot be negative. Using positive value.")
            radians = -radians
        self._trapezoidal_movement(-max_vel, decel_time, -radians, is_linear=False)
    
    # 梯形速度控制的通用实现（内部方法）
    def _trapezoidal_movement(self, max_vel, decel_time, total_value, is_linear):
        if abs(max_vel) < 0.01:
            rospy.logwarn("Invalid max velocity: %.3f", max_vel)
            return
            
        if abs(total_value) < 0.001:
            rospy.logwarn("Invalid movement value: %.3f", total_value)
            return
            
        if decel_time <= 0:
            rospy.logwarn("Deceleration time must be positive: %.3f", decel_time)
            return
        
        # 确定运动方向
        direction = 1 if max_vel >= 0 else -1
        abs_vel = abs(max_vel)
        abs_value = abs(total_value)
        
        # 计算加速度
        acceleration = abs_vel / decel_time
        
        # 计算加速阶段位移/角度
        accel_dist = (abs_vel ** 2) / (2 * acceleration)
        
        # 检查是否需要使用三角形速度曲线（无匀速阶段）
        use_triangle_profile = accel_dist * 2 > abs_value
        
        if use_triangle_profile:
            # 计算实际能达到的最大速度
            real_max_vel = math.sqrt(acceleration * abs_value) * direction
            
            # 计算加速阶段时间
            accel_time = math.sqrt(abs_value / acceleration)
            decel_time = accel_time
            total_time = accel_time * 2
            abs_vel = abs(real_max_vel)
            
            rospy.loginfo("Using triangle profile: max speed %.3f, acceleration time %.3fs, deceleration time %.3fs", 
                         abs_vel * direction, accel_time, decel_time)
        else:
            # 梯形曲线
            real_max_vel = max_vel
            
            # 计算匀速阶段长度
            const_dist = abs_value - (2 * accel_dist)
            
            # 计算各阶段持续时间
            accel_time = decel_time
            const_time = const_dist / abs_vel
            total_time = accel_time + const_time + decel_time
            
            rospy.loginfo("Using trapezoidal profile: max speed %.3f, acceleration %.3f (%d%%), constant speed %.3f (%d%%), deceleration %.3f (%d%%)", 
                         abs_vel * direction, 
                         accel_dist, int(accel_dist * 100 / abs_value),
                         const_dist, int(const_dist * 100 / abs_value),
                         accel_dist, int(accel_dist * 100 / abs_value))
        
        # 开始运动控制
        start_time = rospy.get_time()
        while rospy.get_time() - start_time < total_time:
            elapsed = rospy.get_time() - start_time
            move_cmd = Twist()
            
            if use_triangle_profile:
                # 三角形速度曲线
                if elapsed < accel_time:  # 加速阶段
                    current_vel = (abs_vel / accel_time) * elapsed
                else:  # 减速阶段
                    current_vel = abs_vel - (abs_vel / accel_time) * (elapsed - accel_time)
            else:
                # 梯形速度曲线
                if elapsed < accel_time:  # 加速阶段
                    current_vel = (abs_vel / accel_time) * elapsed
                elif elapsed < accel_time + const_time:  # 匀速阶段
                    current_vel = abs_vel
                else:  # 减速阶段
                    current_vel = abs_vel - (abs_vel / decel_time) * (elapsed - (accel_time + const_time))
            
            # 应用方向
            current_vel *= direction
            
            # 设置运动命令
            if is_linear:
                move_cmd.linear.x = current_vel
            else:
                move_cmd.angular.z = current_vel
            
            self.pub.publish(move_cmd)
            self.rate.sleep()
        
        # 确保最终停止
        self.stop()