from random import Random
from sequence_pickler import SequencePickler
import string
import subprocess
import sys
import time
from typing import List, NamedTuple


class Sample(NamedTuple):
    index: int
    name: str
    is_active: bool
    properties: List[str]


def generate_random_object(random_generator: Random, nested=False):
    if nested:
        num = random_generator.randrange(3)
    else:
        num = random_generator.randrange(5)

    if num == 0:
        return random_generator.randrange(0x1000000000000)
    elif num == 1:
        return ''.join(
            chr(ch)
            for ch in random_generator.choices(list(range(256)), k=256))
    elif num == 2:
        return b''.join(
            chr(ch).encode()
            for ch in random_generator.choices(list(range(256)), k=256))
    elif num == 3:
        key = ''.join(random_generator.choices(string.printable, k=5))
        value = generate_random_object(random_generator, nested=True)
        return {key: value}
    elif num == 4:
        sample = Sample(
            random_generator.randrange(1000000000),
            "".join(
                chr(ch)
                for ch in random_generator.choices(list(range(256)), k=256)),
            random_generator.choice([True, False]),
            random_generator.choices(list(range(256)), k=5),
        )
        return sample
    else:
        raise RuntimeError(f"Invalid num: {num}")


item_count = 5 * 1024 * 1024
filename = "temp_sp.pickle.gz"
seed = 1

# Run in memory
random_generator = Random(seed)
result = []
start = time.perf_counter()
for _ in range(item_count):
    item = generate_random_object(random_generator)
    result.append(item)
end = time.perf_counter()
print("In memory: Save: ", end - start)

start = time.perf_counter()
for item in result:
    a = item
end = time.perf_counter()
print("In memory: Load: ", end - start)

random_generator = Random(seed)
start = time.perf_counter()
for actual in result:
    expected = generate_random_object(random_generator)
    assert actual == expected
end = time.perf_counter()
print("In memory: Compare: ", end - start)

sys.stdout.flush()
subprocess.run(["ps", "-o", "pid,%cpu,rss,command", "-C", "python"])
print("")
result = None

# Run with SequencePickler
random_generator = Random(seed)
sp = SequencePickler(filename)
start = time.perf_counter()
with sp.open():
    for _ in range(item_count):
        item = generate_random_object(random_generator)
        sp.add(item)
end = time.perf_counter()
print("SequencePickler: Save: ", end - start)

start = time.perf_counter()
for item in sp:
    a = item
end = time.perf_counter()
print("SequencePickler: Load: ", end - start)

random_generator = Random(seed)
start = time.perf_counter()
for actual in sp:
    expected = generate_random_object(random_generator)
    assert actual == expected
end = time.perf_counter()
print("In memory: Compare: ", end - start)

sys.stdout.flush()
subprocess.run(["ls", "-alFh", filename])
print("")
