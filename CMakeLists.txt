cmake_minimum_required(VERSION 2.8.7)

# Drake Designer
project(DD)

if(POLICY CMP0028)
  # Double colon in target name means ALIAS or IMPORTED target.
  cmake_policy(SET CMP0028 NEW)
endif()

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/modules")

# set project variables
include(cmake/dd-version.cmake)
set(DD_INSTALL_BIN_DIR bin)
set(DD_INSTALL_DOC_DIR share/doc/director)
set(DD_INSTALL_LIB_DIR lib)
set(DD_INSTALL_INCLUDE_DIR include/director)
set(DD_INSTALL_CONFIG_DIR ${DD_INSTALL_LIB_DIR}/cmake/director-${DD_VERSION})
set(DD_TARGETS_NAME director-targets)

set(EXECUTABLE_OUTPUT_PATH "${CMAKE_BINARY_DIR}/${DD_INSTALL_BIN_DIR}")
set(LIBRARY_OUTPUT_PATH "${CMAKE_BINARY_DIR}/${DD_INSTALL_LIB_DIR}")

set(CMAKE_MACOSX_RPATH ON)
# Sets CMAKE_INSTALL_RPATH if not set manually. This allows packaging on MacOS.
if(NOT CMAKE_INSTALL_RPATH)
  set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib")
  set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
endif()

# declare options
option(BUILD_SHARED_LIBS "Build director with shared libraries." ON)
option(BUILD_TESTING "Build director with tests enabled." ON)

# include cmake scripts
include(cmake/dd-macros.cmake)
include(cmake/dd-testing.cmake)

# dependency options
option(USE_PORTMIDI "Build director with portmidi dependency." OFF)
option(USE_LCM "Build director with lcm dependency." OFF)
option(USE_LCMGL "Build director with lcmgl dependency." OFF)
option(USE_LIBBOT "Build director with libbot dependency." OFF)
option(USE_DRAKE "Build director with drake dependency." OFF)
option(USE_DRC "Build director with drc dependency." OFF)
option(USE_DRC_MAPS "Build director with drc maps dependency." OFF)
option(USE_DRC_PLANE_SEG "Build director with drc plane segmentation." OFF)
option(USE_OCTOMAP "Build director with octomap dependency." OFF)
option(USE_COLLECTIONS "Build director with collections dependency." OFF)
option(USE_PERCEPTION "Build director features that require OpenCV, PCL, cv-utils, and libbot as dependencies." OFF)

use_cpp11()
setup_qt()
setup_python()
setup_pkg_config_path()
set(DD_INSTALL_PYTHON_DIR ${DD_INSTALL_LIB_DIR}/python${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}/site-packages)

# build project
add_subdirectory(src)

# documentation
add_subdirectory(docs)

include(cmake/dd-post-build.cmake)
