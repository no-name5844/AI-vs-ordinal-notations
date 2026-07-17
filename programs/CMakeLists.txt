cmake_minimum_required(VERSION 3.15)
project(expansion_tool VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Build the GoogologyLib (provides the `googology` library target + headers).
add_subdirectory(lib/GoogologyLib)

set(CLI_SRC src/expansion_tool.cpp)

# The generic binary. Invoke as `expansion_tool <notation> <command> ...`,
# or rename/symlink it to a notation name (multi-call style).
add_executable(expansion_tool ${CLI_SRC})
target_link_libraries(expansion_tool PRIVATE googology)

# Per-notation multi-call binaries (same source; notation chosen by argv[0]).
foreach(NOTATION prss knuth conway epsilon_p_ss epsilon_omega_ss weak_veblen ns)
    add_executable(${NOTATION} ${CLI_SRC})
    target_link_libraries(${NOTATION} PRIVATE googology)
endforeach()
