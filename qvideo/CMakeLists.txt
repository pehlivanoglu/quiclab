cmake_minimum_required(VERSION 3.22)
project(qvideo LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE RelWithDebInfo CACHE STRING "" FORCE)
endif()

# moxygen's standalone build fetches folly/fizz/wangle/mvfst/proxygen at the
# commits pinned in deps/moxygen/build/deps/github_hashes; only the targets
# qvideo links are compiled.
set(QVIDEO_MOXYGEN_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../deps/moxygen")
if(NOT EXISTS "${QVIDEO_MOXYGEN_DIR}/standalone/CMakeLists.txt")
  message(FATAL_ERROR "moxygen checkout missing at ${QVIDEO_MOXYGEN_DIR}; see README.md")
endif()
set(BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(BUILD_MOQTEST OFF CACHE BOOL "" FORCE)
add_subdirectory("${QVIDEO_MOXYGEN_DIR}/standalone" moxygen EXCLUDE_FROM_ALL)

add_executable(qvideo-selftest src/SelfTest.cpp)

add_executable(qvideo-server src/Server.cpp)
target_link_libraries(qvideo-server PRIVATE
  mvfst_server
  mvfst_congestion_control_server_congestion_controller_factory
  proxygen_hq_server
  folly_init_init
  folly_io_async_async_signal_handler)

add_executable(qvideo-client src/Client.cpp)
# Header-only InsecureVerifierDangerousDoNotUseInProduction from moxygen.
target_include_directories(qvideo-client PRIVATE "${QVIDEO_MOXYGEN_DIR}")
target_link_libraries(qvideo-client PRIVATE
  mvfst_client
  mvfst_fizz_client_handshake
  mvfst_common_events_folly_eventbase
  mvfst_common_udpsocket_folly_async_udp_socket
  folly_init_init
  folly_io_async_async_signal_handler)
