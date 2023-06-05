import dataclasses

from io_metro.blender.formats.chunk import *


@dataclasses.dataclass
class CSurface:
    shader: str = ""
    texture: str = ""
    material: str = ""
    name: str = ""

    def read(self, reader: MetroReader, version: int = 0):
        s_len = reader.read_u32()
        self.shader = reader.read_str(s_len)

        t_len = reader.read_u32()
        self.texture = reader.read_str(t_len)

        m_len = reader.read_u32()
        self.material = reader.read_str(m_len)

        if version >= 5:
            n_len = reader.read_u32()
            self.name = reader.read_str(n_len)


@dataclasses.dataclass
class CMesh:
    is_geo: bool = False
    surface: CSurface = CSurface()


@dataclasses.dataclass
class CForm:
    is_le: bool = False
    flags: int = 0

    version: int = 0
    checksum: int = 0

    meshes_count: int = 0
