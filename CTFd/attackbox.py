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
    cloned_vm_name = "attackbox_Clon" + str(time.time_ns())

    # clone vm
    subprocess.run([vboxmanage_path, 'clonevm', 'Ubuntu Server', '--name', cloned_vm_name, '--register'])

    # start vm
    subprocess.run([vboxmanage_path, 'startvm', cloned_vm_name, '--type=headless'])

    #wait some seconds until the vm ist cloned and booted
    time.sleep(40)

    # get the IP of the vm to create the link to guacamole
    result = subprocess.run(
        [vboxmanage_path, 'guestcontrol', cloned_vm_name, 'run', '--username', 'ubuntu', '--password', 'ubuntu', '--',
         '/bin/bash', '-c', 'ip a | awk \'/inet / && $2 !~ /^127\./ {gsub(/\/.*/, "", $2); print $2}\''],
        capture_output=True)

    counter = 0
    while result.stdout.decode() == '' and counter <= 5: # wird max count erreicht ist etwas schiefgelaufen -> Maschine muss dann gelöscht werden und vorgang neu gestartet
        print(counter)
        counter = counter + 1
        result = subprocess.run(
            [vboxmanage_path, 'guestcontrol', cloned_vm_name, 'run', '--username', 'ubuntu', '--password', 'ubuntu',
             '--', '/bin/bash', '-c', 'ip a | awk \'/inet / && $2 !~ /^127\./ {gsub(/\/.*/, "", $2); print $2}\''],
            capture_output=True)
        time.sleep(5)

    ipaddress = result.stdout.decode().replace("\n", "")

    # TODO das sollte gelogged werden damit man weiß, wer welche Maschine zu welcher Zeit mit welcher IP hatte
    print(get_current_user().email + " - " + cloned_vm_name + " - " + ipaddress)

    return {'url': f'http://{ipaddress}:8080/guacamole-1.5.3/#/', 'vm': cloned_vm_name}


@attackbox.route('/attackbox')
@require_complete_profile
@during_ctf_time_only
@require_verified_emails
def start_attackbox():
    url = asyncio.run(run_attackbox())  # anderer Name falls das klappt
    return url

@attackbox.route('/stop_attackbox/<data>')
@require_complete_profile
@during_ctf_time_only
@require_verified_emails
def stop_attackbox(data=None):
    subprocess.run([vboxmanage_path, 'controlvm', data, 'poweroff'])
    time.sleep(5)
    try:
        # delete the vm and his disk
        subprocess.run([vboxmanage_path, 'unregistervm', data, '--delete'], check=True)

        print(f"The vm {data} is deleted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error by deleting the vm: {e}")
