from typing import List
from urllib.parse import urljoin as original_urljoin


# Function like StringGenerator.get_random_string but with no class
def urljoin(*args: List[str]):
    base = args[0] if args[0][-1] == '/' else args[0] + '/'
    if len(args) > 2:
        return urljoin(original_urljoin(base, args[1]), *args[2:])
    if len(args) == 2:
        return original_urljoin(base, args[1])
    return args[0]
