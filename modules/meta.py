from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import (QPushButton, QLabel, QComboBox)
import cv2

from modules.VideoThread import VideoThread


def addMeta(self):
    """ Добавление/изменение мета поля """
    removeMetaButtons(self)
    name = "Исходный видеопоток"
    if self.isMetaButtons:
        buttonName = f'metaButton-{name}'
        addMetaButton(self, name)
        self.metaButtons[buttonName].clicked.connect(lambda: setOriginalSource(self))
        loadMetaFromPrevData(self)
    if self.isMetaComboBox:
        print('ComboBox generated')
        buttonName = f'metaButton-{name}'
        self.metaLabel = QLabel(parent=self.metaFrame)
        self.metaLabel.setMinimumSize(QSize(0, 20))
        self.metaLabel.setObjectName("metaLabel")
        self.metaLabel.setText(name)
        self.meta.addWidget(self.metaLabel)
        self.metaComboBox = QComboBox(parent=self.metaFrame)
        self.metaComboBox.setMinimumSize(QSize(0, 20))
        self.metaComboBox.setObjectName("metaComboBox")
        
        addMetaComboBoxItems(self, name)
        self.metaComboBox.currentTextChanged.connect(lambda: setOriginalSource(self))
        loadMetaFromPrevData(self)

        self.meta.addWidget(self.metaComboBox)
        self.meta.setStretch(0, 1)


def addMetaButton(self, name):
    """ Добавление кнопки в конец метаполя """
    if self.isMetaButtons:
        buttonName = f'metaButton-{name}'
        self.metaButtons[buttonName] = QPushButton(parent=self.centralwidget)
        self.metaButtons[buttonName].setEnabled(True)
        self.metaButtons[buttonName].setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.metaButtons[buttonName].setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.metaButtons[buttonName].setFlat(False)
        self.metaButtons[buttonName].setObjectName(buttonName)
        self.metaButtons[buttonName].setText(name)
        if self.video_thread is None:
            self.metaButtons[buttonName].clicked.connect(lambda: metaClickAction(self, name))
        else:
            self.metaButtons[buttonName].clicked.connect(lambda: self.pauseThread(name))
        self.meta.addWidget(self.metaButtons[buttonName])


def addMetaComboBoxItems(self, name):
    """ Добавление строки в metaComboBox """
    if self.isMetaComboBox:
        self.metaComboBox.addItem(name)
        if self.video_thread is None:
            self.metaComboBox.currentTextChanged.connect(metaClickAction)
        else:
            self.metaComboBox.currentTextChanged.connect(self.pauseThread)

def removeMetaButtons(self, name=''):
    """ Удаление конкретной кнопки или всех """
    if name == '': # очистка meta
        for button in self.metaButtons.values():
            try: button.clicked.disconnect() 
            except Exception: pass
            self.meta.removeWidget(button)
        self.metaButtons.clear()
        try: 
            self.metaComboBox.currentTextChanged.disconnect()
            self.metaComboBox.clear()
            self.meta.removeWidget(self.metaComboBox)
            self.meta.removeWidget(self.metaLabel)
        except Exception: pass
    else: # удаление конкретной кнопки
        if self.isMetaButtons:
            name = f"metaButton-{name}"
            button = self.metaButtons.pop(name)
            try: button.clicked.disconnect() 
            except Exception: pass
            self.meta.removeWidget(button)
        if self.isMetaComboBox: 
            index = self.metaComboBox.findText(name)  # find the index of text
            self.metaComboBox.removeItem(index)

def metaClickAction(self, name):
    """ Поведение метакнопок """
    self.currentImageLabel.setText(name)
    self.isOriginal = False
    if self.video_thread is not None:
        self.video_thread.pause()
        self.playButton.setDisabled(True)
        self.threadOn = False
    if self.cut_video_thread is not None:
        self.cut_video_thread.pause()
    if self.isMetaComboBox:
        self.metaLabel.setText(name)
        if self.metaComboBox.currentIndex() == 0:
            self.isOriginal = True
            self.playButton.setDisabled(False)
    for box in self.boxes[self.source]:
        if box.name == name:
            self.cut_video_thread = VideoThread(self.source, 0, x1=box.x1, x2=box.x2, y1=box.y1, y2=box.y2)
            self.cut_video_thread.change_pixmap_signal.connect(self.update_frame)
            self.cut_video_thread.start()

def loadMetaFromPrevData(self):
    """ Обновление meta из ранее сохраненных данных """
    if self.source in self.boxes:
        for box in self.boxes[self.source]:
            if self.isMetaButtons:
                addMetaButton(self, box.name)
            if self.isMetaComboBox:
                addMetaComboBoxItems(self, box.name)

def setOriginalSource(self):
    """ Установка оригинального изображения """
    self.isOriginal = True
    self.transformedImage = self.originalImage
    if self.video_thread is not None:
        self.playButton.setDisabled(False)
    self.update_frame(self.transformedImage)

def fitFrameToWindow(self, image):
    """ Вписывание вырезанной области в окно показа """
    w = self.graphicsView.width()
    h = self.graphicsView.height()
    w_im = image.shape[1]
    h_im = image.shape[0]
    if w/w_im < h/h_im:
        factor = w/w_im
    else:
        factor = h/h_im
    image = cv2.resize(image, (int(w_im*factor)-2, int(h_im*factor)-2), interpolation = cv2.INTER_AREA)
    return image
