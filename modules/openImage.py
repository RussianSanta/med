from PyQt6.QtWidgets import QFileDialog
import cv2
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (QLabel, QComboBox)
from modules.meta import (addMeta)

def openImage(self):
    """Открытие изображения"""
    self.closePreviousThread()
    print(self.isMetaButtons)
    self.source, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Image files (*.jpeg *.jpg *.png)")
    if self.source != "":
        print(f"Image {self.source.split('/')[-1]} OPENED")
        self.isChanged = True
        self.isOriginal = True
        self.video_thread = None
        self.playButton.setDisabled(True)
        self.playButton.setIcon(self.playIcon)
        # self.originalImage = Image.open(self.source)
        self.originalImage = cv2.imread(self.source) # cv
        self.originalImage = cv2.cvtColor(self.originalImage, cv2.COLOR_BGR2RGB)
        self.transformedImage = self.originalImage
        self.update_frame(self.transformedImage)
        # UI
        self.sourceLabel.setText(f"файл {self.source.split('/')[-1]}")
        self.sourcePathLabel.setText("из папки " + '/'.join(self.source.split('/')[-2:-1]))
        self.processingLabel.setText('Обработка изображения')
        self.processingLabel.setStyleSheet("color: white; background-color: #292929")
        # Мета кнопки
        addMeta(self)
