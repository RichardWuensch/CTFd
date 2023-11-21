import asyncio

from flask import Blueprint, redirect, render_template, request, url_for
from CTFd.utils.decorators import (
    during_ctf_time_only,
    require_complete_profile,
    require_verified_emails,
)
import subprocess
import time

attackbox = Blueprint("attackbox", __name__)


async def run_script():
    vboxmanage_path = r'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
    cloned_vm_name = "attackbox_Clon" + str(time.time_ns())

    # VM klonen
    subprocess.run([vboxmanage_path, 'clonevm', 'Ubuntu Server', '--name', cloned_vm_name, '--register'])

    # Befehl zum Starten der geklonten VM
    subprocess.run([vboxmanage_path, 'startvm', cloned_vm_name, '--type=headless'])

    time.sleep(60)

    # Befehl innerhalb der VM ausführen
    result = subprocess.run(
        [vboxmanage_path, 'guestcontrol', cloned_vm_name, 'run', '--username', 'ubuntu', '--password', 'ubuntu', '--',
         '/bin/bash', '-c', 'ip a | awk \'/inet / && $2 !~ /^127\./ {gsub(/\/.*/, "", $2); print $2}\''],
        capture_output=True)

    counter = 0
    while result.stdout.decode() == '' and counter <= 5:
        print(counter)
        counter = counter + 1
        result = subprocess.run(
            [vboxmanage_path, 'guestcontrol', cloned_vm_name, 'run', '--username', 'ubuntu', '--password', 'ubuntu',
             '--', '/bin/bash', '-c', 'ip a | awk \'/inet / && $2 !~ /^127\./ {gsub(/\/.*/, "", $2); print $2}\''],
            capture_output=True)
        time.sleep(5)

    string = result.stdout.decode().replace("\n", "")
    # retuned die URL mit der IP der erzeugten AttackBox
    return f'http://{string}:8080/guacamole-1.5.3/#/'


@attackbox.route('/attackbox')
@require_complete_profile
@during_ctf_time_only
@require_verified_emails
def main():
    url = asyncio.run(run_script())
    return url
