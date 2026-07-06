#encoding: UTF-8
#!/usr/bin/env python2

from movement import Movement

import rospy,time
from sensor_msgs.msg import Range

class Sonor(object):

    def __init__(self):
        super(Sonor, self).__init__()
        self.data = rospy.wait_for_message('sonor_range',Range)
    # 获取超声波数据    
    def get_sonor_data(self):
        # data = rospy.wait_for_message('sonor_range',Range)
        distance = self.data.range
        # print(distance)
        return distance

    # 目标点1的距离保持控制
    def sonor_control_goal_1(self):
        distance = self.get_sonor_data()
        # time.sleep(0.5)
        if distance > 0.30:   # default: 0.31 0.32 0.30         # 太远
            Movement().moveforward(0.03, 0.2)#0.05,0.3
            return False
        elif distance < 0.28: # default: 0.27 0.30 0.28         # 太近
            Movement().moveback(0.03, 0.2)
            return False
        else:                                                   # 合适距离
            Movement().stop()
            return True

    def sonor_control_goal_2(self):
        distance = self.get_sonor_data()
        # time.sleep(0.5)
        if distance > 0.69: #0.68
            Movement().moveforward(0.05, 0.3)
            return False
        elif distance < 0.67: #0.66 0.67
            Movement().moveback(0.05, 0.3)
            return False
        else:
            Movement().stop()
            return True
        
    def sonor_control_goal_3(self):
        distance = self.get_sonor_data()

        if distance > 0.35: #60，0.56
            Movement().moveforward(0.03, 0.2)#0.05,0.3
            return False
        elif distance < 0.33: #58，0.54
            Movement().moveback(0.03, 0.2)
            return False
        else:
            Movement().stop()
            return True

    def sonor_control_goal_4(self):
        distance = self.get_sonor_data()
        # time.sleep(0.5)
        if distance > 0.22:   # default: 0.31
            Movement().moveforward(0.05, 0.5)
            return False
        elif distance < 0.20: # default: 0.27
            Movement().moveback(0.05, 0.5)
            return False
        else:
            Movement().stop()
            return True


    def sonor_control_goal_5(self):
            distance = self.get_sonor_data()
            if distance > 0.56: #60，0.56
                Movement().moveforward(0.05, 0.5)#0.05,0.3
                return False
            elif distance < 0.54: #58，0.54
                Movement().moveback(0.05, 0.5)
                return False
            else:
                Movement().stop()
                return True

    def sonor_control_goal_6(self):
            distance = self.get_sonor_data()
            # time.sleep(0.5)
            if distance > 0.64: #0.68
                Movement().moveforward(0.05, 0.3)
                return False
            elif distance < 0.62: #0.66 0.67
                Movement().moveback(0.05, 0.3)
                return False
            else:
                Movement().stop()
                return True