cd ..
pyinstaller -F -w --distpath builds/pc main.py
xcopy data builds\pc\data /E /y /i
rmdir build /s /q
del main.spec /q
PAUSE
CLS
EXIT