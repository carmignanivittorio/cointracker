import random
import string


def get_random_string(length):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))
