#encoding: UTF-8
#!/usr/bin/env python2

import rospy
from geometry_msgs.msg import Twist

class Movement(object):

    def __init__(self):
        super(Movement, self).__init__()
        # rospy.init_node('movement', anonymous=True)
        self.pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)
        self.rate = rospy.Rate(20) # 20hz

    # 小车停止
    def stop(self):
        print("stopping...")
        move_cmd = Twist()  # 默认所有值为0
        self.pub.publish(move_cmd)
        self.rate.sleep()

    #小车后退
    def moveback(self, vel, time_seconds):
        print("backward...")
        count = 20*time_seconds
        move_cmd = Twist()
        while count > 0:
            move_cmd.linear.x = -vel #m/s-0.05
            self.pub.publish(move_cmd)
            self.rate.sleep()
            count -= 1

    #小车前进
    def moveforward(self, vel, time_seconds):		
        print("forward...")
        count = 20*time_seconds
        move_cmd = Twist()
        while count > 0:
            move_cmd.linear.x = vel #m/s0.05
            self.pub.publish(move_cmd)
            self.rate.sleep()
            count -= 1

    #小车右转
    def rotate_to_right(self, vel, time_seconds):
        print("rotate_to_right...")
        count = 20*time_seconds
        move_cmd = Twist()
        while count > 0:
            move_cmd.angular.z = -vel #rad/s-0.2
            self.pub.publish(move_cmd)
            self.rate.sleep()
            count -= 1

    #小车左转
    def rotate_to_left(self, vel, time_seconds):
        print("rotate_to_left...")
        count = 20*time_seconds
        move_cmd = Twist()
        while count > 0:
            move_cmd.angular.z = vel #rad/s0.2
            self.pub.publish(move_cmd)
            self.rate.sleep()            
            count -= 1

# move = Movement()
