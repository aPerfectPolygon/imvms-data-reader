# Version: 2.1.0

## Install

1) Download
   this [repository](https://github.com/aPerfectPolygon/imvms-data-reader-lifecycle/archive/refs/heads/main.zip)
   and extract it in appropriate path
2) go to `src\addresses.txt` and add all the paths which you want to translate the data from (each path in one line)<br>
   ```
   G:\path\to\server1
   G:\path\to\server2
   G:\path\to\server3
   ```
3) go to `setup` and install `python-3.10.10-amd64.exe`
4) go to `setup` and run `install (run as admin).bat` as Administrator
5) Verify the installation by looking at Windows Services there should be a service named `WinSdrTranslator` (if it is stopped Start it) 
6) Enjoy :)