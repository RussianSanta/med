import cv2
from PyQt6.QtGui import QPixmap, QIcon

def openProcessingFrame(self):
    """ Открытие формы обработки изображения """
    if self.source is not None:
        self.processingLabel.setText('Обработка изображения')
        self.frameProcessing.show()
        self.verticalFrame.hide()
        self.binarizationSlider.setEnabled(False)
    else:
        self.frameProcessing.hide()
        self.processingLabel.setText('Изображение не выбрано!')
        self.processingLabel.setStyleSheet("color: red; background-color: #292929;")

def toggleProcessing(self):
    """ Включение/выключение обработки изображения """
    if self.source is not None:
        icon3 = QIcon()
        if self.toggleProcessingButton.isChecked():
            icon3.addPixmap(QPixmap("ui\\icons/on.png"), QIcon.Mode.Normal, QIcon.State.Off)
            self.childFrameProcessing.setEnabled(True)
        else:
            icon3.addPixmap(QPixmap("ui\\icons/off.png"), QIcon.Mode.Normal, QIcon.State.Off)
            self.childFrameProcessing.setEnabled(False)
            self.convertToGrayCheckBox.setChecked(False)
            self.binarizationCheckBox.setChecked(False)
        self.toggleProcessingButton.setIcon(icon3)
        processingOn(self)

def processingOn(self):
    if not self.threadOn:
        self.update_frame(self.transformedImage)

def processFrame(self, image):
    if self.toggleProcessingButton.isChecked():
        # в оттенки серого
        if self.convertToGrayCheckBox.isChecked() and not self.binarizationCheckBox.isChecked():
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # бинаризация
        if self.binarizationCheckBox.isChecked():
            self.binarizationSlider.setEnabled(True)
            threshold = self.binarizationSlider.value()
            self.binarizationValue.setText(str(threshold))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            ret, image = cv2.threshold(image, threshold, 255, 0)
        else:
            self.binarizationSlider.setEnabled(False)
    return image

def scalingFrame(self, image):
    """ Произвольное масштабирование """
    w_im = image.shape[1]
    h_im = image.shape[0]
    self.scaleFactor = self.scaleSlider.value()/100
    self.scaleValue.setText(str(self.scaleFactor))
    image = cv2.resize(image, (int(w_im*self.scaleFactor), int(h_im*self.scaleFactor)), interpolation = cv2.INTER_AREA)
    return image