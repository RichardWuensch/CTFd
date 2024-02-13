import paramiko
import subprocess




'''async def async_ssh_connect(victims_connection, token):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        private_key_path = 'C:\\Users\\richa\\Desktop\\FHWS\\7.Semester\\key.pem'
        private_key = paramiko.RSAKey.from_private_key_file(private_key_path)
        connection_parameter = victims_connection.split("@")
        print(connection_parameter[1])
        print(connection_parameter[0])
        ssh.connect(hostname=connection_parameter[1], username=connection_parameter[0], pkey=private_key)
        ssh.exec_command('echo "' + token + '"> token')
        ssh.close()

    except paramiko.AuthenticationException:
        print("Error: Authentication failed")
    except paramiko.SSHException as ssh_err:
        print(f"Failed SSH-Connection: {ssh_err}")


async def async_run_vm(vm_name):
    subprocess.run([r'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe', 'startvm', vm_name, '--type=headless'])


async def async_stop_vm(vm_name):
    subprocess.run([r'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe', 'controlvm', vm_name, 'poweroff'])


async def async_restore_snapshot(vm_name, victims_connection, token):
    await async_stop_vm(vm_name)
    # await asyncio.sleep(5)
    subprocess.run([r'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe', 'snapshot', vm_name, 'restorecurrent'])
    # await asyncio.sleep(10)
    await async_run_vm(vm_name)
    # await asyncio.sleep(30)
    if victims_connection != "":
        await async_ssh_connect(victims_connection, token)
'''
#-----------------------------------------------------------------------------------------------------
'''
def ssh_connect(vm_ip, ssh_username, vm_password_type, ssh_password, token):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        if vm_password_type == "RSA Key":
            private_key_path = 'C:\\Users\\richa\\Desktop\\FHWS\\7.Semester\\key.pem'
            private_key = paramiko.RSAKey.from_private_key_file(private_key_path)
            ssh.connect(hostname=vm_ip, username=ssh_username, pkey=private_key)
        else:
            ssh.connect(hostname=vm_ip, username=ssh_username, password=ssh_password)
        ssh.exec_command('echo "' + token + '"> token')
        ssh.close()

    except paramiko.AuthenticationException:
        print("Error: Authentication failed")
    except paramiko.SSHException as ssh_err:
        print(f"Failed SSH-Connection: {ssh_err}")


vboxmanage_path = r'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'


def run_vm(vm_name):
    subprocess.run([vboxmanage_path, 'startvm', vm_name, '--type=headless'])


def stop_vm(vm_name):
    subprocess.run([vboxmanage_path, 'controlvm', vm_name, 'poweroff'])


def restore_snapshot(vm_name, vm_ip, ssh_username, ssh_password, vm_password_type, token):
    stop_vm(vm_name)
    time.sleep(5)
    subprocess.run([vboxmanage_path, 'snapshot', vm_name, 'restorecurrent'])
    time.sleep(10)
    run_vm(vm_name)
    time.sleep(30)
    ssh_connect(vm_ip, ssh_username, vm_password_type, ssh_password, token)
    
    ----------------------------------------------------------------------------------------------------------
    '''

'''
def shutdown_vm(vm, session):
    if str(vm.state) == 'Aborted' or str(vm.state) == 'PoweredOff':
        return

    vm.create_session(session=session)
    session.console.power_down()


def start_vm(vm, session):
    if str(vm.state) == 'Aborted' or str(vm.state) == 'PoweredOff':
        proc = vm.launch_vm_process(session, "headless", [])
        proc.wait_for_completion(timeout=-1)


def restore_snapshot(vm_name, vm_ip, ssh_username, ssh_password, token):
    vbox = virtualbox.VirtualBox()
    session = virtualbox.Session()
    vm = vbox.find_machine(vm_name)
    shutdown_vm(vm, session)
    time.sleep(5)
    vm.create_session(session=session)
    restoring = session.machine.restore_snapshot(vm.current_snapshot)
    while restoring.operation_percent < 100:
        time.sleep(0.5)

    session.unlock_machine()
    if restoring.completed == 1:
        start_vm(vm, session)
        time.sleep(30)
        print(vm_ip, ssh_username, ssh_password, token)
        ssh_connect(vm_ip, ssh_username, ssh_password, token)
        return 0
    else:
        return 1'''
