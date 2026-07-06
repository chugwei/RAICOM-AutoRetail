#encoding: UTF-8
#!/usr/bin/env python2

import re, rospy, actionlib, os, json
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Pose, Point, Quaternion

def read_goal(filename):
    goal = MoveBaseGoal() 
    print("开始...")
    file_to_read = open(filename)
    index = 0
    for line in file_to_read.readlines():
        line = line.strip()
        index += 1
        if index == 2:
            pattern = re.compile(r"(?<=\[).*?(?=\])")
            query = pattern.search(line)
            listFromLine = query.group().split(',')
            goal.target_pose.pose.position.x = float(listFromLine[0])
            goal.target_pose.pose.position.y = float(listFromLine[1])
        if index == 3:
            pattern = re.compile(r"(?<=\[).*?(?=\])")
            query = pattern.search(line)
            listFromLine = query.group().split(',')
            goal.target_pose.pose.orientation.z = float(listFromLine[2])
            goal.target_pose.pose.orientation.w = float(listFromLine[3])

    print(goal.target_pose.pose)
    print("坐标接收完毕...")
    return goal

def read_goal_from_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
        
    goals = []
    for entry in data:
        goal = MoveBaseGoal()
        
        # 设置平移信息
        translation = entry["translation"]
        goal.target_pose.pose.position = Point(translation[0], translation[1], translation[2])
        
        # 设置旋转信息（四元数）
        quaternion = entry["rotation"]["quaternion"]
        goal.target_pose.pose.orientation = Quaternion(quaternion[0], quaternion[1], quaternion[2], quaternion[3])
        
        goals.append(goal)
    
    return goals

def send_goal(goal_number, goal):
    client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
    print("等待与服务端连接")
    client.wait_for_server()
    print("与服务端连接成功")
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()
    client.send_goal(goal)
    str_log = "Send NO. %s Goal !!!" %str(goal_number)
    rospy.loginfo(str_log)

    wait = client.wait_for_result(rospy.Duration.from_sec(60.0))  
    if not wait:
        str_log="The NO. %s Goal Planning Failed for some reasons" %str(goal_number)
        rospy.loginfo(str_log)
    else:
        str_log="The NO. %s Goal achieved success !!!" %str(goal_number)
        rospy.loginfo(str_log)

