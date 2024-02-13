#!/usr/bin/env python3

import subprocess
import sys

if len(sys.argv) > 1:
    subprocess.run([sys.argv[1]+'getToken.sh'])
else:
    print("Keine Argumente angegeben.")