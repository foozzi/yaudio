from cx_Freeze import setup, Executable
buildOptions = dict(
	packages = [
		'idna', 
		'lxml', 
		'qtawesome', 
		'lxml', 
		'furl', 
		'requests', 
		'queue', 
		'pafy',
		'about'		
	], 
	excludes = [	
	],
	includes=[], 
	include_files=[])
 
import sys
base = 'Win32GUI' if sys.platform=='win32' else None
 
executables = [
    Executable('yaudio.py', base=base)
]

setup(
    name='YAudio',
    version = '0.1.0b',
    description = 'Audio player for youtube streaming with search by keywords',
    options = dict(build_exe = buildOptions),
    executables = executables
)
