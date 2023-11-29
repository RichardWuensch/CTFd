import paramiko

def ssh_connect(vm_ip, ssh_username, ssh_password, token):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(vm_ip, username=ssh_username, password=ssh_password)
        ssh.exec_command('echo "'+token+'"> token')
        ssh.close()

    except paramiko.AuthenticationException:
        print("Error: Authentication failed")
    except paramiko.SSHException as ssh_err:
        print(f"Failed SSH-Connection: {ssh_err}")

