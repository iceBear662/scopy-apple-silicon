setlocal EnableExtensions EnableDelayedExpansion
@echo on

:: meson options
:: (set pkg_config_path so deps in host env can be found)
set ^"MESON_OPTIONS=^
  --prefix="%LIBRARY_PREFIX%" ^
  --buildtype=release ^
  --backend=ninja ^
 ^"

:: configure build using meson
meson setup forgebuild !MESON_OPTIONS!
if errorlevel 1 exit 1

:: print results of build configuration
meson configure forgebuild
if errorlevel 1 exit 1

ninja -v -C forgebuild -j %CPU_COUNT%
if errorlevel 1 exit 1

ninja -C forgebuild install -j %CPU_COUNT%
if errorlevel 1 exit 1

:: don't install static library (CFEP #18)
:: (easier to remove it than patch to disable it in the build)
del /q /f "%LIBRARY_LIB%\liborc*.a"
if errorlevel 1 exit 1
