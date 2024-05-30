#!/usr/bin/python3
'''This script needs the api-token from an Admin to run
    This script reset all Challenges that are available in the DB with a Path to the .vdi file
    and set new flags inside of the vms and the DB
    This script should be planed as a cronjob'''
import subprocess
import sys
import requests


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
                    response = requests.get(url + 'challenges/' + str(c['id']) + '/flags', headers=headers)
                    flag = response.json()['data'][0]
                    change_flag(c.get('victims_connection'), c.get('vm_name'), flag)
                else:
                    continue
else:
    pass
