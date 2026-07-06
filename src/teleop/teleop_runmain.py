from pymycobot.mycobot import MyCobot
import threading
from multiprocessing import Process
import os, time

def teleop_runmain():
    os.system(
        "python /home/robuster/czc_robuster/3/code_left/main.py"
    )

t = threading.Thread(target=teleop_runmain,name='teleop_runmain')
t.setDaemon(True)
t.start()