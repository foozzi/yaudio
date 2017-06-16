import vlc
import requests
from PyQt5 import QtCore

class Streamer():

	def __init__(self, *data):
		self.uri = data[0]


	def stop(self):
		self.player.stop()
		return

	def pause(self):
		pass

	def play(self):		
		r = requests.get(self.uri)
		if r.status_code == 200:			
			print('play')
			self.vlcInstance = vlc.Instance("--no-xlib --verbose 2")
			self.player = self.vlcInstance.media_player_new()

			self.player.set_mrl(self.uri)
			self.player.play()
		else:
			return