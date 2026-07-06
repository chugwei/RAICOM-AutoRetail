#encoding: UTF-8
#!/usr/bin/env python2

from GrabParams import grabParams

import time
from pymycobot.mycobot import MyCobot
from pymycobot.genre import Angle

class Rob_basic(object):

    # 初始化机械臂连接和参数
    def __init__(self):
        super(Rob_basic, self).__init__()
        self.mc = MyCobot(grabParams.usb_dev, grabParams.baudrate)
        self.mc.power_on()
        self.angular = 0 # linear  = 1  # 0=角度模式，1=线性模式

    #grap
    # 控制夹爪开合 flag: True=闭合夹爪，False=打开夹爪
    def grap(self, flag):
        if flag:            # 闭合
            # close
            # self.mc.set_gripper_state(1, 0)
            time.sleep(0.1)
            self.mc.set_gripper_value(30,60)        # 值越小夹得越紧
            time.sleep(2)
        else:               # 打开
            # open
            time.sleep(0.1)
            self.mc.set_gripper_value(255,60)       # 值越大夹得越松
            time.sleep(2)

    # 移动机械臂到指定坐标
    def move_to_my_coords(self,coords,speed,times):
        print("move_to_my_coords")
        self.mc.set_color(0,0,255)#blue, arm is busy
        # self.mc.send_coords(coords,speed,1)
        self.mc.send_coords(coords,speed,self.angular)
        time.sleep(times)
    
    def move_to_my_coords2(self,coords,speed,times):
        print("move_to_my_coords")
        self.mc.set_color(0,0,255)#blue, arm is busy
        self.mc.send_coords(coords,speed,1)
    # self.mc.send_coords(coords,speed,self.angular)
        time.sleep(times)


    def move_to_my_angles(self,angles,speed,times):
        print("move_to_my_angles")
        self.mc.set_color(0,0,255)#blue, arm is busy
        self.mc.send_angles(angles,speed)
        time.sleep(times)


    # 获取当前机械臂坐标(带重试机制)
    def get_coords():
        coords_now = []
        count = 0
        while len(coords_now)<6 and count < 6:  
            time.sleep(0.5)            
            coords_now = self.mc.get_coords()        
            print("get_coords ", coords_now, count)
            count = count + 1
            
        return coords_now


    def get_angles():
        # angles = mc.get_angles()
        angles_now = []
        count = 0
        while len(angles_now)<6 and count < 6:
            time.sleep(0.5)
            angles = self.mc.get_angles()
            print("get_angles",angles_now,count)
            count = count + 1
        return angles_now

# def release_servo(servo_id):
#     mc.release_servo(servo_id)

# def release_all_servos():
#     mc.release_all_servos()

# def focus_servo(servo_id):
#     mc.focus_servo(servo_id)

# def focus_all_servos():
#     for servo_id in range(1,7):
#         mc.focus_servo(servo_id)
#         time.sleep(0.2)
