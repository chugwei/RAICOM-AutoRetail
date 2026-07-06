#encoding: UTF-8
#!/usr/bin/env python2

from pymycobot.mycobot import MyCobot
from pymycobot.genre import Angle
import time

from GrabParams import grabParams

mc = MyCobot(grabParams.usb_dev, grabParams.baudrate)

angular = 0 # linear  = 1

#grap
def grap(flag):
    if flag:
        # close
        # self.mc.set_gripper_state(1, 0)
        time.sleep(0.1)
        mc.set_gripper_value(45,30)  
        time.sleep(1)
    else:
        # open
        time.sleep(0.1)
        mc.set_gripper_value(255,30)
        time.sleep(1)

def move_to_my_coords(coords,speed,times):
    print("move_to_my_coords")
    # mc.set_color(255,0,0)#blue, arm is busy
    mc.send_coords(coords,speed,angular)
    # mc.set_gripper_value(45,30)
    time.sleep(times)

def move_to_my_coords2(coords,speed,times):
    print("move_to_my_coords2")
    # mc.set_color(255,0,0)#blue, arm is busy
    mc.send_coords(coords,speed,1)
    # mc.set_gripper_value(45,30)
    time.sleep(times)

def move_to_target_z_offset(target_coords, z_offset, speed, delay_time, angular_before=0, angular_down=0):
    """
    :param target_coords: 目标坐标列表 [x, y, z, rx, ry, rz]
    :param z_offset: 上方高度偏移量(正数)
    :param speed: 移动速度
    :param delay_time: 移动后的等待时间
    :param angular_before: 移动到上方位置的移动模式(0=线性,1=关节)
    :param angular_down: 垂直下降的移动模式(0=线性,1=关节)
    """
    print("移动到目标上方")
    # 创建上方位置坐标 - Python 2 兼容版本
    above_target = list(target_coords)  # 创建副本
    above_target[2] = above_target[2] + z_offset  # 只修改Z轴高度
    
    # 移动到上方位置
    mc.send_coords(above_target, speed, angular_before)
    time.sleep(delay_time)
    
    print("开始垂直下降")
    # 获取当前坐标（应该在上方位置）
    current_coords = mc.get_coords()
    if not current_coords:
        print("无法获取当前坐标，使用上方位置坐标")
        current_coords = above_target
    
    # 计算下降步长和步数
    drop_height = z_offset
    step_size = 5  # 每次下降的毫米数，可根据需要调整
    steps = int(drop_height / step_size)
    
    # 确保至少有一次下降
    if steps == 0:
        steps = 1
    
    # 逐步下降
    for i in range(1, steps + 1):
        # 计算下一步的Z坐标
        next_z = current_coords[2] - step_size
        if next_z < target_coords[2]:
            next_z = target_coords[2]  # 确保不超过目标高度
        
        # 创建下一步坐标（只改变Z轴）
        next_coords = list(current_coords)
        next_coords[2] = next_z
        
        # 发送坐标指令
        mc.send_coords(next_coords, speed, angular_down)
        
        # 等待一小段时间让机械臂移动
        time.sleep(0.5)  # 可根据实际速度调整
        
        # 更新当前坐标
        current_coords = next_coords
    
    print("到达目标位置")
    # 确保最终到达目标位置
    mc.send_coords(target_coords, speed, angular_down)
    time.sleep(delay_time)
    
def get_coords():
    coords_now = []
    count = 0
    while len(coords_now)<6 and count < 6:  
        time.sleep(0.5)            
        coords_now = mc.get_coords()        
        print("get_coords ", coords_now, count)
        count = count + 1
        
    return coords_now
