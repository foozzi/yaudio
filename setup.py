from cx_Freeze import setup, Executable
 
# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(
	packages = ['idna', 'lxml'], 
	excludes = [], 
	includes=['qtawesome', 'lxml', 'furl', 'requests', 'queue', 'pafy'], 
	include_files=[
		'./src/main.py', 
		'./src/helpers/', 
		'./src/about.py', 
		'./src/streamer.py',
		'./src/vlc.py',
		'./src/config.cfg',
		'./src/img/'	
		])
 
import sys
base = 'Win32GUI' if sys.platform=='win32' else None
 
executables = [
    Executable('./src/yaudio.py', base=base)
]
 
setup(
    name='YAudio',
    version = '0.0.6a',
    description = 'Audio player for youtube streaming with search by keywords',
    options = dict(build_exe = buildOptions),
    executables = executables
)