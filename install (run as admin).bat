
echo installing ...
pushd "%~dp0"


@echo on
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe --version || goto :error
nssm.exe install WinSdrTranslatorLifeCycle "C:\Users\elyas\AppData\Local\Programs\Python\Python310\python.exe" "%cd%\main.py"
pause
@echo off

:error
echo %errorlevel%
pause
