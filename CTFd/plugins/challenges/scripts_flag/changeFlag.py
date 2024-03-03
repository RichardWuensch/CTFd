import subprocess
import sys


def restore_snapshot(vm_name, path_to_vdi, flag):
    subprocess.run(['VBoxManage', 'controlvm', vm_name, 'poweroff'])  # shutdown
    subprocess.run(['VBoxManage', 'snapshot', vm_name, 'restorecurrent'])  # reset on last snapshot
    if path_to_vdi != "" and path_to_vdi is not None:
        subprocess.run([path_to_vdi + 'newFlag.sh', flag])  # call the script for the vm to set a new token
    subprocess.run(['VBoxManage', 'startvm', vm_name, '--type=headless'])  # start the vm


vm_name = None
path_to_vdi = None
token = None
if len(sys.argv) > 1:
    vm_name = sys.argv[1]
    if len(sys.argv) > 2:
        path_to_vdi = sys.argv[2]
        if len(sys.argv) > 3:
            token = sys.argv[3]
    restore_snapshot(vm_name, path_to_vdi, token)
