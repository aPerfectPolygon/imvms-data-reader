
echo installing ...
pushd "%~dp0"


@echo on
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe --version || goto :error
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe -m pip install pytz
nssm.exe install WinSdrTranslator "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe" "C:\WinSdrTranslator\src\main.py"
pause
@echo off

:error
echo %errorlevel%
pause
