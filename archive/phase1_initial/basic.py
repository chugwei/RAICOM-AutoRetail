#encoding: UTF-8
#!/usr/bin/env python2

# 导入机械臂控制类
from pymycobot.mycobot import MyCobot
# 导入角度相关的枚举类型（当前文件中未直接使用）
from pymycobot.genre import Angle
import time

# 导入抓取任务所需的串口和波特率参数
from GrabParams import grabParams

# 初始化机械臂连接
mc = MyCobot(grabParams.usb_dev, grabParams.baudrate)

# 坐标运动模式：0 表示角度/姿态模式，1 表示线性模式
angular = 0 # linear  = 1

# 控制夹爪开合
def grap(flag):
    # flag 为真时闭合夹爪，否则张开夹爪
    if flag:
        # close
        # self.mc.set_gripper_state(1, 0)
        time.sleep(0.1)
        # 设置夹爪闭合到较小开口，30 为速度
        mc.set_gripper_value(45,30)
        time.sleep(1)
    else:
        # open
        time.sleep(0.1)
        # 设置夹爪完全张开，30 为速度
        mc.set_gripper_value(255,30)
        time.sleep(1)

# 按当前全局运动模式移动到指定坐标
def move_to_my_coords(coords,speed,times):
    print("move_to_my_coords")
    # mc.set_color(255,0,0)#blue, arm is busy
    # 发送目标坐标，speed 为速度，angular 为运动模式
    mc.send_coords(coords,speed,angular)
    # mc.set_gripper_value(45,30)
    # 等待机械臂执行完成
    time.sleep(times)

# 以线性模式移动到指定坐标
def move_to_my_coords2(coords,speed,times):
    print("move_to_my_coords2")
    # mc.set_color(255,0,0)#blue, arm is busy
    # 第三个参数固定为 1，表示使用线性轨迹运动
    mc.send_coords(coords,speed,1)
    # mc.set_gripper_value(45,30)
    # 等待机械臂执行完成
    time.sleep(times)

# 获取当前机械臂坐标
def get_coords():
    coords_now = []
    count = 0
    # 最多尝试 6 次，直到成功拿到 6 维坐标数据
    while len(coords_now)<6 and count < 6:  
        time.sleep(0.5)            
        coords_now = mc.get_coords()        
        print("get_coords ", coords_now, count)
        count = count + 1
        
    return coords_now
