import asyncio

from flask import Blueprint, redirect, render_template, request, url_for
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


async def run_playground():
    cloned_vm_name = get_current_user().email + "_" + str(time.time_ns())

    # clone vm
    subprocess.run(['VBoxManage', 'clonevm', 'Hacker\'s Playground', '--name', cloned_vm_name, '--register'])

    # start vm
    subprocess.run(['VBoxManage', 'startvm', cloned_vm_name, '--type=headless'])

    # wait some seconds until the vm ist cloned and booted
    time.sleep(40)

    # get the IP of the vm to create the link to guacamole
    result = subprocess.run(
        ['VBoxManage', 'guestcontrol', cloned_vm_name, 'run', '--username', 'kali', '--password', 'kali', '--',
         '/bin/bash', '-c', 'ip a | awk \'/inet / && $2 !~ /^127\./ {gsub(/\/.*/, "", $2); print $2}\''],
        capture_output=True)

    counter = 0
    while result.stdout.decode() == '' and counter <= 20:  # wird max count erreicht ist etwas schiefgelaufen -> Maschine muss dann gelöscht werden und vorgang neu gestartet
        counter = counter + 1
        result = subprocess.run(
            ['VBoxManage', 'guestcontrol', cloned_vm_name, 'run', '--username', 'kali', '--password', 'kali',
             '--', '/bin/bash', '-c', 'ip a | awk \'/inet / && $2 !~ /^127\./ {gsub(/\/.*/, "", $2); print $2}\''],
            capture_output=True)
        time.sleep(5)

    ipaddress = result.stdout.decode().replace("\n", "")

    password = subprocess.run(
        ['VBoxManage', 'guestcontrol', cloned_vm_name, 'run', '--username', 'root', '--password', 'toor',
         '--', '/bin/bash', '-c', 'cat /etc/guacamole/passwd.txt'],
        capture_output=True)

    log(
        "playgrounds",
        format="[{date}] {ip} - {email} uses the vm {vm} with the IP Address {ipaddress}",
        email=get_current_user().email,
        vm=cloned_vm_name,
        ipaddress=ipaddress
    )
    return {'url': f'https://194.95.220.15:443/{ipaddress}/guacamole/#/', 'vm': cloned_vm_name, 'password': password.stdout.decode()}


@playground.route('/playground')
@require_complete_profile
@during_ctf_time_only
@require_verified_emails
def start_playground():
    all_vms = subprocess.run(['VBoxManage', 'list', 'vms'], capture_output=True).stdout.decode()
    vm_names = [line.split("\"")[1].strip('"') for line in all_vms.splitlines()]
    if len([element for element in vm_names if element.startswith(get_current_user().email)]) < 1:
        url = asyncio.run(run_playground())
        return url
    else:
        return "You cannot create a second machine"


@playground.route('/stop_playground')
@require_complete_profile
@during_ctf_time_only
@require_verified_emails
def stop_playground():
    all_vms = subprocess.run(['VBoxManage', 'list', 'vms'], capture_output=True).stdout.decode()
    vm_names = [line.split("\"")[1].strip('"') for line in all_vms.splitlines()]
    vm_name = [element for element in vm_names if element.startswith(get_current_user().email)]
    if len(vm_name) > 0:
        user = vm_name[0]
        subprocess.run(['VBoxManage', 'controlvm', user, 'poweroff'])
        time.sleep(5)
        try:
            # delete the vm and his disk
            subprocess.run(['VBoxManage', 'unregistervm', user, '--delete'], check=True)

            return "Successful"
        except subprocess.CalledProcessError as e:
            return "Error"
    else:
        return "No running playground"
