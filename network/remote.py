import paramiko
import os

# 服务器列表，每个服务器是一个字典，包含IP、端口、用户名和对应的sh文件路径
servers = [
    {"ip": "47.94.8.103", "port": 22, "username": "root", "script": "/startup/startup_0.sh", "pem_file": "minicernet.pem"},
    {"ip": "139.224.223.30", "port": 22, "username": "root", "script": "/startup/startup_1.sh", "pem_file": "minicernet.pem"},
    {"ip": "118.178.238.89", "port": 22, "username": "root", "script": "/startup/startup_2.sh", "pem_file": "minicernet.pem"},
    {"ip": "47.104.105.204", "port": 22, "username": "root", "script": "/startup/startup_3.sh", "pem_file": "minicernet.pem"},
    {"ip": "120.79.158.94", "port": 22, "username": "root", "script": "/startup/startup_4.sh", "pem_file": "minicernet.pem"},
    {"ip": "8.134.59.19", "port": 22, "username": "root", "script": "/startup/startup_5.sh", "pem_file": "minicernet.pem"},
    {"ip": "47.108.213.86", "port": 22, "username": "root", "script": "/startup/startup_6.sh", "pem_file": "minicernet.pem"},
    {"ip": "39.104.74.124", "port": 22, "username": "root", "script": "/startup/startup_7.sh", "pem_file": "minicernet.pem"}
]

# 服务器上的sh文件存放路径
remote_sh_base_path = "/remote/path/to/scripts/"

def send_and_execute_script(server_info):
    ip = server_info["ip"]
    port = server_info["port"]
    username = server_info["username"]
    local_sh_path = server_info["script"]
    remote_sh_path = remote_sh_base_path + os.path.basename(local_sh_path)
    pem_file = server_info["pem_file"]
    
    # 创建SSH客户端
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # 使用.pem文件创建RSAKey对象
        key = paramiko.RSAKey.from_private_key_file(pem_file)
        
        # 连接服务器
        ssh.connect(ip, port=port, username=username, pkey=key)
        sftp = ssh.open_sftp()
        
        # 发送sh文件到服务器
        sftp.put(local_sh_path, remote_sh_path)
        sftp.close()
        
        # 在服务器上将sh文件设置为可执行
        ssh.exec_command(f"chmod +x {remote_sh_path}")
        
        # 执行sh文件
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(f"bash {remote_sh_path}")
        print(ssh_stdout.read().decode())  # 打印执行结果
    except Exception as e:
        print(f"Failed to connect or execute on {ip}: {e}")
    finally:
        ssh.close()

# 遍历服务器列表，发送并执行脚本
for server in servers:
    send_and_execute_script(server)
