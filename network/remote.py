import paramiko
import os
import json
import argparse

SSH_FAILED = 0
SSH_SUCCESS = 1
EXEC_SUCCESS = 2 

def send_and_execute_script(server_info, network="minicernet"):
    process = SSH_FAILED
    ip = server_info["ip"]
    port = server_info["port"]
    username = server_info["username"]
    local_sh_path = os.path.join('setup',os.path.basename(server_info["script"]))
    pem_file = os.path.join("topo", network, server_info["pem_file"])
    
    # 创建SSH客户端
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        key = paramiko.RSAKey.from_private_key_file(pem_file)
        print(f"Connecting to {ip}")
        # 连接服务器
        ssh.connect(ip, port=port, username=username, pkey=key)
        print(f"Connected to {ip}")
        process = SSH_SUCCESS
        # 读取sh文件内容并执行
        with open(os.path.abspath(local_sh_path), 'r') as f:
            sh_content = f.read()
        # 直接执行sh文件内容并输出结果
        stdin, stdout, stderr = ssh.exec_command(sh_content)
        res, err = stdout.read(), stderr.read()
        result = res if res else err
        print(result.decode().strip())
        print("-" * 60)
        print(f"Successfully executed the script on {ip}")
        print("-" * 60)
        process = EXEC_SUCCESS
    except Exception as e:
        print(f"Failed to connect or execute on {ip}: {e}")
    finally:
        ssh.close()
    return process


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", help="network", default="minicernet", type=str)
    args = parser.parse_args()
    
    #paramiko.util.log_to_file("paramiko.log", level=paramiko.util.DEBUG)
    
    # Read the JSON file
    with open(os.path.join("topo", args.network, "pwd.json")) as f:
        servers = json.load(f)

    results = []
    for server in servers:
        result = send_and_execute_script(server, network=args.network)
        results.append(result)
    # 显示执行结果，分三类，并且输出各类的数量与IP
    print(f"EXEC_SUCCESS: {results.count(EXEC_SUCCESS)}")
    print(f"SSH_SUCCESS but EXEC_FAILED: {results.count(SSH_SUCCESS)}")
    print(f"SSH_FAILED: {results.count(SSH_FAILED)}")
    # 没有失败则不显示
    if results.count(SSH_FAILED+SSH_SUCCESS) == 0:
        print("All servers are successfully executed.") 
    else:
        print("Failed IPs:")
        for server, result in zip(servers, results):
            if result == SSH_FAILED:
                print(server["ip"])

