import asyncio

from flask import Blueprint, redirect, render_template, request, url_for
from CTFd.utils.decorators import (
    during_ctf_time_only,
    require_complete_profile,
    require_verified_emails,
)
import subprocess
import time

from CTFd.utils.user import get_current_user

attackbox = Blueprint("attackbox", __name__)
vboxmanage_path = r'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'


async def run_attackbox():
    cloned_vm_name = get_current_user().email + "_" + str(time.time_ns())

    # clone vm
    subprocess.run([vboxmanage_path, 'clonevm', 'Hacker\'s Playground', '--name', cloned_vm_name, '--register'])

    # start vm
    subprocess.run([vboxmanage_path, 'startvm', cloned_vm_name, '--type=headless'])

    # wait some seconds until the vm ist cloned and booted
    time.sleep(40)

    # get the IP of the vm to create the link to guacamole
    result = subprocess.run(
        [vboxmanage_path, 'guestcontrol', cloned_vm_name, 'run', '--username', 'kali', '--password', 'kali', '--',
         '/bin/bash', '-c', 'ip a | awk \'/inet / && $2 !~ /^127\./ {gsub(/\/.*/, "", $2); print $2}\''],
        capture_output=True)

    counter = 0
    while result.stdout.decode() == '' and counter <= 10:  # wird max count erreicht ist etwas schiefgelaufen -> Maschine muss dann gelöscht werden und vorgang neu gestartet
        counter = counter + 1
        result = subprocess.run(
            [vboxmanage_path, 'guestcontrol', cloned_vm_name, 'run', '--username', 'kali', '--password', 'kali',
             '--', '/bin/bash', '-c', 'ip a | awk \'/inet / && $2 !~ /^127\./ {gsub(/\/.*/, "", $2); print $2}\''],
            capture_output=True)
        time.sleep(5)

    ipaddress = result.stdout.decode().replace("\n", "")

    password = subprocess.run(
        [vboxmanage_path, 'guestcontrol', cloned_vm_name, 'run', '--username', 'root', '--password', 'toor',
         '--', '/bin/bash', '-c', 'cat /etc/guacamole/passwd.txt'],
        capture_output=True)

    # TODO das sollte gelogged werden damit man weiß, wer welche Maschine zu welcher Zeit mit welcher IP hatte
    print(get_current_user().email + " - " + cloned_vm_name + " - " + ipaddress)
    print(password.stdout.decode())
    return {'url': f'http://{ipaddress}:8080/guacamole/#/', 'vm': cloned_vm_name, 'password': password.stdout.decode()}


@attackbox.route('/attackbox')
@require_complete_profile
@during_ctf_time_only
@require_verified_emails
# Todo sollte auth sein oder?
def start_attackbox():
    all_vms = subprocess.run([vboxmanage_path, "list", "vms"], capture_output=True).stdout.decode()
    vm_names = [line.split("\"")[1].strip('"') for line in all_vms.splitlines()]
    if len([element for element in vm_names if element.startswith("admin@admin")]) < 1:
        url = asyncio.run(run_attackbox())  # Todo anderer Name falls das klappt
        return url
    else:
        return "You cannot create a second machine"


@attackbox.route('/stop_attackbox')
@require_complete_profile
@during_ctf_time_only
@require_verified_emails
def stop_attackbox():
    all_vms = subprocess.run([vboxmanage_path, "list", "vms"], capture_output=True).stdout.decode()
    vm_names = [line.split("\"")[1].strip('"') for line in all_vms.splitlines()]
    vm_name = [element for element in vm_names if element.startswith("admin@admin")][0]
    print(vm_name)
    subprocess.run([vboxmanage_path, 'controlvm', vm_name, 'poweroff'])
    time.sleep(5)
    try:
        # delete the vm and his disk
        subprocess.run([vboxmanage_path, 'unregistervm', vm_name, '--delete'], check=True)

        return "Successful"
    except subprocess.CalledProcessError as e:
        return "Error"
