#!/bin/bash
# Install SimplifiedScript from source

git clone https://github.com/Infinite-Networker/SimiplifiedScript.git
cd SimiplifiedScript
pip install -r requirements.txt
python setup.py install
