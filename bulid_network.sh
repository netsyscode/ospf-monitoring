#!/bin/bash
NETWORK=$1
cd network
python3 setup.py --network $1
sudo chmod 600 topo/$1/ssh.pem
python3 remote.py --network $1 | tee -a build_network.log
echo "Network $1 is built"
cd ..
 