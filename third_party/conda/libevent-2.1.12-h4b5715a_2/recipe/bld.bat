@echo on

:: Build
mkdir build
cd build
cmake -G "Ninja" ^
         -DBUILD_SHARED_LIBS=ON ^
         -DCMAKE_BUILD_TYPE=Release ^
         -DCMAKE_PREFIX_PATH=%LIBRARY_PREFIX% ^
         -DCMAKE_INSTALL_PREFIX=%LIBRARY_PREFIX% ^
         %SRC_DIR%
if errorlevel 1 exit 1

:: Install
cmake --build . --config Release --target install
if errorlevel 1 exit 1
