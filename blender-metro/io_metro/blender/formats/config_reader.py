import zlib
import enum
import dataclasses

from typing import List

from io_metro.blender.formats.math import *

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
    Debug = 3
    Dict_Without_Sections = 20


class ConfigReader:
    _type: ConfigType
    _metro_reader: MetroReader
    _typed_strings: dict

    _strings: List[str] = None
    _data_reader: MetroReader = None

    def __init__(self, reader: MetroReader):
        self._metro_reader = reader
        self._type = ConfigType(self._metro_reader.read_u8())

        self._init_data()

        self._typed_strings: dict = {
            "i8": lambda: self.read_i8(),
            "u8": lambda: self.read_u8(),
            "i16": lambda: self.read_i16(),
            "u16": lambda: self.read_u16(),
            "i32": lambda: self.read_i32(),
            "u32": lambda: self.read_u32(),
            "fp32": lambda: self.read_fp32(),
            "bool": lambda: self.read_bool(),
            "bool8": lambda: self.read_bool8(),
            "vec3i": lambda: self.read_vec3i(),
            "vec4i": lambda: self.read_vec4i(),
            "vec3f": lambda: self.read_vec3f(),
            "vec4f": lambda: self.read_vec4f(),
            "choose": lambda: self.read_choose(),
            "stringz": lambda: self.read_str(),
            "array": lambda: self.read_array(),
            "u8_array": lambda: self.read_array_u8(),
            "u16_array": lambda: self.read_array_u16(),
            "u32_array": lambda: self.read_array_u32(),
        }

    def _init_data(self):
        if self._type == ConfigType.Dict_Without_Sections:
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

    def get_type(self) -> ConfigType:
        return self._type

    def more(self) -> bool:
        return self.get_reader().more()

    def read_i8(self, name: str = "") -> int:
        if self._type == ConfigType.Debug:
            self._read_param("i8", name)

        return self.get_reader().read_i8()

    def read_u8(self, name: str = "") -> int:
        if self._type == ConfigType.Debug:
            self._read_param("u8", name)

        return self.get_reader().read_u8()

    def read_i16(self, name: str = "") -> int:
        if self._type == ConfigType.Debug:
            self._read_param("i16", name)

        return self.get_reader().read_i16()

    def read_u16(self, name: str = "") -> int:
        if self._type == ConfigType.Debug:
            self._read_param("u16", name)

        return self.get_reader().read_u16()

    def read_i32(self, name: str = "") -> int:
        if self._type == ConfigType.Debug:
            self._read_param("i32", name)

        return self.get_reader().read_i32()

    def read_u32(self, name: str = "") -> int:
        if self._type == ConfigType.Debug:
            self._read_param("u32", name)

        return self.get_reader().read_u32()

    def read_fp32(self, name: str = "") -> float:
        if self._type == ConfigType.Debug:
            self._read_param("fp32", name)

        return self.get_reader().read_fp32()

    def read_bool(self, name: str = "") -> bool:
        if self._type == ConfigType.Debug:
            self._read_param("bool", name)

        return self.get_reader().read_bool()

    def read_bool8(self, name: str = "") -> Bool8:
        if self._type == ConfigType.Debug:
            self._read_param("bool8", name)

        r = Bool8()
        r.read(self.get_reader())

        return r

    def read_vec3i(self, name: str = "") -> Vec3I:
        if self._type == ConfigType.Debug:
            self._read_param("vec3i", name)

        v = Vec3I()
        v.read(self.get_reader())

        return v

    def read_vec4i(self, name: str = "") -> Vec4I:
        if self._type == ConfigType.Debug:
            self._read_param("vec4i", name)

        v = Vec4I()
        v.read(self.get_reader())

        return v

    def read_vec3f(self, name: str = "") -> Vec3F:
        if self._type == ConfigType.Debug:
            self._read_param("vec3f", name)

        v = Vec3F()
        v.read(self.get_reader())

        return v

    def read_vec4f(self, name: str = "") -> Vec4F:
        if self._type == ConfigType.Debug:
            self._read_param("vec4f", name)

        v = Vec4F()
        v.read(self.get_reader())

        return v

    def read_choose(self, name: str = ""):
        if self._type == ConfigType.Debug:
            self._read_param("choose", name)

        return self.read_str(name)

    def read_str(self, name: str = "", str_len: int = 0) -> str:
        if self._type == ConfigType.Debug:
            self._read_param("stringz", name)

        if self._type == ConfigType.Dict_Without_Sections:
            str_id = self.read_u32()
            strs_len = len(self._strings)

            if str_id >= strs_len:
                raise Exception(f"Incorrect String Index: {str_id} <> {strs_len}")

            return self._strings[str_id]

        return self.get_reader().read_str(str_len)

    def read_array(self, name: str = ""):
        if self._type == ConfigType.Debug:
            self._read_param("array", name)

        arr_rd = self.read_section(name)
        arr_count = arr_rd.read_u32("count")

        return arr_rd, arr_count

    def read_array_u8(self, name: str = ""):
        if self._type == ConfigType.Debug:
            self._read_param("u8_array", name)

        count = self.get_reader().read_u32()

        return [self.get_reader().read_u8() for _ in range(count)]

    def read_array_u16(self, name: str = ""):
        if self._type == ConfigType.Debug:
            self._read_param("u16_array", name)

        count = self.get_reader().read_u32()

        return [self.get_reader().read_u16() for _ in range(count)]

    def read_array_u32(self, name: str = ""):
        if self._type == ConfigType.Debug:
            self._read_param("u32_array", name)

        count = self.get_reader().read_u32()

        return [self.get_reader().read_u32() for _ in range(count)]

    def read_section(self, name: str = ""):
        if self._type == ConfigType.Dict_Without_Sections:
            return self

        crc32 = self.get_reader().read_u32()
        size = self.get_reader().read_u32()

        if not (name and zlib.crc32(name.encode()) == crc32):
            raise Exception(f"CRC32 Calculate Error: {name} <> {crc32}")

        rd = MetroReader(content_path=self.get_reader().get_content_path(), data=self.get_reader().get_bytes(size))
        conf_rd = ConfigReader(rd)

        if self._type != conf_rd._type:
            raise Exception(f"Config Type Not Equal Section Type: {self._type} <> {conf_rd._type}")

        if conf_rd._type == ConfigType.Debug:
            debug_name = conf_rd.get_reader().read_str()

            if debug_name != name:
                raise Exception(f"Debug Name <> Section Name: {debug_name} <> {name}")

        return conf_rd

    def read_typed(self, tp: str, name: str = "") -> dict:
        debug_name, debug_type = self._read_param(tp, name)

        return {f"{debug_name}.{debug_type}": self._typed_strings[tp]()}

    def _read_param(self, expected_type: str, expected_name: str = "") -> [str, str]:
        debug_name = self.get_reader().read_str()
        debug_type = self.get_reader().read_str()

        if expected_name != "" and debug_name != expected_name:
            raise Exception(f"Debug Name <> Expected Name: {debug_name} <> {expected_name}")

        if expected_type == "" or debug_type != expected_type:
            raise Exception(f"Debug Type <> Expected Type: {debug_name} <> {expected_type}")

        if not (debug_type in self._typed_strings):
            raise Exception(f"Unknown Param Type: {debug_type}")

        return debug_name, debug_type
