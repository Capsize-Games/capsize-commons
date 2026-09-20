cmake_minimum_required(VERSION 3.24)

project(
  capsize-commons
  VERSION 0.1.5
  DESCRIPTION "Common C/C++ building blocks shared across Capsize projects"
  LANGUAGES CXX
)

option(CAPSIZE_COMMONS_BUILD_TESTS "Build the capsize-commons tests" ON)
option(CAPSIZE_COMMONS_INSTALL "Generate install rules" ON)

add_library(capsize_commons src/logging.cpp)
add_library(capsize::commons ALIAS capsize_commons)

# C++23, not the standards-default C++20: `std::expected` is the point of
# expected.h, and curlee already compiles at CXX_STANDARD 23. See ADR 0002.
target_compile_features(capsize_commons PUBLIC cxx_std_23)
target_include_directories(
  capsize_commons
  PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
         $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

set_target_properties(
  capsize_commons
  PROPERTIES CXX_STANDARD 23
             CXX_STANDARD_REQUIRED ON
             CXX_EXTENSIONS OFF
)

if(MSVC)
  target_compile_options(capsize_commons PRIVATE /W4 /permissive-)
else()
  target_compile_options(capsize_commons PRIVATE -Wall -Wextra -Wpedantic)
endif()

if(CAPSIZE_COMMONS_INSTALL)
  include(GNUInstallDirs)
  include(CMakePackageConfigHelpers)

  install(
    TARGETS capsize_commons
    EXPORT capsize_commonsTargets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
  )
  install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
  install(
    EXPORT capsize_commonsTargets
    NAMESPACE capsize::
    FILE capsize-commonsTargets.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/capsize-commons
  )

  configure_package_config_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/capsize-commonsConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/capsize-commonsConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/capsize-commons
  )
  write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/capsize-commonsConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
  )
  install(
    FILES ${CMAKE_CURRENT_BINARY_DIR}/capsize-commonsConfig.cmake
          ${CMAKE_CURRENT_BINARY_DIR}/capsize-commonsConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/capsize-commons
  )
endif()

if(CAPSIZE_COMMONS_BUILD_TESTS)
  enable_testing()
  add_subdirectory(tests)
endif()
