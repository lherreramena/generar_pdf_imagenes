echo off

set SOURCE_DIR=%~dp0

echo %SOURCE_DIR%

set TARGET=Debug

::set PYTHON_BIN=C:\Users\lherr\Documents\Develop\Projects\Src\Python\pythonEnv\Scripts\python.exe
if NOT DEFINED PYTHON_BIN (
	rem set PYTHON_BIN=%LocalAppData%\Programs\Python\Python310\python.exe
    set PYTHON_BIN=%SOURCE_DIR%Python\pythonEnv\Scripts\python.exe
)
set PYTHON_SRC=Py_sources\hd_w00_controller\led_ctrl.py
set PARAMS=--local_port 4001 --api_host 192.168.100.4 --api_port 5001

rem %PYTHON_BIN% %PYTHON_SRC% %PARAMS% %*

echo on

::#echo "Starting Local Api Rest with Flask"
::start "Flask Api Rest" %PYTHON_BIN% Python\api_rest_service\api_rest_cors_server.py
::%PYTHON_BIN% Python\api_rest_service\api_rest_cors_server.py --restapi_port 4005 --socket_port 4001

%PYTHON_BIN% %*%

::timeout 10 > NUL

::start "Flask Web Server" %PYTHON_BIN% Flask\app.py
::%PYTHON_BIN% Flask\app.py

echo off

exit /b %errorlevel%
