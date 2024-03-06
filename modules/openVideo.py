from PyQt6.QtWidgets import QFileDialog
from modules.VideoThread import VideoThread
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (QLabel, QComboBox)
from modules.meta import (addMeta)


def openVideo(self):
    """Открытие видеофайла"""
    self.closePreviousThread()
    self.source, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', '', 
                                                'Images (*.mp4 *.avi *.mov *.mkv)')
    if self.source != "":
        print(f"Video {self.source.split('/')[-1]} OPENED")
        try:
            self.isChanged = True
            self.isOriginal = True
            self.video_thread = VideoThread(self.source, 0)  # если 0, то вебкамера, иначе по пути
            self.video_thread.change_pixmap_signal.connect(self.update_frame)
            self.video_thread.start()
            self.threadOn = True
            # ui
            self.playButton.setEnabled(True)
            self.playButton.setIcon(self.pauseIcon)
            self.sourceLabel.setText(f"файл {self.source.split('/')[-1]}")
            self.sourcePathLabel.setText("из папки " + '/'.join(self.source.split('/')[-2:-1]))
            self.processingLabel.setText('Обработка изображения')
            self.processingLabel.setStyleSheet("color: white; background-color: #292929")
            # Мета кнопки
            addMeta(self)

        except Exception as e:
            print(e)
