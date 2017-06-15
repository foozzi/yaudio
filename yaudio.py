import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QMessageBox
from PyQt5 import QtCore, QtGui
import os
# template main
import main
import helpers.search
from streamer import Streamer
from functools import partial

class YAudio(QtWidgets.QMainWindow):
	def __init__(self):
		super(YAudio,self).__init__()
		self.ui = main.Ui_MainWindow()
		self.ui.setupUi(self)

		self.vbox = QtWidgets.QVBoxLayout(self.ui.scrollAreaWidgetContents)

		self.ui.pushButton_3.clicked.connect(self._search_music)
		self.ui.pushButton.clicked.connect(self._stop)

	def _search_music(self):
		keywords = self.ui.lineEdit.text()
		if len(keywords) < 1:
			self.error_modal('Enter the keywords for search', 'Search error')
			return

		self.clearLayout(self.vbox)

		self.ui.pushButton_3.setEnabled(False)
		search_tracks = Search(self, keywords)

	def updateProgress(self, proc):
		pass

	def error_modal(self, message, title):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Information)
		msg.setText(message)
		msg.setWindowTitle(title)
		msg.exec_()

	def add_tracks_from_search(self, title, id):
		hbox_player = QtWidgets.QHBoxLayout()
		self.vbox.addLayout(hbox_player)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		self.pushButton_4 = QtWidgets.QPushButton()
		self.pushButton_4.setSizePolicy(sizePolicy)
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap("../Загрузки/play-button.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
		self.pushButton_4.setIcon(icon)
		self.pushButton_4.setIconSize(QtCore.QSize(24, 24))
		self.pushButton_4.clicked.connect(partial(self._play, id=id))
		self.label = QtWidgets.QLabel(title)
		hbox_player.addWidget(self.pushButton_4)
		hbox_player.addWidget(self.label)

	def clearLayout(self, layout):
		if layout != None:
			while layout.count():
				child = layout.takeAt(0)
				if child.widget() is not None:
					child.widget().deleteLater()
				elif child.layout() is not None:
					self.clearLayout(child.layout())

	def _play(self, id):
		print(id)
		self._playback = Play(self, id)

	def _stop(self):
		pass

class Play(QtCore.QThread):
	sig = QtCore.pyqtSignal(int)
	
	def __init__(self, parent=None, *data):
		super(Play, self).__init__(parent)	

		self.parent = parent
		self.id = data[0]
		self.sig.connect(self.parent.updateProgress)
		

		self.start()

	def run(self):
		uri = helpers.search.get_youtube_streams(self.id)
		self.playback = Streamer(uri['audio'])
		self.playback.play()

class Search(QtCore.QThread):
	sig = QtCore.pyqtSignal(str, str)

	def __init__(self, parent=None, *data):
		super(Search, self).__init__(parent)

		self.parent = parent
		self.sig.connect(self.parent.add_tracks_from_search)

		self.keyword = data[0]
		self.start()

	def run(self):
		raw_html = helpers.search.get_search_results_html(self.keyword)		
		vids = helpers.search.get_videos(raw_html)				
		
		for _ in vids:				
			attrs = helpers.search.get_video_attrs(_)	
			if attrs != None:				
				self.sig.emit(attrs['title'], attrs['id'])
		
		self.parent.ui.pushButton_3.setEnabled(True)

	def __del__(self):
		self.exiting = True
		self.wait()

app = QtWidgets.QApplication(sys.argv)

my_mainWindow = YAudio()
my_mainWindow.show()

sys.exit(app.exec_())