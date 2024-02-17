import asyncio

from flask import Blueprint
from CTFd.utils.decorators import (
    during_ctf_time_only,
    require_complete_profile,
    require_verified_emails,
)
import subprocess
import time

from CTFd.utils.logging import log
from CTFd.utils.user import get_current_user

playground = Blueprint("playground", __name__)


def get_vm(all_vms):
    for line in all_vms.strip().split('\n'):
        vm_name = line.split('"')[1]
        vm_info = subprocess.run(['VBoxManage', 'showvminfo', vm_name, '--machinereadable'], capture_output=True,
                                 text=True).stdout
        if f'groups="/playground"' in vm_info and 'VMState="poweroff"' in vm_info:
            return vm_name
    return None

def get_ip(cloned_vm_name):
    return subprocess.run(
        ['VBoxManage', 'guestcontrol', cloned_vm_name, 'run', '--username', 'kali', '--password', 'kali',
         '--', '/bin/bash', '-c', 'ip a | awk \'/inet / && $2 !~ /^127\./ {gsub(/\/.*/, "", $2); print $2}\''],
        capture_output=True).stdout.decode().replace("\n", "")

def get_password(cloned_vm_name):
    return subprocess.run(
        ['VBoxManage', 'guestcontrol', cloned_vm_name, 'run', '--username', 'root', '--password', 'toor',
         '--', '/bin/bash', '-c', 'cat /etc/guacamole/passwd.txt'],
        capture_output=True).stdout.decode()


async def run_playground(usable_vm):
    cloned_vm_name = get_current_user().email + "_" + str(time.time_ns())
    subprocess.run(['VBoxManage', 'modifyvm', usable_vm, '--name', cloned_vm_name])
    subprocess.run(['VBoxManage', 'startvm', cloned_vm_name, '--type=headless'])
    time.sleep(40)
    result = get_ip(cloned_vm_name)

    counter = 0
    while result == '' and counter <= 20:
        counter = counter + 1
        result = get_ip(cloned_vm_name)
        time.sleep(3)

    ipaddress = result
    print(ipaddress)
    print(get_password(cloned_vm_name))

    log(
        "playgrounds",
        format="[{date}] {ip} - {email} uses the vm {vm} with the IP Address {ipaddress}",
        email=get_current_user().email,
        vm=cloned_vm_name,
        ipaddress=ipaddress
    )
    return {'url': f'https://hlab.fiw.thws.de/{ipaddress}/', 'vm': cloned_vm_name, 'password': get_password(cloned_vm_name)}

@playground.route('/playground')
@require_complete_profile
@during_ctf_time_only
def stop_playground():
    all_vms = subprocess.run(['VBoxManage', 'list', 'vms'], capture_output=True).stdout.decode()
    vm_names = [line.split("\"")[1].strip('"') for line in all_vms.splitlines()]
    vm_name = [element for element in vm_names if element.startswith(get_current_user().email)]
    if len(vm_name) > 0:
        return get_password(vm_name[0])
    else:
        return None


@playground.route('/playground/start')
@require_complete_profile
@during_ctf_time_only
def start_playground():
    all_vms = subprocess.run(['VBoxManage', 'list', 'vms'], capture_output=True).stdout.decode()
    vm_names = [line.split("\"")[1].strip('"') for line in all_vms.splitlines()]
    if len([element for element in vm_names if element.startswith(get_current_user().email)]) < 1:
        usable_vm = get_vm(all_vms)
        print(usable_vm)
        if usable_vm is None:
            return "Currently no Playground is available" # Todo frontend
        url = asyncio.run(run_playground(usable_vm))
        return url
    else:
        existing_vm_name = [element for element in vm_names if element.startswith(get_current_user().email)][0]
        return {'url': f'https://hlab.fiw.thws.de/{get_ip(existing_vm_name)}/', 'vm': existing_vm_name, 'password': get_password(existing_vm_name)}


@playground.route('/playground/stop')
@require_complete_profile
@during_ctf_time_only
def stop_playground():
    all_vms = subprocess.run(['VBoxManage', 'list', 'vms'], capture_output=True).stdout.decode()
    vm_names = [line.split("\"")[1].strip('"') for line in all_vms.splitlines()]
    vm_name = [element for element in vm_names if element.startswith(get_current_user().email)]
    if len(vm_name) > 0:
        subprocess.run(['VBoxManage', 'controlvm', vm_name[0], 'poweroff'])
        time.sleep(5)
        try:
            subprocess.run(['VBoxManage', 'unregistervm', vm_name[0], '--delete'], check=True)
            subprocess.Popen(['python3', 'CTFd/utils/playground/prepare_playgrounds.py'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            return "Successful"
        except subprocess.CalledProcessError as e:
            return "Error"
    else:
        return "No running playground"
