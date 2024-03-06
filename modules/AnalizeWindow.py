from PyQt6.QtWidgets import QWidget, QFileDialog

from PyQt6 import uic

class AnalizeWindow(QWidget):
    """ Класс отвечающий за инициализацию и работу окна анализа """
    def __init__(self, parent):
        super().__init__() 
        uic.loadUi('ui/analize_window.ui', self)
        self.parent = parent
        # self.move(self.parent.x()+740, self.parent.y()+75)
        self.show()
    
    def openAnalizeWindow(self):
        self.analize_window = AnalizeWindow(self)
