#!/usr/bin/python3
import subprocess
import requests
import sys

def change_flag_db(flag, new_flag):
    flag['content'] = new_flag
    requests.patch(url=url + 'flags/' + str(flag.get('id')), headers=headers, json=flag)


def change_flag_vm(vm_name, victims_connection, new_flag):
    subprocess.run(
        ['python3', '/var/www/CTFd/CTFd/plugins/challenges/scripts_flag/changeFlag.py', vm_name, victims_connection,
         new_flag])


def change_flag(victims_connection, vm_name, flag):
    new_flag = subprocess.run(['python3', '/var/www/CTFd/CTFd/plugins/challenges/scripts_flag/generate_new_flag.py'],
                              capture_output=True,
                              text=True).stdout.strip()
    change_flag_db(flag, new_flag)
    change_flag_vm(vm_name, victims_connection, new_flag)


if len(sys.argv) == 2:
    url = 'https://hlab.fiw.thws.de/api/v1/'
    headers = {
        'Authorization': 'Token ' + sys.argv[1],
        'Content-Type': 'application/json'
    }
    response = requests.get(url + 'challenges', headers=headers)

    if response.status_code == 200:
        challenges = response.json()['data']
        for c in challenges:
            if c.get('victims_connection') == "" or c.get('victims_connection') is None:
                continue
            else:
                state = requests.get(url + 'challenges/' + str(c['id']), headers=headers).json()['data']
                if state.get('state') == 'visible':
                    vm_name = c.get('vm_name')
                    result = subprocess.run(['VBoxManage', 'showvminfo', vm_name, '--machinereadable'], capture_output=True, text=True)
                    # Den Output nach dem VM-Status durchsuchen
                    for line in result.stdout.splitlines():
                       if line.startswith('VMState='):
                          # Extrahiere den Status
                          status = line.split('=')[1].strip('"')
                          if status != "running":
                             response = requests.get(url + 'challenges/' + str(c['id']) + '/flags', headers=headers)
                             flag = response.json()['data'][0]
                             change_flag(c.get('victims_connection'), vm_name, flag)
                else:
                    continue
else:
    pass
