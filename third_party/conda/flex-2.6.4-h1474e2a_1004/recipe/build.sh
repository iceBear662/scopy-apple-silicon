#!/bin/bash

autoreconf -vfi

# skip the creation of man pages by faking existance of help2man
if [ `uname` == Darwin ]; then
    export HELP2MAN=/usr/bin/true
fi
if [ `uname` == Linux ]; then
    export HELP2MAN=/bin/true
fi

# TODO: do this in the compiler package
export ac_cv_func_realloc_0_nonnull=yes

if [[ "${CONDA_BUILD_CROSS_COMPILATION}" == "1" ]]; then
  CONFIGURE_ARGS="${CONFIGURE_ARGS} --disable-bootstrap"
fi

if [[ ${HOST} =~ .*linux.* ]]; then
    export CC=${GCC}
fi

./configure --prefix="$PREFIX"  \
            --host=${HOST}      \
            --build=${BUILD} ${CONFIGURE_ARGS}

make -j${CPU_COUNT} ${VERBOSE_AT}
if [[ "${CONDA_BUILD_CROSS_COMPILATION}" != "1" ]]; then
  make check
fi
make install
