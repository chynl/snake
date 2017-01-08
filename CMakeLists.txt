cmake_minimum_required (VERSION 2.8)

if(POLICY CMP0025)
  cmake_policy(SET CMP0025 NEW)
endif()
if(POLICY CMP0054)
  cmake_policy(SET CMP0054 NEW)
endif()

project(Snake CXX)
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)

set(CMAKE_BUILD_TYPE Debug)

# Disable in-source build
if("${PROJECT_SOURCE_DIR}" STREQUAL "${PROJECT_BINARY_DIR}")
    file(MAKE_DIRECTORY build)
    message(FATAL_ERROR "In-source builds are not allowed.\nPlease try:\n1.Delete 'CMakeFiles' and 'CMakeCache.txt' in current directory\n2.Change to directory 'build' and run 'cmake ..'")
endif()

# Compiler flags
message(STATUS "Compiler ID: ${CMAKE_CXX_COMPILER_ID}")
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall")
    if(CMAKE_CXX_COMPILER_VERSION VERSION_LESS "4.7.0")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
    else()
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
    endif()
elseif (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -std=c++11")
elseif (CMAKE_CXX_COMPILER_ID} MATCHES "MSVC")
    # No config
endif()

file(GLOB_RECURSE INCS "${PROJECT_SOURCE_DIR}/include/*.h")
include_directories(${PROJECT_SOURCE_DIR}/include)

file(GLOB_RECURSE SRCS "${PROJECT_SOURCE_DIR}/src/*.cpp")
add_executable(snake ${SRCS} ${INCS})
if(NOT WIN32)
    target_link_libraries(snake pthread)
endif(NOT WIN32)