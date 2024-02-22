#!/usr/bin/env python3

import subprocess
import sys


def getFlag(path_to_vdi):
    subprocess.run([path_to_vdi + 'getToken.sh'])


if len(sys.argv) > 1:
    getFlag(sys.argv[1])
