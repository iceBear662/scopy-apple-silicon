# Build the generic gr-iio blocks from the matching GNU Radio release against
# conda-forge's arm64 GNU Radio package, which omits its optional IIO component.
cmake_minimum_required(VERSION 3.16)
project(scopy_gr_iio VERSION 3.10.11 LANGUAGES CXX)
find_package(Gnuradio 3.10 REQUIRED COMPONENTS runtime blocks)
find_package(libiio REQUIRED)
set(SRC "${CMAKE_CURRENT_LIST_DIR}/../src/gnuradio/gr-iio")
add_library(gnuradio-iio SHARED
    ${SRC}/lib/attr_sink_impl.cc
    ${SRC}/lib/attr_source_impl.cc
    ${SRC}/lib/attr_updater_impl.cc
    ${SRC}/lib/dds_control_impl.cc
    ${SRC}/lib/device_sink_impl.cc
    ${SRC}/lib/device_source_impl.cc
    ${SRC}/lib/iio_types.cc)
target_compile_features(gnuradio-iio PUBLIC cxx_std_17)
target_include_directories(gnuradio-iio PUBLIC
    $<BUILD_INTERFACE:${SRC}/include> $<INSTALL_INTERFACE:include>)
target_link_libraries(gnuradio-iio PUBLIC gnuradio::gnuradio-runtime
    PRIVATE gnuradio::gnuradio-blocks libiio::iio Volk::volk)
set_target_properties(gnuradio-iio PROPERTIES VERSION 3.10.11.0 SOVERSION 3.10.11
    INSTALL_NAME_DIR "@rpath")
install(TARGETS gnuradio-iio EXPORT gnuradio-iioTargets LIBRARY DESTINATION lib)
install(DIRECTORY ${SRC}/include/gnuradio/iio DESTINATION include/gnuradio
    FILES_MATCHING PATTERN "*.h")
install(EXPORT gnuradio-iioTargets NAMESPACE gnuradio::
    FILE gnuradio-iioConfig.cmake DESTINATION lib/cmake/gnuradio-iio)
