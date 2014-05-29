cd "C:\Users\%USERNAME%\Desktop"
RMDIR dist /s /q
RMDIR build /s /q
"C:\Users\levtim\Desktop\Portable Python 2.7.5.1\Python-Portable.exe" "C:\Users\levtim\Desktop\Portable Python 2.7.5.1\pyinstaller-2.0\pyinstaller-2.0\pyinstaller.py" "C:\Users\levtim\Desktop\cygpop\main.py"
xcopy "C:\Users\levtim\Dropbox\main\pdftohtml.exe" "C:\Users\levtim\Desktop\dist\main\"
mkdir "C:\Users\levtim\Desktop\dist\main\src"
xcopy "C:\Users\levtim\Desktop\cygpop\*" "C:\Users\levtim\Desktop\dist\main\src"
xcopy "C:\Users\levtim\Desktop\dist\main\*" "C:\Users\levtim\Dropbox\main\" /sy
RMDIR dist /s /q
RMDIR build /s /q