import contextlib
import enum
import gzip
import os
import pickle
import tempfile
from typing import BinaryIO, Optional


class State(enum.Enum):
    INIT = enum.auto()
    WRITING = enum.auto()
    WRITE_CLOSED = enum.auto()
    REMOVED = enum.auto()


class SequencePicklerError(RuntimeError):
    pass


class SequencePicklerIter(object):
    def __init__(self, filename: str, id_tag: Optional[str]) -> None:
        self._filename = filename
        self._fp = gzip.open(filename, "rb")
        id_tag_in_file = pickle.load(self._fp)
        if id_tag_in_file != id_tag:
            raise SequencePicklerError(
                f"Invalid tag, '{id_tag_in_file}', was found. " +
                f"It should be '{id_tag}'")

    def __iter__(self):
        return self

    def __next__(self):
        if self._fp is None:
            raise StopIteration("File closed.")

        try:
            obj = pickle.load(self._fp)
            return obj
        except EOFError:
            self.close()
            raise StopIteration("End of file")

    def close(self):
        if self._fp is not None:
            self._fp.close()
        self._fp = None


def iterate_sequence_pickler(filename: str, id_tag: Optional[str]):
    spi = SequencePicklerIter(filename, id_tag)
    try:
        for item in spi:
            yield item
    finally:
        spi.close()


class SequencePickler(object):
    def __init__(self,
                 tmp_filename: Optional[os.PathLike] = None,
                 *,
                 protocol: Optional[int] = None,
                 compresslevel: Optional[int] = 1,
                 id_tag: Optional[str] = None) -> None:
        if tmp_filename is None:
            fd, tmp_filename = tempfile.mkstemp("sequence_pickler")
            os.close(fd)

        self._state = State.INIT
        self._protocol = protocol
        self._tmp_filename = tmp_filename
        self._compresslevel = compresslevel
        self._id_tag = id_tag
        self._fp: BinaryIO = None

    @contextlib.contextmanager
    def open(self) -> None:
        if self._state != State.INIT:
            raise SequencePicklerError(
                f"Invalid call of open in {self._state} state.")

        self._state = State.WRITING
        self._fp = gzip.open(self._tmp_filename,
                             "wb",
                             compresslevel=self._compresslevel)
        pickle.dump(self._id_tag, self._fp, protocol=self._protocol)
        try:
            yield
        finally:
            self.close()

    def add(self, obj) -> None:
        if self._state != State.WRITING:
            raise SequencePicklerError(
                f"Invalid call of add in {self._state} state.")

        pickle.dump(obj, self._fp, protocol=self._protocol)

    def close(self) -> None:
        if self._state not in (State.WRITING, State.WRITE_CLOSED):
            raise SequencePicklerError(
                f"Invalid call of close in {self._state} state.")

        self._state = State.WRITE_CLOSED

        if self._fp is not None:
            self._fp.close()
        self._fp = None

    def __iter__(self):
        if self._state not in (State.INIT, State.WRITE_CLOSED):
            raise SequencePicklerError(
                f"Invalid call of __iter__ in {self._state} state.")

        self._state = State.WRITE_CLOSED
        return iterate_sequence_pickler(self._tmp_filename, self._id_tag)

    def remove_file(self):
        if self._state not in (State.INIT, State.WRITE_CLOSED):
            raise SequencePicklerError(
                f"Invalid call of remove_file in {self._state} state.")

        self._state = State.REMOVED
        os.unlink(self._tmp_filename)
