#!/bin/bash

cd build

cmake -P python/volk_modtool/cmake_install.cmake

# delete volk_modtool script and instead add the source to the module so it
# can be used for module invocation and as an entry_point
rm -f "$PREFIX/bin/volk_modtool"
cp "$SRC_DIR/python/volk_modtool/volk_modtool" "$PREFIX/site-packages/volk_modtool/__main__.py"
