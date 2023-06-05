import enum
import dataclasses

from io_metro.blender.formats.reader import MetroReader


class MetroVersion(enum.Enum):
    OG_2033_Early = 7  # Some Old Steam Models
    OG_2033_Release = 8  # Highest Original (2010) Version
    OG_LastLight_Early = 17  # 18 On XBox Builds
    OG_LastLight_Release = 20  # 20/21 On Release
    Redux = 23
    Arktika1_Early = 30
    Arktika1_Release = 31
    Exodus = 42


@dataclasses.dataclass
class Chunk:
    id: int = 0
    size: int = 0

    reader: MetroReader = None

    def read(self, reader: MetroReader):
        self.id = reader.read_u32()
        self.size = reader.read_u32()

        self.reader = MetroReader(content_path=reader.get_content_path(), data=reader.get_bytes(self.size))

        print("Chunk", self.id, self.size)

    @staticmethod
    def find_chunk_by_id(reader: MetroReader, chunk_id: int):
        while reader.more():
            chunk = Chunk()
            chunk.read(reader)

            if chunk.id == chunk_id:
                return chunk

        return None
