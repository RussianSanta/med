from modules.VideoThread import VideoThread
import time
from modules.meta import (addMeta)

def openCamera(self):
    """Открытие вебкамеры"""
    self.isChanged = True
    self.isOriginal = True
    self.closePreviousThread()
    time.sleep(2)
    self.source = 0
    print(f"Camera {self.source} OPENED")
    self.video_thread = VideoThread(self.source, self.recordTime, self.cameraRecordsSavePath)  # если 0, то вебкамера, иначе по пути
    self.video_thread.change_pixmap_signal.connect(self.update_frame)
    self.video_thread.start()
    self.threadOn = True
    # UI
    self.playButton.setEnabled(True)
    self.playButton.setIcon(self.pauseIcon)
    self.sourceLabel.setText("с веб-камеры")
    self.sourcePathLabel.setText("")
    self.processingLabel.setText('Обработка изображения')
    self.processingLabel.setStyleSheet("color: white; background-color: #292929")
    # Мета кнопки
    addMeta(self)

