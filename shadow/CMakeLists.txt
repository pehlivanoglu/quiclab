# Shadow early-congestion detector, offline replay only (moqx_shadow_replay).
# Copied verbatim from moq-testbed src/shadow (pure C++, no moxygen / mvfst);
# see README.md. Build: cmake -S shadow -B shadow/build -DCMAKE_BUILD_TYPE=Release && cmake --build shadow/build
cmake_minimum_required(VERSION 3.16)
project(quiclab_shadow CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(moqx_shadow_detector STATIC Detector.cpp Engine.cpp)
# The sources include "shadow/Detector.h": the include root is quiclab/.
target_include_directories(moqx_shadow_detector PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/..)
target_compile_options(moqx_shadow_detector PRIVATE -Wall -Wextra -Wpedantic)

add_executable(moqx_shadow_replay Replay.cpp)
target_link_libraries(moqx_shadow_replay PRIVATE moqx_shadow_detector)
