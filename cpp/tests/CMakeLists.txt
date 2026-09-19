add_executable(
  capsize_commons_tests
  main.cpp
  test_expected.cpp
  test_scope_guard.cpp
  test_string_utils.cpp
  test_float_format.cpp
  test_logging.cpp
)

target_link_libraries(capsize_commons_tests PRIVATE capsize::commons)
target_compile_features(capsize_commons_tests PRIVATE cxx_std_23)

if(MSVC)
  target_compile_options(capsize_commons_tests PRIVATE /W4 /permissive-)
else()
  target_compile_options(capsize_commons_tests PRIVATE -Wall -Wextra -Wpedantic)
endif()

add_test(NAME capsize_commons_tests COMMAND capsize_commons_tests)
