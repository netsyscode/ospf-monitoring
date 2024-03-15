#!/bin/bash
NETWORK=$1
cd network
python3 setup.py --network $1
sudo chmod 600 topo/$1/ssh.pem
python3 remote.py --network $1 | tee -a build_network.log
echo 1 > /proc/sys/net/ipv4/ip_forward
echo "Network $1 is built"
cd ..
 