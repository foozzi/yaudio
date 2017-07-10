from cx_Freeze import setup, Executable

build_exe_options = {
	'build_exe': 'build', 
	'packages':{'idna', 'lxml', 'qtawesome', 'lxml', 'furl', 'requests', 'queue', 'pafy','vlc'},
    'includes': {'about'},
    'include_files': {'helpers'},
	'optimize':2
}
 
import sys
base = 'Win32GUI' if sys.platform=='win32' else None
 
executables = [
    Executable('yaudio.py', base=base)
]

setup(
    name='YAudio',
    version = '0.1.1b',
    description = 'Audio player for youtube streaming with search by keywords',
    options = dict(build_exe = build_exe_options),
    executables = executables
)
