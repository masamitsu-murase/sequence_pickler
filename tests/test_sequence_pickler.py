from random import Random
from sequence_pickler import SequencePickler, SequencePicklerError
from sequence_pickler.sequence_pickler import SequencePicklerIter
import string
from typing import List, NamedTuple
import unittest
from unittest.mock import patch


class Sample(NamedTuple):
    index: int
    name: str
    is_active: bool
    properties: List[str]


class TestSequencePickler(unittest.TestCase):
    def test_write_objects(self):
        sp = SequencePickler()
        with self.assertRaises(SequencePicklerError):
            sp.add(None)

        added_items = [
            None,
            "str",
            123456,
            {
                "key1": "value1"
            },
        ]
        with sp.open():
            for item in added_items:
                sp.add(item)

            with self.assertRaises(SequencePicklerError):
                for item in sp:
                    pass

        items = []
        for item in sp:
            items.append(item)
        self.assertEqual(added_items, items)

        sp.remove_file()

        with self.assertRaises(SequencePicklerError):
            sp.remove_file()

    def test_read_from_other_sequence_pickler(self):
        filename = "tempfile.pickle.gz"
        sp_write = SequencePickler(filename)
        added_items = [
            set([1, 2, 3]),
            b"abcde",
            Sample(1, "name", True, ["a", "b", "c"]),
        ]

        with sp_write.open():
            for item in added_items:
                sp_write.add(item)

        sp_read0 = SequencePickler(filename)
        items0 = []
        sp_read1 = SequencePickler(filename)
        items1 = []
        sp_read2 = SequencePickler(filename)
        items2 = []
        for item0, item1, item2 in zip(sp_read0, sp_read1, sp_read2):
            items0.append(item0)
            items1.append(item1)
            items2.append(item2)

        self.assertEqual(added_items, items0)
        self.assertEqual(added_items, items1)
        self.assertEqual(added_items, items2)

    def generate_random_object(self, random_generator: Random, nested=False):
        if nested:
            num = random_generator.randrange(3)
        else:
            num = random_generator.randrange(4)

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
            value = self.generate_random_object(random_generator, nested=True)
            return {key: value}
        else:
            raise RuntimeError(f"Invalid num: {num}")

    def test_close_called_in_normal_case(self):
        filename = "tempfile.pickle.gz"

        close_org = SequencePicklerIter.close
        with patch.object(SequencePicklerIter, 'close') as mock_method:
            sp = SequencePickler(filename)

            def side_effect():
                close_org(sp)

            mock_method.side_effect = side_effect

            with sp.open():
                item = 1
                sp.add(item)
                item = 2
                sp.add(item)

            for index, actual in enumerate(sp):
                expected = index + 1
                self.assertEqual(expected, actual)

            mock_method.assert_called()

    def test_close_called_when_breaked(self):
        filename = "tempfile.pickle.gz"

        close_org = SequencePicklerIter.close
        with patch.object(SequencePicklerIter, 'close') as mock_method:
            sp = SequencePickler(filename)

            def side_effect():
                close_org(sp)

            mock_method.side_effect = side_effect

            with sp.open():
                item = 1
                sp.add(item)
                item = 2
                sp.add(item)

            for actual in sp:
                expected = 1
                self.assertEqual(expected, actual)
                break

            mock_method.assert_called()

    def test_close_called_when_error_raised(self):
        filename = "tempfile.pickle.gz"

        close_org = SequencePicklerIter.close
        with patch.object(SequencePicklerIter, 'close') as mock_method:
            sp = SequencePickler(filename)

            def side_effect():
                close_org(sp)

            mock_method.side_effect = side_effect

            with sp.open():
                item = 1
                sp.add(item)
                item = 2
                sp.add(item)

            with self.assertRaises(RuntimeError):
                for actual in sp:
                    expected = 1
                    self.assertEqual(expected, actual)
                    raise RuntimeError()

            mock_method.assert_called()

    def test_large_objects(self):
        filename = "temp_sp.pickle.gz"
        item_count = 128 * 1024
        seed = 1

        random_generator = Random(seed)
        sp = SequencePickler(filename)
        with sp.open():
            for _ in range(item_count):
                item = self.generate_random_object(random_generator)
                sp.add(item)

        random_generator = Random(seed)
        for _, actual in zip(range(item_count), sp):
            expected = self.generate_random_object(random_generator)
            self.assertEqual(expected, actual)
