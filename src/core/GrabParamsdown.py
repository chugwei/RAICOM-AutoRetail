#encoding: UTF-8
#!/usr/bin/env python2

class GrabParams(object):

    # 物体放置位置配置
    pace_apple_site = "left"            #设置放置方位(left/right)
    # pace_apple_site = "right"
    
    # get the results by calibration
    ratio = 0.223 #0.223 #0.196    0.230      # 像素到实际坐标的转换比例230,219
    
    # 增加x向左，减少x向右
    x_bias =  16# 18       # X轴偏移校准

    #增加y向上，减少y向下
    y_bias = 8   #8              # Y轴偏移校准


    #############以下坐标轴是经过修改，是正确的
    #               	 (y)front
    #                 	  
    #				 	  :
    #				  	  :
    #                 	  :
    # (x)< ..............o..............(-x)right
    #					  :
    #					  :
    #					  :
    #					  :
    #					 (-y)

    # increase height_bias to move higher, or decrease height_bias to move lower+50
    
    # 机械臂高度参数
    height_bias = 264.1 + 62  #50  原来的是：264.1 + 72         # 抓取高度偏移
    y = -120   #-120

    # 映射关系控制参数
    mapping_mode = 1  # 映射模式: 0=三段式, 1=线性映射, 2=阶梯映射
    linear_range_low = 120  # 线性映射区间下限
    linear_range_high = 195  # 线性映射区间上限
    step_count = 10  # 阶梯映射的阶梯数量

    y_far = -120
    y_middle = -90
    y_near = -75

    grab_direct = "front"

    angles_ready = [-89.56, -54.05, 82.96, -27.68, -1.66, -46.66] #[-88.33, -64.59, 107.84, -47.02, -1.58, 131.3]
    coords_ready = [-64.0, -87.4, 330, -88.2, -46.62, 177.46] #[-62.1, -79.3, 315, 91.96, 47.9, 2]
    angles_finish = [-89.38, -34.45, 62.92, 12.56, 0.52, -45.7]
    coords_finish = [-62.9, -2.4, 393.1, -38.5, -32.95, 146.94]
    

    # 根据放置位置设置目标坐标
    if pace_apple_site == "left":
        coords_place_apple = [-278.1, -87.0, 145, -145.11, -27.32, 146.66]  #我的右边
        coords_place_apple2 = [-278.1, -87.0, 195, -145.11, -27.32, 146.66]
        coords_place_clock = [-234.5, 114.6, 150, 135.87, 42.76, -65.28]        #我的左边
        
    if pace_apple_site == "right":
        coords_place_apple = [252.8, -114.8, 139.8, 157.4, 23.51, 100.7]
        coords_place_clock = [267.3, 76.5, 149.5, 153.88, 24.93, 138.77]

    # 运动控制参数
    max_moves = 50                              # 最大移动次数
    GRAB_MOVE_SPEED = 20                        # 抓取移动速度
    stop_back =  345             # 物体检测前停止阈值(像素)
    stop_middle = 325  #350,410，420 460          # 物体检测后停止阈值(像素)
    debug = True #True         

    # please do not change the parameter values below
    # 系统参数(勿修改)
    IMG_SIZE = 640                              # 图像尺寸
    done = False                                # 任务完成标志
    cap_num = 2                                 # 摄像头设备号
    usb_dev = "/dev/arm"                        # 机械臂设备路径
    baudrate = 115200                           # 串口波特率

grabParams = GrabParams()

