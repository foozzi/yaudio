import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QWidget, QInputDialog, 
	QLineEdit, QFrame)
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer, Qt
from requests import get
from pathlib import Path
import html
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
		self.setWindowIcon(QtGui.QIcon('./img/Youtube.png'))
		self.ui = main.Ui_MainWindow()
		self.ui.setupUi(self)

		parser = configparser.ConfigParser()
		parser.read('config.cfg')

		self.vbox = QtWidgets.QVBoxLayout(self.ui.scrollAreaWidgetContents)

		self.ui.search_btn.clicked.connect(lambda: self._search_music(clear=True))
		self.ui.play_pause_btn.clicked.connect(self._pause)
		self.ui.stop_btn.clicked.connect(self._stop)

		self.len_title_text = parser['YAudio']['len_title_text']
		self.volume = parser['YAudio']['volume']

		self.defaultTime = "00:00:00"
		# next page youtube id
		self.n_page = None

		self.is_stop = True
		self.is_pause = False
		# current now play track id
		self.np = None

		# volume slider
		self.ui.verticalSlider.setValue(int(self.volume))
		self.ui.verticalSlider.setToolTip('Volume')
		self.ui.verticalSlider.valueChanged.connect(self.volumeChanged)
		self.ui.verticalSlider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
		self.ui.verticalSlider.setTickInterval(1)
		self.ui.label_2.setText('<img src="./img/volume.png" />')

		self.ui.horizontalSlider.sliderMoved.connect(self.changePosition)

		self.ui.play_pause_btn.setEnabled(False)
		self.ui.stop_btn.setEnabled(False)
		self.ui.horizontalSlider.setEnabled(False)

		# trigger for open about page from top menu
		self.ui.actionsd.triggered.connect(lambda: helpers.gui.open_about(self=self))

		# arr quene track for playing
		self.quene_tracks = []

		# arr button tracks
		self.button_tracks = []

		# last search keyword
		self.last_search_keyword = None

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
		if not keywords.strip():
			helpers.gui.error_modal('Enter the keywords for search', 'Search error')
			return

		# if next page
		next = False

		# if load more, not clean playlist
		if clear == True:			
			helpers.gui.clearLayout(self.vbox)			
		else:
			next = True
			helpers.gui.clearLayout(self.hbox_last_container)
			sep_next = QFrame()
			sep_next.setFrameShape(QFrame.HLine)
			sep_next.setFrameShadow(QFrame.Sunken)
			self.hbox_last_container.addWidget(sep_next)

		self.ui.search_btn.setEnabled(False)
		search_tracks = Search(self, keywords, next)

	def next_track(self):				
		self.get_next_button()
		for index, track in enumerate(self.quene_tracks):
			if self.np != track:
				continue
			try:				
				# @TODO change _get_nowplay_button to really now play button for new track							
				self._play(self.quene_tracks[index + 1], self._get_nowplay_button())			
			finally:
				return

	def get_next_button(self):
		for index, button in enumerate(self.button_tracks):
			if self._get_nowplay_button() != button:
				continue
			try:
				self._set_nowplay_button(self.button_tracks[index + 1])			
			finally:
				return

	def updateProgress(self, position, time, length):				
		if time > 1 and length == time:					
			self._stop()
			self.next_track()
			return

		self.ui.horizontalSlider.setValue(position*1000.0)
		m, s = divmod(int(time / 1000), 60)
		if s >= 1:
			# if not paused, not change icons 
			if not self.is_pause:
				helpers.gui.change_icon_button(self.ui.play_pause_btn, 'fa.pause')
			self.ui.play_pause_btn.setEnabled(True)
			self.ui.stop_btn.setEnabled(True)
			h, m = divmod(m, 60)
			con_time_human = "%02d:%02d:%02d" % (h, m, s)	
			self.ui.label.setText(con_time_human)		

	def add_tracks_from_search(self, title, id, length, last=False, new_search=False):
		# if not "load more"
		if new_search == True:
			self.quene_tracks = []
			self.button_tracks = []
		hbox_player = QtWidgets.QHBoxLayout()
		self.vbox.addLayout(hbox_player)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, 
			QtWidgets.QSizePolicy.Fixed)
		self.track_play_btn = QtWidgets.QPushButton()
		self.track_play_btn.setSizePolicy(sizePolicy)
		helpers.gui.change_icon_button(self.track_play_btn, 'fa.play')
		self.track_play_btn.clicked.connect(partial(self._play, id=id,
			widget=self.track_play_btn))
		title_cut = html.unescape(helpers.text.truncate(title, 
			int(self.len_title_text)).strip())
		self.label = QtWidgets.QLabel(title_cut)
		self.label.setToolTip(html.unescape(title))
		self.label_time_track = QtWidgets.QLabel(length)
		self.label_time_track.setToolTip(length)
		self.label_time_track.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		# add button to arr
		self.button_tracks.append(self.track_play_btn)
		self.quene_tracks.append(id)
		hbox_player.addWidget(self.track_play_btn)
		hbox_player.addWidget(self.label)
		hbox_player.addWidget(self.label_time_track)		

		if last == True:
			self.hbox_last_container = QtWidgets.QHBoxLayout()
			self.vbox.addLayout(self.hbox_last_container)
			self.loadmore_btn = QtWidgets.QPushButton("Load More")
			self.loadmore_btn.clicked.connect(lambda: self._search_music(clear=False))
			self.hbox_last_container.addWidget(self.loadmore_btn)


	def _set_nowplay_button(self, widget):
		self.nowPlaying = widget

	def _get_nowplay_button(self):
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
			helpers.gui.change_icon_button(self.ui.play_pause_btn, 'fa.play')
			self._stop()					

		self.ui.horizontalSlider.setEnabled(True)
		self.ui.horizontalSlider.setMaximum(1000)
		self.ui.play_pause_btn.setEnabled(False)
		self.ui.stop_btn.setEnabled(True)
		widget.setEnabled(False)
		widget.setFlat(True)		
		helpers.gui.change_icon_button(self.ui.play_pause_btn, spin=True)
		self._set_nowplay_button(widget)
		self._playback = Play(self, id)
		self.check_position_t = QTimer(self)
		self.check_position_t.timeout.connect(self._playback._get_position)
		self.check_position_t.setInterval(1000)
		self.check_position_t.start()

	def _pause(self):
		np_b = self._get_nowplay_button()
		if not self.is_stop and not self.is_pause:
			self._playback.pause()
			self.is_pause = True			
			helpers.gui.change_icon_button(np_b, 'fa.play')
			helpers.gui.change_icon_button(self.ui.play_pause_btn, 'fa.play')
		elif not self.is_stop and self.is_pause:
			self._playback.playback.unpause()
			self.is_pause = False
			helpers.gui.change_icon_button(np_b, 'fa.pause')
			helpers.gui.change_icon_button(self.ui.play_pause_btn, 'fa.pause')
			

	def _stop(self):
		np_b = self._get_nowplay_button()
		np_b.setEnabled(True)
		np_b.setFlat(False)
		helpers.gui.change_icon_button(self.ui.play_pause_btn, 'fa.play')
		self.ui.play_pause_btn.setEnabled(False)
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
		self.playback.play(self.cached(uri))
		if self.parent.is_stop == True:
			self.__del__()

	def cached(self, url, folder="cached", bin="binary"):
		import os
		if not os.path.exists(folder):
			os.makedirs(folder)
		path = folder + '/' + bin
		my_file = Path(path)
		if my_file.is_file():			
			os.remove(path)

		with open(path, "wb") as file:
			response = get(url)
			file.write(response.content)
		return path

	def pause(self):
		self.playback.pause()

	def set_volume(self, value):
		self.playback.player.audio_set_volume(value)

	def set_position(self, value):
		self.playback.player.set_position(value)

	def stop(self):
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
	sig = QtCore.pyqtSignal(str, str, str, bool, bool)

	def __init__(self, parent=None, *data):
		super(Search, self).__init__(parent)

		self.parent = parent
		self.sig.connect(self.parent.add_tracks_from_search)

		self.new_search = False		
		self.keyword = data[0]
		if self.parent.last_search_keyword != None \
			and self.parent.last_search_keyword != self.keyword:
			self.new_search = True
		self.parent.last_search_keyword = self.keyword
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
			self.sig.emit(_['title'], _['id'], _['length'], last, self.new_search)				

		self.parent.ui.search_btn.setEnabled(True)

app = QtWidgets.QApplication(sys.argv)

my_mainWindow = YAudio()
my_mainWindow.show()

sys.exit(app.exec_())