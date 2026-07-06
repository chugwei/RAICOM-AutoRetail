from pymycobot.mycobot import MyCobot
import threading
from multiprocessing import Process
import os, time

def teleop_node():
    os.system(
        "python /home/robuster/czc_robuster/2/main.py  --debug ''"
    )

t = threading.Thread(target=teleop_node,name='teleop_node')
t.setDaemon(True)
t.start()