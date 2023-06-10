import dataclasses

from typing import List

from io_metro.blender.formats.math import *
from io_metro.blender.formats.chunk import *


@dataclasses.dataclass
class CTriangle:
    vector0: Vec3F = dataclasses.field(default_factory=Vec3F)
    vector1: Vec3F = dataclasses.field(default_factory=Vec3F)
    vector2: Vec3F = dataclasses.field(default_factory=Vec3F)

    def read(self, reader: MetroReader):
        self.vector0.read(reader)
        self.vector1.read(reader)
        self.vector2.read(reader)


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

        if version > 8:
            n_len = reader.read_u32()
            self.name = reader.read_str(n_len)


@dataclasses.dataclass
class CMesh:
    is_geo: bool = False
    surface: CSurface = dataclasses.field(default_factory=CSurface)
    mesh_index: int = 0  # 65535 In Mesh OR Index Of Level

    is_nxs: bool = False
    nxs_size: int = 0
    nxs_header_1: int = 0
    nxs_header_2: int = 0

    flags: int = 0              # ALWAYS 12
    vertex_count: int = 0
    vertex_size: int = 0        # 12 -> float, 24 -> double
    triangles_count: int = 0
    triangles_size: int = 0     # 3 -> byte, 6 -> word, 12 -> dword

    vertex: List[Vec3F] = dataclasses.field(default_factory=list)
    triangles: List[CTriangle] = dataclasses.field(default_factory=list)

    indies: List[int] = dataclasses.field(default_factory=list)

    def read(self, reader: MetroReader, version: int = 0):
        self.is_geo = reader.read_bool()
        self.surface.read(reader, version)
        self.mesh_index = reader.read_u32()

        self.is_nxs = reader.read_bool()
        self.nxs_size = reader.read_u32()

        reader = MetroReader(content_path=reader.get_content_path(), data=reader.get_bytes(self.nxs_size))

        self.nxs_header_1, self.nxs_header_2 = reader.read_u32(), reader.read_u32()

        if not self.is_nxs:
            raise Exception("Isn't NXS MESH")

        self.flags = reader.read_u32()

        self.vertex_count = reader.read_u32()

        if self.flags == 12:
            self.vertex_size = int(reader.read_fp32())
        elif self.flags == 24:
            self.vertex_size = int(reader.read_double())

        self.triangles_count = reader.read_u32()

        if self.flags == 3:
            self.triangles_size = reader.read_u8()
        elif self.flags == 6:
            self.triangles_size = reader.read_u16()
        elif self.flags == 12:
            self.triangles_size = reader.read_u32()

        self.vertex = []

        if self.vertex_size != 0:
            for _ in range(self.vertex_count):
                v = Vec3F()
                v.read(reader)

                self.vertex.append(v)

        if self.triangles_size != 0:
            self.triangles = []
            for _ in range(self.triangles_count):
                t = CTriangle()
                t.read(reader)

                self.triangles.append(t)

        self.indies = []
        while reader.more():
            self.indies.append(reader.read_u8())


@dataclasses.dataclass
class CForm:
    is_le: bool = False
    flags: int = 0

    version: int = 0
    checksum: int = 0

    meshes_count: int = 0
    meshes: List[CMesh] = dataclasses.field(default_factory=list)

    def read(self, reader: MetroReader):
        self.is_le = reader.read_bool()
        self.flags = reader.read_u32()

        self.version = reader.read_u32()
        self.checksum = reader.read_u32()

        self.meshes = []
        self.meshes_count = reader.read_u32()
        for _ in range(self.meshes_count):
            mesh = CMesh()
            mesh.read(reader, self.version)

            self.meshes.append(mesh)
