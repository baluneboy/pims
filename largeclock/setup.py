from distutils.core import setup
import py2exe, sys, os

# In this dir "C:\Python27\pims\largeclock"
# RUN c:\Python27\python.exe setup.py
# to get dist directory that has your exe

sys.argv.append('py2exe')

setup(
	#options={'py2exe': {'bundle_files': 1, 'compressed': True}},
	windows=[{'script': 'largeclock.py'}],
	#zipfile=None,
	)