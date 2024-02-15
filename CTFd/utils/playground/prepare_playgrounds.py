import subprocess
import time


def get_vms_in_group(group_name):
    output = subprocess.run(['VBoxManage', 'list', 'vms'], capture_output=True, text=True).stdout
    vms_in_group = []
    for line in output.strip().split('\n'):
        vm_name = line.split('"')[1]
        vm_uuid = line.split('{')[1].split('}')[0]
        vm_info = subprocess.run(['VBoxManage', 'showvminfo', vm_uuid, '--machinereadable'], capture_output=True, text=True).stdout
        if f'groups="/{group_name}"' in vm_info:
            vms_in_group.append(vm_name)
    return vms_in_group


def start_and_stop_vm(vm_name):
    subprocess.run(['VBoxManage', 'startvm', vm_name, '--type', 'headless'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    time.sleep(180)  # wait for boot befor start
    subprocess.run(['VBoxManage', 'controlvm', vm_name, 'poweroff'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

def main():
    group_name = "playground"
    base_vm_name = "Hacker's Playground"
    target_count = 10 #max number of existing Playground machines, if increase this number, please stop the corrospondig cronjob and start the script seperate, afterwards enable the corrosponig cronjob again
    vms_in_group = get_vms_in_group(group_name)
    clone_count = len(vms_in_group)
    for i in range(clone_count, target_count):
        clone_name = f"{base_vm_name}_Clone_{str(time.time_ns())}"
        subprocess.run(['VBoxManage', 'clonevm', base_vm_name, '--name', clone_name, '--register'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        subprocess.run(['VBoxManage', 'modifyvm', clone_name, '--groups', f"/{group_name}"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) # move clone in group playground
        start_and_stop_vm(clone_name)

if __name__ == "__main__":
    main()