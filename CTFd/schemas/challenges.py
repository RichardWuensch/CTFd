import os.path
import subprocess

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
        if value == "" or value is None:
            return value
        result = subprocess.run(['VBoxManage', "list", "vms"], capture_output=True).stdout.decode()

        vm_names = [line.split("\"")[1].strip('"') for line in result.splitlines()]

        if vm_names.__contains__(value):
            result = subprocess.run(['VBoxManage', "showvminfo", "--machinereadable", value],
                                    capture_output=True).stdout.decode().splitlines()
            vm_info = {}

            for line in result:
                parts = line.split("=")
                if len(parts) > 1:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    vm_info[key] = value
            return value
        else:
            raise ValidationError("VM name didn't exists in VirtualBox")


class ChallengeVictimsConnectionValidator(validate.Validator):
    def __call__(self, value):
        if value == "" or value is None:
            return value
        elif os.path.exists(value + 'newFlag.sh'):
            return value
        else:
            raise ValidationError("newFlag.sh is not available in the given folder")


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
