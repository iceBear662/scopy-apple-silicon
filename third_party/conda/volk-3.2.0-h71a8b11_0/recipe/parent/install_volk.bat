setlocal EnableDelayedExpansion

cd build

cmake -DCMAKE_INSTALL_LOCAL_ONLY=1 -P cmake_install.cmake
if errorlevel 1 exit 1

cmake -P apps/cmake_install.cmake
if errorlevel 1 exit 1

cmake -P lib/cmake_install.cmake
if errorlevel 1 exit 1
