import random
import time
import json
import string

ticker = [
    "".join(random.choices(string.ascii_uppercase, k=4))
    for _ in range(10)
]

print(ticker)