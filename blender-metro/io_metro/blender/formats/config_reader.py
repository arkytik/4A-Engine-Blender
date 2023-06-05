import enum
import dataclasses

from typing import List

from io_metro.blender.formats.chunk import Chunk
from io_metro.blender.formats.reader import MetroReader


class Bool8:
    val: int = 0

    b0: bool = False
    b1: bool = False
    b2: bool = False
    b3: bool = False
    b4: bool = False
    b5: bool = False
    b6: bool = False
    b7: bool = False

    def __init__(self, val: int = 0):
        self.val = val

    def read(self, reader: MetroReader):
        self.val = reader.read_u8()


class ConfigType(enum.Enum):
    Invalid = 0
    Dict = 20


class ConfigReader:
    _metro_reader: MetroReader
    _type: ConfigType

    _strings: List[str] = None
    _data_reader: MetroReader = None

    def __init__(self, reader: MetroReader):
        self._metro_reader = reader
        self._type = ConfigType(self._metro_reader.read_u8())

        self._init_data()

    def _init_data(self):
        if self._type == ConfigType.Dict:
            data_chunk = Chunk()
            strings_chunk = Chunk()

            data_chunk.read(self._metro_reader)
            strings_chunk.read(self._metro_reader)

            if not data_chunk or not strings_chunk:
                raise Exception("Incorrect Data And Strings Chunks")

            self._strings = []
            self._data_reader = data_chunk.reader

            for i in range(strings_chunk.reader.read_u32()):
                self._strings.append(strings_chunk.reader.read_str())

    def get_reader(self):
        if self._data_reader and self._data_reader.more():
            return self._data_reader

        return self._metro_reader

    def more(self) -> bool:
        return self.get_reader().more()

    def read_i8(self) -> int:
        return self.get_reader().read_i8()

    def read_u8(self) -> int:
        return self.get_reader().read_u8()

    def read_i16(self) -> int:
        return self.get_reader().read_i16()

    def read_u16(self) -> int:
        return self.get_reader().read_u16()

    def read_i32(self) -> int:
        return self.get_reader().read_i32()

    def read_u32(self) -> int:
        return self.get_reader().read_u32()

    def read_fp32(self) -> float:
        return self.get_reader().read_fp32()

    def read_bool(self) -> bool:
        return self.get_reader().read_bool()

    def read_bool8(self) -> Bool8:
        r = Bool8()
        r.read(self.get_reader())

        return r

    def read_str(self) -> str:
        if self._type == ConfigType.Dict:
            return self._strings[self.read_u32()]

        return self.get_reader().read_str()
