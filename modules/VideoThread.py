from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition, QMutexLocker
import numpy as np
import cv2
import itertools
import sys
from datetime import datetime
import time
from PyQt6.QtCore import Qt, pyqtSlot, QSize


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    def_path = "C:/.My/Study/DM/task5/example_media/CameraRecords"

    def __init__(self, source=0, recordTime=0, path=def_path, fps=30, x1=0, x2=0, y1=0, y2=0):
        super().__init__()
        self.is_run = True
        self.is_paused = bool()  # Флаг для паузы
        self.mutex = QMutex()  # Блокировщик потока
        self.cond = QWaitCondition()  # Условие блокировки
        self.source = source
        if self.source == 0:
            self.delay = 1
        else:
            self.delay = 870 // fps
        self.recordTime = int(recordTime * 60)
        self.path = path
        self.x1 = int(x1)
        self.x2 = int(x2)
        self.y1 = int(y1)
        self.y2 = int(y2)

    def run(self):
        """Протекание видеопотока"""
        print("Video thread STARTED")
        self.is_run = True
        if self.source == 0 and self.recordTime > 0:
            print(f'Record for {self.recordTime} sec STARTED')
            self.fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        it = itertools.cycle(['|', '\b', '/', '\b', '—', '\b', '\\', '\b'])
        print('Playing ', end="")
        recordIsStarted = False
        self.frame = None
        while self.is_run:
            print(next(it), end='', flush=True)
            with QMutexLocker(self.mutex):
                while self.is_paused:
                    self.cond.wait(self.mutex)
                if self.frame is None:
                    self.capture = cv2.VideoCapture(self.source)
                    self.capture.set(3, 720)
                    self.capture.set(4, 1024)
                    self.capture.set(5, 30)
                    self.frame = "Крутим на репите, главное во время паузы не поймать этот фрейм"
                else:
                    ret, self.frame = self.capture.read()
                    if self.x1 != 0 or self.x2 != 0 or self.y1 != 0 or self.y2 != 0:
                        frame_re = self.frame[self.y1:self.y2, self.x1:self.x2]
                        self.frame = frame_re

                    # if self.frame is None: # завершение потока при окончании видеоролика
                    #     self.is_run = False
                    # fshape = self.originalImage.shape
                    if ret:
                        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                        self.change_pixmap_signal.emit(self.frame)
                        # запись в файл каждые recordTime минут
                        if self.source == 0:
                            if not recordIsStarted and self.recordTime > 0:
                                self.out1 = cv2.VideoWriter(
                                    self.path + f"/video{datetime.now().strftime('%Y-%m-%d__%H-%M-%S')}.avi",
                                    self.fourcc, 30, (640, 480))
                                start = time.time()
                                recordIsStarted = True
                            if recordIsStarted:
                                if (time.time() - start) <= self.recordTime:
                                    self.out1.write(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))
                                else:
                                    self.out1.release()
                                    print('\b' * 9 + 'Recorded successfully!')
                                    recordIsStarted = False
                        # задержка для корректной раскадровки
                        self.msleep(self.delay)
        if 'self.out1' in locals():
            self.out1.release()
        self.capture.release()
        self.close()
        print('\b' * 9 + 'Video thread CLOSED')

    def close(self):
        """Закрытие видеопотока"""
        self.is_run = False

    def pause(self):
        """Приостановка видеопотока"""
        with QMutexLocker(self.mutex):
            self.is_paused = True
            print('\b' * 9 + 'Video thread PAUSED')
            return self.frame

    def resume(self):
        """Возобновление видеопотока"""
        if not self.is_paused:
            return
        with QMutexLocker(self.mutex):
            self.is_paused = False
            self.cond.wakeOne()
            print('Video thread RESUMED')
            print('Playing  ', end="")

    @pyqtSlot()
    def toggle_video(self):
        if self.video_thread is None:
            return
        if self.threadOn:
            self.originalImage = self.video_thread.pause()
            self.transformedImage = self.originalImage
            self.playButton.setIcon(self.playIcon)
            self.threadOn = False
        else:
            self.isOriginal = True
            self.video_thread.resume()
            self.playButton.setIcon(self.pauseIcon)
            self.threadOn = True
