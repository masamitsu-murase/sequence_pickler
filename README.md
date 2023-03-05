# Sequence Pickler

This is a python library to save long sequence in a file and read it back.

## Usage

```python
from sequence_pickler import SequencePickler

filename = "tempfile.pickle.gz"
sp = SequencePickler(filename)

# First, add objects.
with sp.open():
    sp.add(123)
    sp.add(234)
    sp.add(345)

# Then, read them.
for item in sp:
    print(item)  # => 123, 234, 345

# Again, read them.
for item in sp:
    print(item)  # => 123, 234, 345

# Read them from a different instance.
sp = SequencePickler(filename)
for item in sp:
    print(item)  # => 123, 234, 345

# Remove the file.
sp.remove_file()
```
