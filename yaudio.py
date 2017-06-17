import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QMessageBox, QFrame
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer
import os
# template main
import main
import helpers.search
from streamer import Streamer
from functools import partial
import qtawesome as qta

class YAudio(QtWidgets.QMainWindow):
	def __init__(self):
		super(YAudio,self).__init__()
		self.ui = main.Ui_MainWindow()
		self.ui.setupUi(self)

		self.vbox = QtWidgets.QVBoxLayout(self.ui.scrollAreaWidgetContents)

		self.ui.pushButton_3.clicked.connect(partial(self._search_music, clear=True))
		self.ui.pushButton.clicked.connect(self._stop)

		self.defaultTime = "00:00:00"
		self.n_page = None

		self.is_stop = True

		self.ui.pushButton_2.setEnabled(False)
		self.ui.pushButton.setEnabled(False)
		self.ui.horizontalSlider.setEnabled(False)

	def _search_music(self, clear=True):
		keywords = self.ui.lineEdit.text()
		if len(keywords) < 1:
			self.error_modal('Enter the keywords for search', 'Search error')
			return

		# if next page
		next = False

		# if load more, not clean playlist
		if clear == True:
			self.clearLayout(self.vbox)			
		else:
			next = True
			self.clearLayout(self.hbox_last_container)
			sep_next = QFrame()
			sep_next.setFrameShape(QFrame.HLine)
			sep_next.setFrameShadow(QFrame.Sunken)
			self.hbox_last_container.addWidget(sep_next)

		self.ui.pushButton_3.setEnabled(False)
		search_tracks = Search(self, keywords, next)

	def updateProgress(self, proc, full):
		self.ui.horizontalSlider.setEnabled(True)
		self.ui.horizontalSlider.setMaximum(int(full/1000))
		self.ui.horizontalSlider.setValue(int(proc/1000))
		m, s = divmod(int(proc / 1000), 60)
		if s >= 1:
			np_btn = self._get_np_button()
			np_btn.setEnabled(True)
			self.change_icon_button(self.ui.pushButton_2, qta.icon('fa.pause'))
			self.change_icon_button(np_btn, qta.icon('fa.pause'))
			self.ui.pushButton_2.setEnabled(True)
			self.ui.pushButton.setEnabled(True)
		h, m = divmod(m, 60)
		con_time_human = "%02d:%02d:%02d" % (h, m, s)
		self.ui.label.setText(con_time_human)

	def error_modal(self, message, title):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Information)
		msg.setText(message)
		msg.setWindowTitle(title)
		msg.exec_()

	def add_tracks_from_search(self, title, id, last=False):
		hbox_player = QtWidgets.QHBoxLayout()
		self.vbox.addLayout(hbox_player)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		self.pushButton_4 = QtWidgets.QPushButton()
		self.pushButton_4.setSizePolicy(sizePolicy)
		self.pushButton_4.setIcon(qta.icon('fa.play'))
		self.pushButton_4.setIconSize(QtCore.QSize(24, 24))		
		self.pushButton_4.clicked.connect(partial(self._play, id=id, widget=self.pushButton_4))
		self.label = QtWidgets.QLabel(title)
		hbox_player.addWidget(self.pushButton_4)
		hbox_player.addWidget(self.label)
		if last == True:
			self.hbox_last_container = QtWidgets.QHBoxLayout()
			self.vbox.addLayout(self.hbox_last_container)
			self.pushButton_loadMore = QtWidgets.QPushButton("Load More")
			self.pushButton_loadMore.clicked.connect(
				partial(self._search_music, clear=False))
			self.hbox_last_container.addWidget(self.pushButton_loadMore)


	def clearLayout(self, layout):
		if layout != None:
			while layout.count():
				child = layout.takeAt(0)
				if child.widget() is not None:
					child.widget().deleteLater()
				elif child.layout() is not None:
					self.clearLayout(child.layout())

	def _set_np_button(self, widget):
		self.nowPlaying = widget

	def _get_np_button(self):
		if hasattr(self, 'nowPlaying'):
			return self.nowPlaying
		return None

	def _play(self, id, widget):
		if self.is_stop == False:
			self._stop()
		self.ui.pushButton_2.setEnabled(False)
		self.ui.pushButton.setEnabled(True)
		widget.setEnabled(False)
		self.change_icon_button(self.ui.pushButton_2, spin=True)
		self.change_icon_button(widget, spin=True)
		self._set_np_button(widget)
		self._playback = Play(self, id)
		self.check_position_t = QTimer(self)
		self.check_position_t.timeout.connect(self._playback._get_position)
		self.check_position_t.setInterval(1000)
		self.check_position_t.start()

	def _pause(self):
		if not self.is_stop:
			pass
			

	def _stop(self):
		np_b = self._get_np_button()
		np_b.setEnabled(True)
		self.change_icon_button(self.ui.pushButton_2, qta.icon('fa.play'))
		self.change_icon_button(np_b, qta.icon('fa.play'))
		self.ui.horizontalSlider.setValue(0)
		self.ui.label.setText(self.defaultTime)
		self.is_stop = True
		self.check_position_t.stop()
		self._playback.stop()
		# self._playback.terminate()
		return

	def change_icon_button(self, widget, icon=None, spin=False):
		if spin == True:
			icon = qta.icon('fa.spinner',
				animation=qta.Spin(widget))
		widget.setIcon(icon)
		widget.setIconSize(QtCore.QSize(24, 24))

class Play(QtCore.QThread):	
	sig = QtCore.pyqtSignal(int, int)

	def __init__(self, parent=None, *data):
		super(Play, self).__init__(parent)	

		self.parent = parent
		self.id = data[0]		

		self.parent.is_stop = False

		self.sig.connect(self.parent.updateProgress)
		self.playback = Streamer()
		self.start()

	def run(self):				
		uri = helpers.search.get_youtube_streams(self.id)
		self.playback.play(uri['audio'])

	def stop(self):
		self.playback.stop()
		self.terminate()
		return

	def _get_position(self):
		length = self.playback.player.get_time()
		full_length = self.playback.player.get_length()
		self.sig.emit(length, full_length)
			

class Search(QtCore.QThread):
	sig = QtCore.pyqtSignal(str, str, bool)

	def __init__(self, parent=None, *data):
		super(Search, self).__init__(parent)

		self.parent = parent
		self.sig.connect(self.parent.add_tracks_from_search)

		self.keyword = data[0]
		self.next = data[1]
		self.start()

	def run(self):
		raw_html = helpers.search.get_search_results_html(
			self.keyword, False if not self.next else self.parent.n_page)		
		vids, self.parent.n_page = helpers.search.get_videos(raw_html)				
		# flag for last track
		last = False
		
		
		i = 0
		clear_vids = []
		# ...fix lol
		for _ in vids:						
			attrs = helpers.search.get_video_attrs(_)				
			if attrs != None:
				clear_vids.append(attrs)
		
		len_vids = len(clear_vids)
		for _ in clear_vids:
			i = i + 1
			if i == len_vids:
				last = True	
			self.sig.emit(_['title'], _['id'], last)				

		self.parent.ui.pushButton_3.setEnabled(True)

	def __del__(self):
		self.exiting = True
		self.wait()

app = QtWidgets.QApplication(sys.argv)

my_mainWindow = YAudio()
my_mainWindow.show()

sys.exit(app.exec_())