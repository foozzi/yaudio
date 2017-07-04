import vlc
from PyQt5 import QtCore

class Streamer():
	
	def __init__(self, *data):
		self.vlcInstance = vlc.Instance("--no-xlib")
		self.player = self.vlcInstance.media_player_new()
		self.volume = data[0]

	def stop(self):
		self.player.stop()

	def pause(self):
		self.player.pause()

	def unpause(self):
		self.player.play()

	def play(self, uri):
		m=self.vlcInstance.media_new(uri)
		
		self.player.set_media(m)
		self.player.audio_set_volume(int(self.volume))
		self.player.play()
