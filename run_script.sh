#!/bin/bash
# Run a SimplifiedScript (.ss) file with the interpreter
# Usage: ./run_script.sh <your_program.ss>

if [ -z "$1" ]; then
    echo "Usage: ./run_script.sh <your_program.ss>"
    exit 1
fi

python interpreter.py "$1"
