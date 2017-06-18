import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QWidget, QInputDialog, 
	QLineEdit, QFrame)
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer, Qt
from functools import partial
# template main
import main
# helpers
import helpers.search
import helpers.text
import helpers.gui
# player wrapper
from streamer import Streamer
import configparser


class YAudio(QtWidgets.QMainWindow):
	def __init__(self):
		super(YAudio,self).__init__()
		self.ui = main.Ui_MainWindow()
		self.ui.setupUi(self)

		parser = configparser.ConfigParser()
		parser.read('config.cfg')

		self.vbox = QtWidgets.QVBoxLayout(self.ui.scrollAreaWidgetContents)

		self.ui.pushButton_3.clicked.connect(partial(self._search_music, clear=True))
		self.ui.pushButton_2.clicked.connect(self._pause)
		self.ui.pushButton.clicked.connect(self._stop)

		self.len_title_text = parser['YAudio']['len_title_text']
		self.volume = parser['YAudio']['volume']

		self.defaultTime = "00:00:00"
		self.n_page = None

		self.is_stop = True
		self.is_pause = False
		self.np = None

		self.ui.verticalSlider.setValue(int(self.volume))
		self.ui.verticalSlider.setToolTip('Volume')
		self.ui.verticalSlider.valueChanged.connect(self.volumeChanged)
		self.ui.verticalSlider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
		self.ui.verticalSlider.setTickInterval(1)
		self.ui.label_2.setText('<img src="./img/volume.png" />')

		self.ui.horizontalSlider.sliderMoved.connect(self.changePosition)

		self.ui.pushButton_2.setEnabled(False)
		self.ui.pushButton.setEnabled(False)
		self.ui.horizontalSlider.setEnabled(False)

		self.ui.actionsd.triggered.connect(partial(helpers.gui.open_about, self=self))

		self.quene_tracks = []

	def changePosition(self, value):
		if not self.is_stop:
			self.check_position_t.stop()
			self._playback.set_position(value / 1000.0)
			self.check_position_t.start()

	def volumeChanged(self, value):
		self.volume = value
		if self.volume <= 1:
			self.ui.label_2.setText('<img src="./img/novolume.png" />')
		elif self.volume > 1:
			self.ui.label_2.setText('<img src="./img/volume.png" />')
		if not self.is_stop:			
			self._playback.set_volume(self.volume)

	def keyPressEvent(self, e):		
		if e.key() == Qt.Key_Escape:
			self.close()
		elif e.key() == Qt.Key_Return and self.ui.lineEdit.hasFocus():
			self._search_music()

	def _search_music(self, clear=True):
		keywords = self.ui.lineEdit.text()
		if len(keywords) < 1:
			helpers.gui.error_modal('Enter the keywords for search', 'Search error')
			return

		# if next page
		next = False

		# if load more, not clean playlist
		if clear == True:
			# clear icon from the current track,
			# couse that call error update animateion
			np_b = self._get_np_button()
			if np_b:
				np_b.setIcon(QtGui.QIcon())
			helpers.gui.clearLayout(self.vbox)			
		else:
			next = True
			helpers.gui.clearLayout(self.hbox_last_container)
			sep_next = QFrame()
			sep_next.setFrameShape(QFrame.HLine)
			sep_next.setFrameShadow(QFrame.Sunken)
			self.hbox_last_container.addWidget(sep_next)

		self.ui.pushButton_3.setEnabled(False)
		search_tracks = Search(self, keywords, next)

	def next_track(self):		
		if self.np in self.quene_tracks:
			i = 0
			for _ in self.quene_tracks:
				if self.np == _:
					try:
						# self.np = self.quene_tracks[i+1]										
						self._play(self.quene_tracks[i+1], self._get_np_button())
						return
					except Exception as e:
						return					
				i = i + 1

	def updateProgress(self, position, time, length):				
		if time > 1 and length == time:
			self._stop(terminate=False)
			self.next_track()

		self.ui.horizontalSlider.setValue(position*1000.0)
		m, s = divmod(int(time / 1000), 60)
		if s >= 1:
			# if not paused, not change icons 
			if not self.is_pause:
				helpers.gui.change_icon_button(self.ui.pushButton_2, 'fa.pause')
			self.ui.pushButton_2.setEnabled(True)
			self.ui.pushButton.setEnabled(True)
		h, m = divmod(m, 60)
		con_time_human = "%02d:%02d:%02d" % (h, m, s)		
		self.ui.label.setText(con_time_human)

	def add_tracks_from_search(self, title, id, last=False):
		hbox_player = QtWidgets.QHBoxLayout()
		self.vbox.addLayout(hbox_player)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, 
			QtWidgets.QSizePolicy.Fixed)
		self.pushButton_4 = QtWidgets.QPushButton()
		self.pushButton_4.setSizePolicy(sizePolicy)
		helpers.gui.change_icon_button(self.pushButton_4, 'fa.play')
		self.pushButton_4.clicked.connect(partial(self._play, id=id, 
			widget=self.pushButton_4))
		title_cut = helpers.text.truncate(title, int(self.len_title_text)).strip()
		self.label = QtWidgets.QLabel(title_cut)
		self.label.setToolTip(title)
		hbox_player.addWidget(self.pushButton_4)
		hbox_player.addWidget(self.label)
		self.quene_tracks.append(id)

		print(self.quene_tracks)

		if last == True:
			self.hbox_last_container = QtWidgets.QHBoxLayout()
			self.vbox.addLayout(self.hbox_last_container)
			self.pushButton_loadMore = QtWidgets.QPushButton("Load More")
			self.pushButton_loadMore.clicked.connect(
				partial(self._search_music, clear=False))
			self.hbox_last_container.addWidget(self.pushButton_loadMore)


	def _set_np_button(self, widget):
		self.nowPlaying = widget

	def _get_np_button(self):
		if hasattr(self, 'nowPlaying'):
			return self.nowPlaying
		return None

	def _play(self, id, widget):		
		# check if track active
		if id == self.np:
			self._pause()
			return		
		self.is_pause = False
		self.np = id		
		if self.is_stop == False:
			self._stop()		

		self.ui.horizontalSlider.setEnabled(True)
		self.ui.horizontalSlider.setMaximum(1000)
		self.ui.pushButton_2.setEnabled(False)
		self.ui.pushButton.setEnabled(True)
		widget.setEnabled(False)
		widget.setFlat(True)
		helpers.gui.change_icon_button(self.ui.pushButton_2, spin=True)
		self._set_np_button(widget)
		self._playback = Play(self, id)
		self.check_position_t = QTimer(self)
		self.check_position_t.timeout.connect(self._playback._get_position)
		self.check_position_t.setInterval(1000)
		self.check_position_t.start()

	def _pause(self):
		np_b = self._get_np_button()
		if not self.is_stop and not self.is_pause:
			self._playback.pause()
			self.is_pause = True			
			helpers.gui.change_icon_button(np_b, 'fa.play')
			helpers.gui.change_icon_button(self.ui.pushButton_2, 'fa.play')
		elif not self.is_stop and self.is_pause:
			self._playback.playback.unpause()
			self.is_pause = False
			helpers.gui.change_icon_button(np_b, 'fa.pause')
			helpers.gui.change_icon_button(self.ui.pushButton_2, 'fa.pause')
			

	def _stop(self, terminate=True):
		try:
			np_b = self._get_np_button()
			np_b.setEnabled(True)
			np_b.setFlat(False)
		except Exception as e:
			pass
	
		helpers.gui.change_icon_button(self.ui.pushButton_2, 'fa.play')
		self.ui.pushButton_2.setEnabled(False)
		self.ui.horizontalSlider.setValue(0)
		self.ui.label.setText(self.defaultTime)
		self.is_stop = True
		self.check_position_t.stop()
		self._playback.stop()


class Play(QtCore.QThread):	
	sig = QtCore.pyqtSignal(float, int, int)

	def __init__(self, parent=None, *data):
		super(Play, self).__init__(parent)	

		self.parent = parent
		self.id = data[0]		

		self.parent.is_stop = False

		self.sig.connect(self.parent.updateProgress)
		self.playback = Streamer(self.parent.volume)
		self.start()

	def run(self):						
		uri = helpers.search.get_youtube_streams(self.id)
		self.playback.play(uri)
		if self.parent.is_stop == True:
			self.__del__()

	def pause(self):
		self.playback.pause()

	def set_volume(self, value):
		self.playback.player.audio_set_volume(value)

	def set_position(self, value):
		self.playback.player.set_position(value)

	def stop(self, terminate=True):
		self.playback.stop()		
		return

	def _get_position(self):
		position = self.playback.player.get_position()
		time = self.playback.player.get_time()
		length = self.playback.player.get_length()
		self.sig.emit(position, time, length)

	def __del__(self):
		self.quit()
		self.wait()
			

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

app = QtWidgets.QApplication(sys.argv)

my_mainWindow = YAudio()
my_mainWindow.show()

sys.exit(app.exec_())