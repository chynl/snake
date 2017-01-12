cmake_minimum_required(VERSION 2.8.2)

if (POLICY CMP0025)
    cmake_policy(SET CMP0025 NEW)
endif ()
if (POLICY CMP0054)
    cmake_policy(SET CMP0054 NEW)
endif ()

project(Snake CXX)

# Disable in-source build
if ("${PROJECT_SOURCE_DIR}" STREQUAL "${PROJECT_BINARY_DIR}")
    file(MAKE_DIRECTORY build)
    message(FATAL_ERROR "In-source builds are not allowed.\nPlease try:\n1.Delete 'CMakeFiles' and 'CMakeCache.txt' in current directory\n2.Change to directory 'build' and run 'cmake ..'")
endif ()

set(PROJ_EXEC_NAME snake)
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)

# Set default build type
if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Debug)
endif ()

# Compiler config
if ("${CMAKE_CXX_COMPILER_ID}" MATCHES "GNU")
    set(CMAKE_CXX_FLAGS "-Wall -Werror -Wextra -std=c++11 ${CMAKE_CXX_FLAGS}")
    set(CMAKE_CXX_FLAGS_DEBUG "-g -O0")
    set(CMAKE_CXX_FLAGS_RELEASE "-O2")
elseif ("${CMAKE_CXX_COMPILER_ID}" MATCHES "Clang")
    set(CMAKE_CXX_FLAGS "-Wall -Werror -Wextra -std=c++11 ${CMAKE_CXX_FLAGS}")
    set(CMAKE_CXX_FLAGS_DEBUG "-g -O0")
    set(CMAKE_CXX_FLAGS_RELEASE "-O2")
elseif ("${CMAKE_CXX_COMPILER_ID}" MATCHES "MSVC")
    # No config
endif ()
message(STATUS "CMAKE_BUILD_TYPE: ${CMAKE_BUILD_TYPE}")
message(STATUS "CMAKE_CXX_COMPILER_ID: ${CMAKE_CXX_COMPILER_ID}")
message(STATUS "CMAKE_CXX_FLAGS: ${CMAKE_CXX_FLAGS}")
message(STATUS "CMAKE_CXX_FLAGS_DEBUG: ${CMAKE_CXX_FLAGS_DEBUG}")
message(STATUS "CMAKE_CXX_FLAGS_RELEASE: ${CMAKE_CXX_FLAGS_RELEASE}")

# Include headers
file(GLOB_RECURSE HEADERS "${PROJECT_SOURCE_DIR}/include/*.h")
include_directories(${PROJECT_SOURCE_DIR}/include)

file(GLOB_RECURSE SRCS "${PROJECT_SOURCE_DIR}/src/*.cpp")
add_executable(${PROJ_EXEC_NAME} ${SRCS} ${HEADERS})

if(NOT WIN32)
    target_link_libraries(${PROJ_EXEC_NAME} pthread)
endif(NOT WIN32)
