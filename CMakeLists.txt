cmake_minimum_required (VERSION 2.8)

project(Snake CXX)

if("${PROJECT_SOURCE_DIR}" STREQUAL "${PROJECT_BINARY_DIR}")
    file(MAKE_DIRECTORY build)
    message(FATAL_ERROR "In-source builds are not allowed.\nPlease try:\n1.Delete 'CMakeFiles' and 'CMakeCache.txt' in current directory\n2.Change to directory 'build' and run 'cmake ..'")
endif("${PROJECT_SOURCE_DIR}" STREQUAL "${PROJECT_BINARY_DIR}")

if(CMAKE_COMPILER_IS_GNUCXX)
    set(CMAKE_CXX_FLAGS "-Wall -std=c++11 -O2")
    message(STATUS "Compiler flags: ${CMAKE_CXX_FLAGS}")
endif(CMAKE_COMPILER_IS_GNUCXX)
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)

include_directories(
    ${PROJECT_SOURCE_DIR}/include
)

aux_source_directory(${PROJECT_SOURCE_DIR}/src DIR_SRC)

add_executable(snake ${DIR_SRC})
if(NOT WIN32)
    target_link_libraries(snake pthread)
endif(NOT WIN32)