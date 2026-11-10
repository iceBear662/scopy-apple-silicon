#!/bin/bash
# Get an updated config.sub and config.guess
cp $BUILD_PREFIX/share/gnuconfig/config.* ./build

if [[ "${target_platform}" == linux-* ]]; then
  export CFLAGS="${CFLAGS} -D_GNU_SOURCE"
fi

./configure prefix=$PREFIX --disable-dependency-tracking
make
make install
