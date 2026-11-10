#!/bin/bash
# Get an updated config.sub and config.guess
cp $BUILD_PREFIX/share/libtool/build-aux/config.* ./build-aux

export PERL=${BUILD_PREFIX}/bin/perl

if [[ ${HOST} =~ .*linux.* ]]; then
  export CFLAGS="${CFLAGS} -lrt"
fi

M4=m4 \
  ./configure --prefix=${PREFIX} --host=${HOST}
make -j${CPU_COUNT} ${VERBOSE_AT}

if [[ "${CONDA_BUILD_CROSS_COMPILATION}" != "1" ]]; then
make check
fi
make install

strings ${PREFIX}/bin/bison | grep ${BUILD_PREFIX}/bin/m4 || exit 0
echo "ERROR :: BUILD_PREFIX of ${BUILD_PREFIX}/bin/m4 found in ${PREFIX}/bin/bison"
exit 1
