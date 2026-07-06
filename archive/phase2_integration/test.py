from GrabParams import grabParams

import time
from pymycobot.mycobot import MyCobot
from pymycobot.genre import Angle

mc = MyCobot(grabParams.usb_dev, grabParams.baudrate)
mc.power_on()


mc.release_all_servos()

mc.focus_servo(1)
mc.focus_servo(2)
mc.focus_servo(3)
mc.focus_servo(4)
mc.focus_servo(5)
mc.focus_servo(6)
time.sleep(1)
print("coords:", mc.get_coords())
print("angles:", mc.get_angles())
# # mc.send_angles([0,0,0,0,0,0],30)

# print(grabParams.coords_ready[1] - 18)
# print(grabParams.coords_ready[2] - 90)