from pymycobot.mycobot import MyCobot
import threading
from multiprocessing import Process
import os, time

def teleop_loadmap():
    os.system(
        "roslaunch robuster_mr_navigation navigation.launch"
    )

t = threading.Thread(target=teleop_loadmap,name='teleop_loadmap')
t.setDaemon(True)
t.start()
