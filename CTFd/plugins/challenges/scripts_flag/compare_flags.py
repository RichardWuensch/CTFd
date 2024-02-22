import requests

from CTFd.plugins.challenges.scripts_flag.changeFlag import restore_snapshot
from CTFd.plugins.challenges.scripts_flag.generate_new_flag import generate_random_flag
from CTFd.plugins.challenges.scripts_flag.getFlag import getFlag

url = 'https://hlab.fiw.thws.de/api/v1/'
headers = {
    'Authorization': 'Token ctfd_43675bacbbd5877904e4f54c83c6d2f571d9394030cf031acb5827534f8bccc4', # Prod
    'Content-Type': 'application/json'
}


def set_new_flag(flag, new_flag):
    flag['content'] = new_flag
    requests.patch(url + 'flags/' + str(flag.get('id')), headers=headers, json=flag)


def compare_token(victims_connection, vm_name, flag):
    flag_from_vm = getFlag(victims_connection)  # subprocess.run(['python3', '/var/www/', victims_connection], capture_output=True, text=True).stdout
    if flag_from_vm == flag:
        return
    else:
        new_flag = generate_random_flag()
        set_new_flag(flag, new_flag)
        restore_snapshot(vm_name, victims_connection, new_flag)


response = requests.get(url + 'challenges', headers=headers)

if response.status_code == 200:
    challenges = response.json()['data']
    mapped_dict = dict()
    for c in challenges:
        if c.get('victims_connection') == "" or c.get('victims_connection') is None:
            continue
        else:
            response = requests.get(url + 'challenges/' + str(c['id']) + '/flags', headers=headers)
            flag = response.json()['data'][0]
            compare_token(c.get('victims_connection'), c.get('vm_name'), flag)
