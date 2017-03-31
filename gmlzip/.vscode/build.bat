@echo off
chcp 65001
setlocal ENABLEDELAYEDEXPANSION
pushd "%~dp0.."

:parse_next
echo === %1 ===
if "%1" equ "x64" call :set_env %1
if "%1" equ "x86" call :set_env %1
if "%1" equ "clean" call :clean
if "%1" equ "gmlzip" call :gmlzip %2
shift
if not "%~1"=="" goto:parse_next
::parse_next

:exit_ok
popd
endlocal
echo All done
echo on
@goto:eof
::exit_ok

:set_env
if "%1" equ "" (
    set build_for=x64
) else (
    set build_for=%1
)
set build_dir=build_%build_for%
if "%build_for%" equ "x64" (
    call "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvars64.bat"
) else if "%build_for%" equ "x86" (
    call "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvars32.bat"
)
echo %INCLUDE%
goto:eof
::set_env

:clean
if exist %build_dir% (
    echo removing existing folder %build_dir%
    rmdir /s /q %build_dir%
)

goto:eof
::clean

:gmlzip
echo building gmlzip application
echo args: %*

if not exist %build_dir% (
    echo creating folder %build_dir%
    mkdir %build_dir%
)

if not exist %build_dir%\sqlite3.obj (
    cl /c /O2 /EHs /MD "/Fo%build_dir%\\sqlite3.obj" "src\\sqlite3.c"
)

cl /nologo /c /O2 /EHs /MD "/Fo%build_dir%\\gmlz.obj" "src\\gmlz.cpp"
cl /nologo /c /O2 /EHs /MD "/Fo%build_dir%\\gmlzip.obj"  "src\\gmlzip.cpp"
link /nologo /OUT:%build_dir%\\gmlzip.exe "%build_dir%\\*.obj"

if "%1" neq "" (
    %build_dir%\gmlzip.exe "%1"
)
::gmlzip
goto:eof




