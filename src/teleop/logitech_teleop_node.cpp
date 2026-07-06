#include <ros/ros.h>
#include <geometry_msgs/Twist.h>
#include <std_msgs/String.h> 
#include <sensor_msgs/Joy.h>
#include <actionlib/server/simple_action_server.h>
#include <boost/shared_ptr.hpp>
#include <nav_msgs/Odometry.h>
#include <unistd.h> 

using namespace std;
 
// Logitech 手柄遥控节点：
// 1. 订阅手柄的 joy 话题
// 2. 将摇杆输入转换为底盘速度并发布到 cmd_vel
// 3. 结合不同按键触发机械臂相关的 Python 脚本
class LogTeleop
{
public:
    LogTeleop();
 
private:
    // 手柄消息回调函数
    void LogCallback(const sensor_msgs::Joy::ConstPtr& Joy);
    // ROS 节点句柄
    ros::NodeHandle n;
    // 手柄订阅者
    ros::Subscriber sub ;
    // 底盘速度发布者
    ros::Publisher pub ;
    // move_base 任务取消发布者
    ros::Publisher cancel_pub_;
    // 线速度、角速度比例系数
    double vlinear,vangular;
    // 摇杆轴索引和使能按键索引
    int axis_ang_z,axis_lin_x,ton;
    // 空 GoalID，用于取消当前导航目标
    actionlib_msgs::GoalID empty_goal_;
    // 线速度加速度相关变量（当前仅保留参数）
    double acc_linear_x;
    double current_linear_x;
    // 标记上一帧是否处于遥控激活状态，用于松开按键后停车
    bool b_flag;
};
 
LogTeleop::LogTeleop()
{
    // 从参数服务器读取手柄轴映射和速度参数，未配置时使用默认值
    n.param<int>("axis_linear_x",axis_lin_x,1);
    n.param<int>("axis_angular_z",axis_ang_z,2);
    n.param<double>("vel_linear",vlinear,0.25);
    n.param<double>("vel_angular",vangular,0.2);
    n.param<int>("button",ton,5);
    n.param<double>("acc_linear_x",acc_linear_x,0.1);
    // 发布底盘速度指令
    pub= n.advertise<geometry_msgs::Twist>("cmd_vel", 1, true);
    // 订阅手柄输入
    sub = n.subscribe<sensor_msgs::Joy>("joy",1,&LogTeleop::LogCallback,this);
    // 发布取消导航任务的消息，避免手动接管时导航继续控制底盘
    cancel_pub_ = n.advertise<actionlib_msgs::GoalID>("move_base/cancel",1);
    b_flag = false;
}


void LogTeleop::LogCallback(const sensor_msgs::Joy::ConstPtr& Joy)
{
	// 用于保存本次要发布的底盘速度
	geometry_msgs::Twist twist;

	// 只有按住使能键时，才允许遥控和功能触发
	if(Joy->buttons[ton])//button RB
	{
		// X 键：抓取上层或 ArUco 抓取
		if(Joy->buttons[0])//button X
		{
			// 先结束已有 Python 抓取脚本，避免多个脚本同时运行
			system("killall -9 python");
			if(Joy->buttons[4])//button LB
			{
				// LB + X：执行上层抓取
				system("python /home/robuster/beetle_ai/scripts/pick_top.py");
				printf("pick_top");
			}
			else
			{
				// X：执行 ArUco 识别抓取
				system("python /home/robuster/beetle_ai/scripts/aruco_grab.py");
				printf("aruco_grab");
			}			 
			ros::Duration(1).sleep();
		}
		// Y 键：抓取下层或颜色抓取
		else if(Joy->buttons[3])//button Y
		{
			system("killall -9 python");
			if(Joy->buttons[4])//button LB
			{
				// LB + Y：执行下层抓取
				system("python /home/robuster/beetle_ai/scripts/pick_bottom.py");
				printf("pick_bottom");
			}
			else
			{
				// Y：执行颜色识别抓取
				system("python /home/robuster/beetle_ai/scripts/color_grab.py");
				printf("colo_grab");
			}			 
			ros::Duration(1).sleep();
		}
		// B 键：执行深度学习抓取
		else if(Joy->buttons[2])//button B
		{
			system("killall -9  python");
			system("python /home/robuster/beetle_ai/scripts/dnn_grab.py");
			printf("dnn_grab");
			ros::Duration(1).sleep();
		}
		// A 键：执行放置动作
		else if(Joy->buttons[1])//button A
		{
			system("killall -9  python");
			system("python /home/robuster/beetle_ai/scripts/place.py");
			printf("place"); 
			ros::Duration(1).sleep();
		}
		// Back 键：机械臂回 home 位
		else if(Joy->buttons[8])//button Back
		{
			system("killall -9  python");
			system("python /home/robuster/beetle_ai/scripts/home.py");
			printf("home"); 
			ros::Duration(1).sleep();
		}
		// Start 键：机械臂回零位
		else if(Joy->buttons[9])//button Start
		{
			system("killall -9  python");
			system("python /home/robuster/beetle_ai/scripts/zero.py");
			printf("zero"); 
			ros::Duration(1).sleep();
		}

		// 标记当前处于手动控制状态
		b_flag = true;

		// 使用手柄轴值微调最大线速度，并限制在安全范围内
		vlinear = vlinear * (1 + (Joy->axes[5] * 0.1));
		if(vlinear>=1.0)
		   vlinear = 1.0;
		else if (vlinear<=0.1)
		   vlinear = 0.1;
		else
		   vlinear = vlinear;
		
		// 使用手柄轴值微调最大角速度，并限制在安全范围内
		vangular = vangular * (1 +  (Joy->axes[4] * 0.1));
		if(vangular>=1.5)
			vangular = 1.5;
		else if(vangular<=0.1)
			vangular = 0.1;
		else
			vangular = vangular;

	    // 根据摇杆输入生成底盘线速度和角速度
	    twist.linear.x =(Joy->axes[axis_lin_x])*vlinear;
	    twist.linear.y = 0;
	    twist.linear.z = 0;
	    
	    twist.angular.x = 0;
	    twist.angular.y = 0;
	    twist.angular.z =(Joy->axes[axis_ang_z])*vangular;

		// 发布手动遥控速度
		pub.publish(twist);

		// 手动接管时取消 move_base 当前目标
		cancel_pub_.publish(empty_goal_);
	}
	else
	{
		// 松开使能键时，只在上一帧处于运动状态的情况下发送一次零速度停车
		if(b_flag)
		{
			twist.linear.x = 0;
		    twist.linear.y = 0;
		    twist.linear.z = 0;
		    
		    twist.angular.x = 0;
		    twist.angular.y = 0;
		    twist.angular.z = 0;
			pub.publish(twist);
			b_flag = false;
		}
	}

	

}

int main(int argc,char** argv)
{
    // 初始化 ROS 节点并进入循环等待手柄消息
    ros::init(argc, argv, "logitech_teleop_node");    
    LogTeleop  logteleop;
    ros::spin();
    return 0;
}
