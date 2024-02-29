#!/bin/bash
NETWORK=$1
cd network
python setup.py $1
python remote.py
cd ..
 