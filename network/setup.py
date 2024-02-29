# 编写根据json文件，自动化生成对应setup.sh的脚本
import os, sys, json
import networkx as nx
import matplotlib.pyplot as plt

# 生成setup_index.sh
def generate_setup_sh(x, system='openwrt'):
    with open(os.path.join('topo', x), 'r') as f:
        data = json.load(f)
        # 构建nx拓扑图
        G = nx.Graph()
        for index in range(len(data)):
            G.add_node(index,OuterIP=data[index]['OuterIP'])
        # 子网
        num = 2
        # 每条边有序号，从2开始
        for index in range(len(data)):
            for nei in data[index]['Connected']:
                if  nei > index:
                    G.add_edge(index, nei, index=num)
                    num += 1

        # 输出有OuterIP地址的拓扑图
        outer_ip_labels = {node: data[node]['OuterIP'] for node in G.nodes}
        nx.draw(G, with_labels=True, labels=outer_ip_labels, font_weight='bold')
        plt.savefig("topology.png")
        plt.show()

        for index in range(len(data)):
            print(data[index])
            setup_sh = os.path.join('setup', f'setup_{index}.sh')
            with open(setup_sh, 'w') as f:
                f.write('#!/bin/bash\n')
                f.write('# Add setup commands here\n')
                # 配置SNMP的public community为cnpt
                f.write('echo "rocommunity cnpt" >> /etc/snmp/snmpd.conf\n')
                # 重启SNMP
                if system == 'openwrt':
                    f.write('/etc/init.d/snmpd restart\n')
                else:
                    f.write('systemctl restart snmpd\n')

                # 配置防火墙规则
                if system == 'centos':
                    f.write('firewall-cmd --add-port=161/udp --permanent\n')
                    f.write('firewall-cmd --add-port=162/udp --permanent\n')
                    f.write('firewall-cmd --add-protocol=ospf --permanent\n')
                    f.write('firewall-cmd --reload\n')

                #修改FRR配置文件/etc/frr/daemons 
                f.write('sed -i \'s/ospfd=no/ospfd=yes/g\' /etc/frr/daemons\n')
                f.write('sed -i \'s/ospf6d=no/ospf6d=yes/g\' /etc/frr/daemons\n')
                if system == 'openwrt':
                    f.write('./init.d/frr restart\n')
                else:
                    f.write('systemctl restart frr\n')
                
                # 清空原配置
                # 获取所有以gre开头的隧道名称
                f.write('tunnels=$(ip tunnel show | grep "^gre" | cut -d: -f1)\n')
                f.write('for tunnel in $tunnels; do\n')
                f.write('    echo "Deleting tunnel $tunnel"\n')
                f.write('    ip link set $tunnel down\n')
                f.write('    ip tunnel del $tunnel\n')
                f.write('done\n')

                f.write('echo "All GRE tunnels have been deleted."\n')
                
                intranetwork = set()
                # 根据相连的点index列表与其外网IP地址，内网IP地址，配置GRE隧道
                for i,nei in enumerate(data[index]['Connected']):
                    f.write(f'ip tunnel add gre-{i} mode gre remote {data[nei]["OuterIP"]} local {data[index]["OuterIP"]} ttl 255\n')
                    f.write(f'ip link set gre-{i} up\n')
                    e = G.edges[nei,index]['index']
                    if nei > index:
                        f.write(f'ip addr add 192.168.{e}.1/24 dev gre-{i}\n')
                        #f.write(f'ip addr add 192.168.{e}.1/24 peer 192.168.{e}.2/24  dev gre-{i}\n')
                    else:
                        f.write(f'ip addr add 192.168.{e}.2/24 dev gre-{i}\n')
                        #f.write(f'ip addr add 192.168.{e}.2/24 peer 192.168.{e}.1/24 dev gre-{i}\n')
                    if system == 'centos':
                        f.write(f'sysctl -w net.ipv4.conf.gre-{i}.rp_filter=0\n')
                    intranetwork.add(f'192.168.{e}.0/24')
                    f.write(f'echo "Creating GRE tunnel gre-{i} with remote {data[nei]["OuterIP"]} and local {data[index]["OuterIP"]}"\n')
                f.write(f'sysctl -p\n')
                # 配置FRR
                f.write('echo \"configure terminal\n')
                for i,nei in enumerate(data[index]['Connected']):
                    f.write(f'int gre-{i}\n')
                    e = G.edges[nei,index]['index']
                    if nei > index:
                        f.write(f'ip address 192.168.{e}.1/24\n')
                        #f.write(f'ip addr add 192.168.{e}.1/24 peer 192.168.{e}.2/24  dev gre-{i}\n')
                    else:
                        f.write(f'ip address 192.168.{e}.2/24\n')
                        #f.write(f'ip addr add 192.168.{e}.2/24 peer 192.168.{e}.1/24 dev gre-{i}\n')
                f.write('router ospf\n')
                # 根据相连的点index列表和自身，配置ospf
                for n in intranetwork:
                    f.write(f'network {n} area 0\n')
                f.write(f'ospf router-id {index+1}.{index+1}.{index+1}.{index+1}\n')
                f.write('end\n')
                f.write('write memory\n')
                f.write('exit\n\" | vtysh\n')
                
# 设置输入参数为json文件
if __name__ == "__main__":
    if len(sys.argv) == 3:
        generate_setup_sh(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        generate_setup_sh(sys.argv[1])
    else:
        print("Usage: python setup.py <json_file> [system]")
        print("system: openwrt(default) or centos")
        exit(1)
    print("setup.sh has been generated.")