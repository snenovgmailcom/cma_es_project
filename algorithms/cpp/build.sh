#!/bin/bash
# Build nb_tree C++ extension module for MSC-CMA-ES
# Run from: algorithms/cpp/
set -e

cd "$(dirname "$0")"

PYBIND_INC=$(python3 -m pybind11 --includes)
EXT_SUFFIX=$(python3-config --extension-suffix)

echo "Building nb_tree${EXT_SUFFIX} ..."

c++ -O3 -march=native -shared -std=c++17 -fPIC \
    ${PYBIND_INC} \
    nb_tree.cpp \
    -o nb_tree${EXT_SUFFIX}

echo "Done: nb_tree${EXT_SUFFIX}"
ls -lh nb_tree${EXT_SUFFIX}
