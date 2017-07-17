# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import configparser

class Ui_Form(object):
	def setupUi(self, Form):
		Form.setObjectName("Form")
		Form.resize(249, 286)
		self.verticalLayout = QtWidgets.QVBoxLayout(Form)
		self.verticalLayout.setObjectName("verticalLayout")
		self.label_2 = QtWidgets.QLabel(Form)
		self.label_2.setAlignment(QtCore.Qt.AlignCenter)
		self.label_2.setObjectName("label_2")
		self.verticalLayout.addWidget(self.label_2)
		self.label = QtWidgets.QLabel(Form)
		self.label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
		self.label.setObjectName("label")
		self.verticalLayout.addWidget(self.label)

		self.retranslateUi(Form)
		QtCore.QMetaObject.connectSlotsByName(Form)

	def retranslateUi(self, Form):
		parser = configparser.ConfigParser()
		parser.read('config.cfg')

		_translate = QtCore.QCoreApplication.translate
		Form.setWindowTitle(_translate("Form", "About"))
		self.label_2.setText(_translate("Form", "<html><head/><body><p><img src=\"./img/Youtube-about.png\"/></p></body></html>"))
		self.label.setText(_translate("Form", "<html><head/><body><p><span style=\" font-weight:600;\">YAudio</span> (v. "+parser['YAudio']['version']+")</p><p>Audio player for youtube streaming with </p><p>search by keywords</p><p>Home page: <a href=\"https://github.com/foozzi/yaudio\"><span style=\" text-decoration: underline; color:#0000ff;\">https://github.com/foozzi/yaudio</span></a></p><p>Author: Igor Tkachenko</p><p>Twitter: <a href=\"https://twitter.com/foozzi\"><span style=\" text-decoration: underline; color:#0000ff;\">https://twitter.com/foozzi</span></a></p></body></html>"))

