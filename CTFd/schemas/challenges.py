import re
import subprocess

import paramiko
from marshmallow import validate
from marshmallow.exceptions import ValidationError
from marshmallow_sqlalchemy import field_for

from CTFd.models import Challenges, ma


class ChallengeRequirementsValidator(validate.Validator):
    default_message = "Error parsing challenge requirements"

    def __init__(self, error=None):
        self.error = error or self.default_message

    def __call__(self, value):
        if isinstance(value, dict) is False:
            raise ValidationError(self.default_message)

        prereqs = value.get("prerequisites", [])
        if all(prereqs) is False:
            raise ValidationError(
                "Challenge requirements cannot have a null prerequisite"
            )
        return value

class ChallengeVMValidator(validate.Validator):
    def __call__(self, value):
        vboxmanage_path = r'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
        result = subprocess.run([vboxmanage_path, "list", "vms"], capture_output=True).stdout.decode()

        vm_names = [line.split("\"")[1].strip('"') for line in result.splitlines()]

        if vm_names.__contains__(value):
            result = subprocess.run([vboxmanage_path, "showvminfo", "--machinereadable", value],
                                    capture_output=True).stdout.decode().splitlines()
            vm_info = {}

            # Parsen der Ausgabe und Hinzufügen zum Dictionary
            for line in result:
                parts = line.split("=")
                if len(parts) > 1:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    vm_info[key] = value
            if vm_info["VMState"].strip('"') == "running":
                return value
            else:
                raise ValidationError("VM exists but is not running")
        else:
            raise ValidationError("VM name didn't exists in VirtualBox")

class ChallengeVictimsConnectionValidator(validate.Validator):
    def __call__(self, value):
        regex = "^(?:[a-zA-Z0-9_-]+)@(?:[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})$"
        if value == "":
            return value
        elif re.match(regex, value):
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                private_key_path = 'C:\\Users\\richa\\Desktop\\FHWS\\7.Semester\\key.pem'
                private_key = paramiko.RSAKey.from_private_key_file(private_key_path)
                connection_parameter = value.split("@")
                ssh.connect(hostname=connection_parameter[1], username=connection_parameter[0], pkey=private_key)
                ssh.close()
                return value
            except paramiko.AuthenticationException:
                raise ValidationError("Authentication of SSH failed")
            except paramiko.SSHException as ssh_err:
                raise ValidationError(f"Failed SSH-Connection: {ssh_err}")
        else:
            raise ValidationError("Victims Connection is not in the right format")

class ChallengeSchema(ma.ModelSchema):
    class Meta:
        model = Challenges
        include_fk = True
        dump_only = ("id",)

    name = field_for(
        Challenges,
        "name",
        validate=[
            validate.Length(
                min=0,
                max=80,
                error="Challenge could not be saved. Challenge name too long",
            )
        ],
    )

    category = field_for(
        Challenges,
        "category",
        validate=[
            validate.Length(
                min=0,
                max=80,
                error="Challenge could not be saved. Challenge category too long",
            )
        ],
    )

    description = field_for(
        Challenges,
        "description",
        allow_none=True,
        validate=[
            validate.Length(
                min=0,
                max=65535,
                error="Challenge could not be saved. Challenge description too long",
            )
        ],
    )

    requirements = field_for(
        Challenges,
        "requirements",
        validate=[ChallengeRequirementsValidator()],
    )

    vm_name = field_for(
        Challenges,
        "vm_name",
        validate=[ChallengeVMValidator()],
    )

    victims_connection = field_for(
        Challenges,
        "victims_connection",
        validate=[ChallengeVictimsConnectionValidator()],
    )
