# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.6 (main, Mar 10 2023, 10:55:28) [GCC 11.3.0]
# Embedded file name: /home/robuster/beetle_ai/scripts/VideoCapture.py
# Compiled at: 2022-06-27 20:47:35
import cv2, Queue, threading, time
from GrabParams import grabParams
import os

class FastVideoCapture(object):

    # 多线程视频捕获初始化
    def __init__(self, num):
        print('FastVideoCapture __init__: ')
        self.done = False
        self.cap = cv2.VideoCapture("/dev/armvideo") # , cv2.CAP_V4L2
        self.q = Queue.Queue()
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()
        self.__init_flag = True

    # 独立的帧读取线程
    def _reader(self):
        while not self.done:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()
                except Queue.Empty:
                    pass

            self.q.put(frame)

    # 获取最新帧
    def read(self):
        frame = self.q.get()
        if frame is None:
            return None  # 返回 None 以指示没有更多的帧
        return frame

    def getHeight(self):
        return self.cap.get(4)

    def getWidth(self):
        return self.cap.get(3)

    def close(self):
        self.done = True
    
    def close_image(self):
        self.cap.release()
        cv2.destroyAllWindows()
    
    def end_read(self):
        self.q.put(None)

    def release(self):
        # cv2.VideoCapture.release()
        self.cap.release()