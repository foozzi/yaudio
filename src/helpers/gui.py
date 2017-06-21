from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QDialog
import qtawesome as qta

import about

''' about dialog '''
class About(QtWidgets.QDialog) :
	def __init__(self, parent):
		super(About, self).__init__(parent)
		self.ui = about.Ui_Form()
		self.ui.setupUi(self)

def error_modal(message, title):
	msg = QMessageBox()
	msg.setIcon(QMessageBox.Information)
	msg.setText(message)
	msg.setWindowTitle(title)
	msg.exec_()

def open_about(self):
	about_ = About(self)
	about_.exec()

def clearLayout(layout):
	if layout != None:
		while layout.count():
			child = layout.takeAt(0)
			if child.widget() is not None:
				child.widget().deleteLater()
			elif child.layout() is not None:
				clearLayout(child.layout())

def change_icon_button(widget, icon_str=None, spin=False):
	if spin == True:
		icon = qta.icon('fa.spinner',
		animation=qta.Spin(widget))
	else :
		icon = qta.icon(icon_str)
	widget.setIcon(icon)
	widget.setIconSize(QtCore.QSize(24, 24))