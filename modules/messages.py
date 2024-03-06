from PyQt6 import QtWidgets

def get_msg_result(title: str, question: str):
    """Создание вопросительного диалогового окна"""
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle(title)
    msg.setIcon(QtWidgets.QMessageBox.Icon.Question)
    msg.setText(question)
    msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
    return msg.exec() == QtWidgets.QMessageBox.StandardButton.Yes
