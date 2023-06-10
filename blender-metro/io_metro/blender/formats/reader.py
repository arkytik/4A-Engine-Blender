import struct


class MetroReader:
    data: bytes

    size: int
    offset: int

    file_path: str

    def __init__(self, content_path: str = None, bin_path: str = None, data: bytes = None):
        if content_path:
            self.file_path = content_path

        if bin_path:
            with open(bin_path, 'rb+') as fb:
                self.data = fb.read()

            self.size = len(self.data)
            self.offset = 0

            self.file_path = bin_path
        else:
            self.data = data

            self.size = len(self.data)
            self.offset = 0

        if not self.file_path:
            raise Exception("Reader Must Contains File Path Or Path To Content")

    def get_content_path(self) -> str:
        try:
            c = self.file_path.index("content")

            path = self.file_path[0:c].strip("\\") if self.file_path else None

            if path:
                return fr"{path}\content"

            return path
        except ValueError:
            return fr"{self.file_path}\content"

    def make_content_path(self, part_path: str) -> str:
        return fr"{self.get_content_path()}\{part_path}"

    def more(self) -> bool:
        return self.offset < self.size

    def get_bytes(self, count: int) -> bytes:
        self.offset += count

        return self.data[(self.offset - count):self.offset]

    def get_struct(self, fmt: str) -> tuple:
        struct_size = struct.calcsize(fmt)

        return struct.unpack(fmt, self.get_bytes(struct_size))

    def read_i8(self) -> int:
        b = self.get_struct("@b")[0]

        return int(b)

    def read_u8(self) -> int:
        b = self.get_struct("@B")[0]

        return int(b)

    def read_i16(self) -> int:
        b = self.get_struct("@h")[0]

        return int(b)

    def read_u16(self) -> int:
        b = self.get_struct("@H")[0]

        return int(b)

    def read_i32(self) -> int:
        b = self.get_struct("@i")[0]

        return int(b)

    def read_u32(self) -> int:
        b = self.get_struct("@I")[0]

        return int(b)

    def read_fp32(self) -> float:
        b = self.get_struct("@f")[0]

        return float(b)

    def read_double(self) -> float:
        b = self.get_struct("@d")[0]

        return float(b)

    def read_bool(self) -> bool:
        r = self.read_u8()

        if r == 0:
            return False

        if r == 1:
            return True

        raise Exception(f"Incorrect Value Of Bool: {r}")

    def read_str(self, str_len: int = 0) -> str:
        r = ""

        while self.more() or str_len > 0:
            c = self.read_u8()

            if 0 < c < 127:
                r += chr(c)
            else:
                return r

            if str_len > 0:
                str_len -= 1
