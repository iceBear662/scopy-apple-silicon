#!/usr/bin/env bash

set -ex

mkdir build
cd build

if [[ "$target_platform" == "win-64" ]]; then
  export PREFIX=${PREFIX}/Library
fi

cmake_config_args=(
    -DCMAKE_BUILD_TYPE=Release
    -DCMAKE_INSTALL_PREFIX=$PREFIX
    -DCMAKE_INSTALL_LIBDIR=lib
    -DCMAKE_PREFIX_PATH=$PREFIX
    -DBUILD_SHARED_LIBS=ON
    -DCMAKE_C_FLAGS="$CFLAGS"
)

if [[ "$target_platform" == "win-64" ]]; then
    cmake_config_args+=(
        -DCMAKE_GNUtoMS=ON
        -DCMAKE_C_COMPILER=$CC.exe
    )
else
    cmake_config_args+=(
        -DCMAKE_C_COMPILER=$CC
    )
fi

# clear variables that are not necessary thanks to CMAKE_ARGS but prevent
# in-tree native build of generate_codebook (picked up by CMAKE without flags)
# after having preserved CC and CFLAGS first as a CMAKE args above
unset AR
unset CFLAGS
unset LD
unset NM
unset RANLIB
unset STRIP
# set CC variable to build env compilers so in-tree native build of
# generate_codebook picks up the right compilers (not used for regular build
# because we set CMAKE_C_COMPILER
CC="$CC_FOR_BUILD"

cmake -G "Ninja" ${CMAKE_ARGS} .. "${cmake_config_args[@]}"
cmake --build . --config Release -- -j${CPU_COUNT}
