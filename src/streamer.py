import vlc

class Streamer():
	
	def __init__(self, *data):
		self.vlcInstance = vlc.Instance("--no-xlib")
		self.player = self.vlcInstance.media_player_new()
		event_manager = self.player.event_manager() # Attach event to player (next 2 lines)
		event=vlc.EventType()
		event_manager.event_attach(event.MediaPlayerStopped, self.end_reached)
		self.flag_stop = False
		self.volume = data[0]

	def end_reached(self, *data):
		self.flag_stop = True

	def stop(self):
		self.player.stop()

	def pause(self):
		self.player.pause()

	def unpause(self):
		self.player.play()

	def is_playing(self):
		return self.player.is_playing()

	def play(self, uri):
		m=self.vlcInstance.media_new(uri)
		
		self.player.set_media(m)
		self.player.audio_set_volume(int(self.volume))
		m.release()
		self.player.play()
		if self.flag_stop:
			self.stop()
			return
