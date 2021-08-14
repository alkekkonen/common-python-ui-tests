import string
import random


class StringGenerator:
    """
    Example of the @staticmethod
    """

    @staticmethod
    def get_random_string(max_length):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(max_length))
