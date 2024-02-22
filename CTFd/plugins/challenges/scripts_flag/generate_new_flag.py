import random
import string


def generate_random_flag(length=10):
    characters = string.ascii_letters + string.digits + "!$%&_"
    random_string = ''.join(random.choice(characters) for i in range(length))
    return 'THWS{' + random_string + '}'


generate_random_flag()
