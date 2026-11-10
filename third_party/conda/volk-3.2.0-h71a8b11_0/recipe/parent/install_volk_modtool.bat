setlocal EnableDelayedExpansion

cd build

cmake -P python/volk_modtool/cmake_install.cmake
if errorlevel 1 exit 1

:: delete volk_modtool script and instead add the source to the module so it
:: can be used for module invocation and as an entry_point
del "%LIBRARY_PREFIX%\bin\volk_modtool.py"
if errorlevel 1 exit 1

copy "%SRC_DIR%\python\volk_modtool\volk_modtool" "%LIBRARY_PREFIX%\site-packages\volk_modtool\__main__.py"
if errorlevel 1 exit 1
