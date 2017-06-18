import vlc
import requests
from PyQt5 import QtCore

class Streamer():
	
	def __init__(self, *data):
		self.vlcInstance = vlc.Instance("--no-xlib --verbose 2")
		self.player = self.vlcInstance.media_player_new()
		event_manager = self.player.event_manager() # Attach event to player (next 3 lines)
		event=vlc.EventType()
		event_manager.event_attach(event.MediaPlayerStopped, self.end_reached)
		self.flag_stop = False

	def end_reached(self, *data):
		self.flag_stop = True
		print("End reached!")

	def stop(self):
		self.player.stop()

	def pause(self):
		print('sd')
		self.player.pause()

	def unpause(self):
		self.player.play()

	def get_position(self):
		return self.player.get_position()

	def play(self, uri):
		print('play')
		m=self.vlcInstance.media_new(uri)
		
		self.player.set_media(m)
		m.release()
		self.player.play()
		while self.flag_stop == True: # Wait until the end of the first media has been reached...
			self.quit()
			return