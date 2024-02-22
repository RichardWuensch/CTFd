import subprocess
import sys
import requests


def set_new_flag(flag, new_flag):
    flag['content'] = new_flag
    print(flag)
    requests.patch(url=url + 'flags/' + str(flag.get('id')), headers=headers, json=flag)


def compare_token(victims_connection, vm_name, flag):
    flag_from_db = flag['content']
    flag_from_vm = subprocess.run(
        ['python3', '/var/www/CTFd/CTFd/plugins/challenges/scripts_flag/getFlag.py', victims_connection],
        capture_output=True, text=True).stdout.strip()
    if flag_from_vm == flag_from_db:
        return
    else:
        new_flag = subprocess.run(
            ['python3', '/var/www/CTFd/CTFd/plugins/challenges/scripts_flag/generate_new_flag.py']).stdout.strip()
        set_new_flag(flag, new_flag)
        subprocess.run(
            ['python3', '/var/www/CTFd/CTFd/plugins/challenges/scripts_flag/changeFlag.py', vm_name, victims_connection,
             new_flag])


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
                response = requests.get(url + 'challenges/' + str(c['id']) + '/flags', headers=headers)
                flag = response.json()['data'][0]
                compare_token(c.get('victims_connection'), c.get('vm_name'), flag)
else:
    pass
