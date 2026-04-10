echo on

set SOURCE_DIR=%~dp0

:: ROOT_DIR es la carpeta raíz de SOURCE_DIR, es decir, la carpeta que contiene el proyecto
set ROOT_DIR=C:\Users\lherr\Documents\Develop\Projects\Src

echo %ROOT_DIR%


if NOT DEFINED PYTHON_BIN (
    set PYTHON_BIN=%ROOT_DIR%\Python\pythonEnv\Scripts\python.exe
)

echo on


%PYTHON_BIN% %*%


echo off

exit /b %errorlevel%
