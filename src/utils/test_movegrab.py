#encoding: UTF-8
#!/usr/bin/env python2

import mobile_to_goal, sonor
from Basic import Rob_basic
from GrabParams import grabParams
from movement import Movement
from sonor import Sonor
from obj_detect import Detect_marker
from obj_follow import Follow_object
from pymycobot.mycobot import MyCobot

import time, rospy, cv2



def goal1_gab(obj_info):
    x, y, width, height, label = obj_info
    
    # 从参数类获取配置
    MODE = grabParams.mapping_mode
    RANGE_MIN = grabParams.linear_range_low
    RANGE_MAX = grabParams.linear_range_high
    STEP_COUNT = grabParams.step_count
    
    # 打印初始参数状态
    print("------------")
    print("参数状态:")
    print("映射模式: " + str(["三段式", "线性映射", "阶梯映射"][MODE]))
    print("宽度区间: [%s, %s]" % (RANGE_MIN, RANGE_MAX))
    print("物体宽度: " + str(width))
    print("距离参数: y_far=%s, y_near=%s" % (grabParams.y_far, grabParams.y_near))
    
    # 确保范围有效
    if abs(RANGE_MAX - RANGE_MIN) < 1e-5:  # 防止除零
        print("错误: 线性范围无效! 最大值等于最小值.")
        real_y = grabParams.y_middle  # 使用中间值作为默认值
    else:
        if width < RANGE_MIN:
            print("宽度(%s) < 下限(%s)，使用最远距离: %s" % (width, RANGE_MIN, grabParams.y_far))
            real_y = grabParams.y_far
        elif width > RANGE_MAX:
            print("宽度(%s) > 上限(%s)，使用最近距离: %s" % (width, RANGE_MAX, grabParams.y_near))
            real_y = grabParams.y_near
        else:
            if MODE == 0:  # 原三段式
                # 计算中间边界
                mid_point = RANGE_MIN + (RANGE_MAX - RANGE_MIN) / 2.0
                if width > mid_point:
                    real_y = grabParams.y_near
                else:
                    real_y = grabParams.y_middle
                    
                print("三段式映射:")
                print("中间点: %.2f" % mid_point)
                print("选择距离: %s" % real_y)
                
            elif MODE == 1:  # 线性映射
                # 确保使用浮点运算
                range_diff = float(RANGE_MAX - RANGE_MIN)
                y_diff = float(grabParams.y_near - grabParams.y_far)
                k = y_diff / range_diff
                b = grabParams.y_far - k * RANGE_MIN
                real_y = k * width + b
                
                print("线性公式: y = %.4f * x + %.4f" % (k, b))
                print("计算值: y = %.4f * %s + %.4f = %.2f" % (k, width, b, real_y))
                
            else:  # MODE == 2 阶梯映射
                width_step = float(RANGE_MAX - RANGE_MIN) / STEP_COUNT
                step_index = min(STEP_COUNT - 1, int((width - RANGE_MIN) / width_step))
                y_step = float(grabParams.y_near - grabParams.y_far) / STEP_COUNT
                real_y = grabParams.y_far + y_step * step_index
                
                print("阶梯映射:")
                print("宽度步长: %.2f, 距离步长: %.2f" % (width_step, y_step))
                print("阶梯索引: %d (共%d阶)" % (step_index, STEP_COUNT))
                print("计算值: %.2f" % real_y)
    
    # 确保在安全范围内
    real_y = max(grabParams.y_far, min(grabParams.y_near, real_y))
    
    # 打印最终结果
    print("最终目标距离参数: " + str(real_y))
    print("------------")
    
    # 移动到目标位置
    Detect_marker().grab_move(1.6, real_y)

if __name__ == '__main__':
    
    rospy.init_node('send_goals_python',anonymous=True)
    basic = Rob_basic()
    move = Movement()
    # sonor = Sonor()
    Detect = Detect_marker()
    follow = Follow_object()


    
    basic.move_to_my_angles(grabParams.angles_ready,80,1.5)
    basic.move_to_my_coords(grabParams.coords_ready,80,0)
    
    time.sleep(1.5)
    
    # 机械臂初始化     
    Detect.init_mycobot()
    # 视觉搜索物体
    detect_result = follow.moving_search()

    goal1_gab(detect_result)
    basic.grap(False)
        
    basic.move_to_my_coords(grabParams.coords_ready,80,1.5)

    time.sleep(0.5)
    
    follow.open_camera()
    # 视觉搜索物体
    detect_result = follow.moving_search()

    goal1_gab(detect_result)
    basic.grap(False)
        
    basic.move_to_my_coords(grabParams.coords_ready,80,1.5)
    time.sleep(0.5)

    follow.open_camera()
    # 视觉搜索物体
    detect_result = follow.moving_search()
    
    # 执行抓取
    goal1_gab(detect_result)
    basic.grap(False)
        
    basic.move_to_my_coords(grabParams.coords_ready,80,1.5)
    time.sleep(0.5)


    follow.open_camera()
    # 视觉搜索物体
    detect_result = follow.moving_search()
    
    # 执行抓取
    goal1_gab(detect_result)
    basic.grap(False)
        
    basic.move_to_my_coords(grabParams.coords_ready,80,1.5)

    move.backward_trapezoidal(0.45,0.08,0.5)
    time.sleep(5)

    for _ in range(4):

        # 视觉搜索物体
        follow.open_camera()
        # 视觉搜索物体
        detect_result = follow.moving_search()

        goal1_gab(detect_result)
        basic.grap(False)
            
        basic.move_to_my_coords(grabParams.coords_ready,80,1.5)

        time.sleep(0.5)
        
        follow.open_camera()
        # 视觉搜索物体
        detect_result = follow.moving_search()

        goal1_gab(detect_result)
        basic.grap(False)
            
        basic.move_to_my_coords(grabParams.coords_ready,80,1.5)

        time.sleep(0.5)

        follow.open_camera()
        # 视觉搜索物体
        detect_result = follow.moving_search()
        
        # 执行抓取
        goal1_gab(detect_result)
        basic.grap(False)
            
        basic.move_to_my_coords(grabParams.coords_ready,80,1.5)
        time.sleep(0.5)


        follow.open_camera()
        # 视觉搜索物体
        detect_result = follow.moving_search()
        
        # 执行抓取
        goal1_gab(detect_result)
        basic.grap(False)
            
        basic.move_to_my_coords(grabParams.coords_ready,80,1.5)

        move.backward_trapezoidal(0.45,0.08,0.5)
        time.sleep(5)



