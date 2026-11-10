#!/usr/bin/env bash

set -exuo pipefail

./configure \
  --prefix=$PREFIX \
  --build=$BUILD \
  --host=$HOST \
  --with-libiconv-prefix=$PREFIX \
  --disable-static \
  --disable-csharp \
  --disable-dependency-tracking \
  --disable-java \
  --disable-native-java \
  --disable-openmp \
  --enable-fast-install \
  --without-emacs || (cat config.log; cat gettext-runtime/config.log; exit 1)

make -j${CPU_COUNT}

