@echo off
chcp 65001
pushd "%~dp0.."

if "%1" equ "" (
    set build_for=x64
) else (
    set build_for=%1
)
set build_dir=build_%build_for%

if exist %build_dir% (
    rmdir /s /q %build_dir%
)
mkdir %build_dir%

setlocal ENABLEEXTENSIONS
setlocal ENABLEDELAYEDEXPANSION
::call "C:\Program Files\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.cmd" /Release /%build_for% 
call "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvars64.bat"
echo %INCLUDE%
::set
cl /c /O2 /EHs /MD "/Fo%build_dir%\\sqlite3.obj" "src\\sqlite3.c"
cl /c /O2 /EHs /MD "/Fo%build_dir%\\gmlz.obj" "src\\gmlz.cpp"
cl /c /O2 /EHs /MD "/Fo%build_dir%\\gmlzip.obj"  "src\\gmlzip.cpp"
link /OUT:%build_dir%\\gmlzip.exe "%build_dir%\\*.obj"
%build_dir%\gmlzip.exe %2
endlocal
endlocal
echo on
