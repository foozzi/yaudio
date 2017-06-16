import vlc
import requests
from PyQt5 import QtCore

class Streamer():

	def __init__(self, *data):
		self.vlcInstance = vlc.Instance("--no-xlib --verbose 2")
		self.player = self.vlcInstance.media_player_new()


	def stop(self):
		self.player.stop()
		return

	def pause(self):
		pass

	def get_position(self):
		return self.player.get_position()

	def play(self, uri):		
		r = requests.get(uri)
		if r.status_code == 200:			
			print('play')
			
			self.player.set_mrl(uri)
			self.player.play()
		else:
			return