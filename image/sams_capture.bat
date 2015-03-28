REM this bat file and python scripts on TReK21 in c:\Users\samsops folder
@echo on
:while1
	REM "C:\Python27\pythonw.exe" "C:\Users\samsops\win32_screencapture.pyw"
	"C:\Python27\pythonw.exe" "\\yoda\pims\www\plots\user\sams\trekscripts\image\win32_screencapture.pyw"
	timeout 60
	goto :while1