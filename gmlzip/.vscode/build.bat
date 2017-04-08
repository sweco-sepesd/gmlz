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
if "%1" equ "gmlz" call :gmlz
if "%1" equ "zlib" call :zlib
if "%1" equ "tryzlib" call :tryzlib

if %errorlevel% neq 0 goto:exit_fail
shift
if not "%~1"=="" goto:parse_next
goto:exit_ok
::parse_next

:exit_fail
echo ERROR %errorlevel%
::exit_fail

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


:zlib
echo compiling zlib

if not exist "%build_dir%\zlib" (
    echo creating folder %build_dir\zlib%
    mkdir "%build_dir%\zlib"
)

set defines=/D WIN32 ^
/D NDEBUG ^
/D _CONSOLE ^
/D XML_STATIC ^
/D _CRT_SECURE_NO_WARNINGS


set src_files=src\zlib-1.2.11\adler32.c ^
    src\zlib-1.2.11\compress.c ^
    src\zlib-1.2.11\crc32.c ^
    src\zlib-1.2.11\deflate.c ^
    src\zlib-1.2.11\gzclose.c ^
    src\zlib-1.2.11\gzlib.c ^
    src\zlib-1.2.11\gzread.c ^
    src\zlib-1.2.11\gzwrite.c ^
    src\zlib-1.2.11\inflate.c ^
    src\zlib-1.2.11\infback.c ^
    src\zlib-1.2.11\inftrees.c ^
    src\zlib-1.2.11\inffast.c ^
    src\zlib-1.2.11\trees.c ^
    src\zlib-1.2.11\uncompr.c ^
    src\zlib-1.2.11\zutil.c 

cl /nologo /c /O2 /EHs /GF /MT /Gy /Gd /W3 %defines% /Fo"%build_dir%\zlib\\" %src_files%
lib /out:"%build_dir%\zlib.lib" "%build_dir%\zlib\*.obj"
::zlib
goto:eof

:tryzlib
cl /nologo /c /O2 /EHs /GF /MT /Gy /Gd /W3 %defines% /Fo"%build_dir%\\" src\tryzlib.c
::cl /nologo /c /O2 /EHs /MD "/Fo%build_dir%\\gmlzip.obj"  "src\\gmlzip.cpp"
link /nologo /LIBPATH:"%build_dir%" /OUT:%build_dir%\\tryzlib.exe "%build_dir%\\*.obj" "zlib.lib"

%build_dir%\tryzlib.exe

::tryzlib
goto:eof


:gmlz
echo compiling gmlz files only

set defines=/D WIN32 ^
/D NDEBUG ^
/D _CONSOLE ^
/D XML_STATIC ^
/D _CRT_SECURE_NO_WARNINGS

cl /nologo /c /O2 /EHs /GF /MT /Gy /Gd /W3 %defines% /Fo"%build_dir%\\" src\gmlz.cpp src\gmlzip.cpp
::gmlz
goto:eof

:gmlzip
echo building gmlzip application
echo args: %*

if not exist %build_dir% (
    echo creating folder %build_dir%
    mkdir %build_dir%
)

if not exist %build_dir%\sqlite3.obj (
    echo building sqlite
    rem ::cl /c /O2 /EHs /MD "/Fo%build_dir%\\sqlite3.obj" "src\\sqlite3.c"
)

if not exist %build_dir%\xmlparse.obj (
    echo building expat
    rem ::cl /c /O2 /EHs /MD /D WIN32 /Fo"%build_dir%\\" src\expat\xmlparse.c src\expat\xmlrole.c src\expat\xmltok.c src\expat\xmltok_impl.c src\expat\xmltok_ns.c
)
set defines=/D WIN32 ^
/D NDEBUG ^
/D _CONSOLE ^
/D XML_STATIC ^
/D _CRT_SECURE_NO_WARNINGS

cl /nologo /c /O2 /EHs /GF /MT /Gy /Gd /W3 %defines% /Fo"%build_dir%\\" src\sqlite3.c src\expat\xmlparse.c src\expat\xmlrole.c src\expat\xmltok.c src\expat\xmltok_impl.c src\expat\xmltok_ns.c src\gmlz.cpp src\gmlzip.cpp
::cl /nologo /c /O2 /EHs /MD "/Fo%build_dir%\\gmlzip.obj"  "src\\gmlzip.cpp"
link /nologo /OUT:%build_dir%\\gmlzip.exe "%build_dir%\\*.obj"

if "%1" neq "" (
    %build_dir%\gmlzip.exe "%1"
)
::gmlzip
goto:eof




