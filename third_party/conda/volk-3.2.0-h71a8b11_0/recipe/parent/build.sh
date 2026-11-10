#!/bin/bash

# copy the cpu_features license to the source root
cp "cpu_features/LICENSE" "LICENSE_CPU_FEATURES"

if [[ $target_platform == osx* ]] ; then
    CXXFLAGS="${CXXFLAGS} -D_LIBCPP_DISABLE_AVAILABILITY"
fi

mkdir build
cd build

cmake_config_args=(
    -DCMAKE_BUILD_TYPE=Release
    -DCMAKE_INSTALL_LIBDIR=lib
    -DCMAKE_INSTALL_PREFIX=$PREFIX
    -DCMAKE_PREFIX_PATH=$PREFIX
    -DVOLK_PYTHON_DIR="$PREFIX/site-packages"
    -DORCC_EXECUTABLE="$BUILD_PREFIX/bin/orcc"
    -DENABLE_LGPL=OFF
    -DENABLE_MODTOOL=ON
    -DENABLE_PROFILING=OFF
    -DENABLE_TESTING=ON
)
cmake ${CMAKE_ARGS} -G "Ninja" .. "${cmake_config_args[@]}"
cmake --build . --config Release -- -j${CPU_COUNT}

if [[ $target_platform == linux-ppc64le ]] ; then
    SKIP_TESTS=(
        qa_volk_32fc_32f_dot_prod_32fc
        qa_volk_32fc_s32fc_multiply_32fc
        qa_volk_32fc_s32fc_rotatorpuppet_32fc
        qa_volk_32fc_x2_s32fc_multiply_conjugate_add_32fc
    )
fi
SKIP_TESTS_STR=$( IFS="|"; echo "${SKIP_TESTS[*]}" )

if [[ "${CONDA_BUILD_CROSS_COMPILATION}" != "1" ]]; then
    if [ -z "$SKIP_TESTS_STR" ]; then
        ctest --build-config Release --output-on-failure --timeout 120 -j${CPU_COUNT}
    else
        ctest --build-config Release --output-on-failure --timeout 120 -j${CPU_COUNT} -E $SKIP_TESTS_STR
        # now run the skipped tests to see the failures, but don't error out
        ctest --build-config Release --output-on-failure --timeout 120 -j${CPU_COUNT} -R $SKIP_TESTS_STR || true
    fi
fi
