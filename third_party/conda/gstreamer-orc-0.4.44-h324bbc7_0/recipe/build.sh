#!/bin/bash
set -eo pipefail

meson setup buildir ${MESON_ARGS}
ninja -C buildir
ninja -C buildir install

# don't install static library (CFEP #18)
# (easier to delete than patch source to not build it)
rm -f $PREFIX/liborc-test*.a
