setlocal EnableDelayedExpansion
@echo on

cd build
if errorlevel 1 exit 1

:: call install script directly because executing the install target re-builds
:: (in that case, the re-build happens because timestamps have changed)
cmake -P cmake_install.cmake
if errorlevel 1 exit 1
