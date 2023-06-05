import os
import dataclasses

from io_metro.blender.formats.model import *


LEVEL_VERSION_REDUX = 16
LEVEL_VERSION_EXODUS = 19

#  Level Chunk's IDs
LEVEL_VER_ID = 1
LEVEL_MAT_ID = 2
LEVEL_REF_ID = 3
LEVEL_CRC_ID = 11

# Level Geometry Chunk's IDs
LEVEL_VB_ID = 9
LEVEL_FB_ID = 10


@dataclasses.dataclass
class LevelMaterial:
    shader: str = ""
    texture: str = ""
    material: str = ""
    flags: int = 0

    def read(self, reader: MetroReader):
        self.shader = reader.read_str()
        self.texture = reader.make_content_path(fr"textures\{reader.read_str()}")
        self.material = reader.read_str()
        self.flags = reader.read_u32()


@dataclasses.dataclass
class LevelVertex:
    position: Vec3F = dataclasses.field(default_factory=Vec3F)
    normal: int = 0
    aux0: int = 0
    aux1: int = 0
    uv0: Vec2S = dataclasses.field(default_factory=Vec2S)
    uv1: Vec2S = dataclasses.field(default_factory=Vec2S)

    def read(self, reader: MetroReader):
        self.position.read(reader)
        self.normal = reader.read_u32()
        self.aux0 = reader.read_u32()
        self.aux1 = reader.read_u32()
        self.uv0.read(reader)
        self.uv1.read(reader)


@dataclasses.dataclass
class LevelFace:
    a: int = 0
    b: int = 0
    c: int = 0

    def read(self, reader: MetroReader):
        self.a = reader.read_u16()
        self.b = reader.read_u16()
        self.c = reader.read_u16()


@dataclasses.dataclass
class LevelRef:
    vertex_type: int = 0

    vertex_offset = 0
    vertex_count: int = 0
    shadow_vertex_count: int = 0

    faces_offset = 0
    faces_count: int = 0
    shadow_faces_count: int = 0

    def read(self, reader: MetroReader, version: int = LEVEL_VERSION_REDUX):
        self.vertex_type = reader.read_u32()
        self.vertex_offset = reader.read_u32()
        self.vertex_count = reader.read_u32()

        if version > LEVEL_VERSION_REDUX:
            self.shadow_vertex_count = reader.read_u32()

        self.faces_offset = reader.read_u32()
        self.faces_count = reader.read_u32()

        if version > LEVEL_VERSION_REDUX:
            self.shadow_faces_count = reader.read_u32()


@dataclasses.dataclass
class LevelMesh:
    ref: LevelRef = dataclasses.field(default_factory=LevelRef)
    header: ModelHeader = dataclasses.field(default_factory=ModelHeader)
    material: ModelMaterial = dataclasses.field(default_factory=ModelMaterial)

    def read(self, reader: MetroReader, version: int = LEVEL_VERSION_REDUX):
        self.ref = LevelRef()
        self.header = ModelHeader()
        self.material = ModelMaterial()

        self.header.version = MetroVersion.Exodus.value

        while reader.more():
            chunk = Chunk()
            chunk.read(reader)

            if chunk.id == ModelChunkType.MeshRef.value:
                self.ref.read(chunk.reader, version)

            if chunk.id == ModelChunkType.HeaderChunk.value:
                self.header.read(chunk.reader)

            if chunk.id == ModelChunkType.MaterialsChunk.value:
                self.material.read(chunk.reader, self.header)


@dataclasses.dataclass
class LevelPart:
    vertex: List[LevelVertex] = dataclasses.field(default_factory=list)
    faces: List[LevelFace] = dataclasses.field(default_factory=list)

    material: LevelMaterial = dataclasses.field(default_factory=LevelMaterial)


@dataclasses.dataclass
class LevelVersion:
    version: int = 0
    flags: int = 0

    def read(self, reader: MetroReader):
        self.version = reader.read_u16()
        self.flags = reader.read_u16()


@dataclasses.dataclass
class LevelChecksum:
    crc32: int = 0

    def read(self, reader: MetroReader):
        self.crc32 = reader.read_u32()


@dataclasses.dataclass
class LevelMeshes:
    meshes: List[LevelMesh] = dataclasses.field(default_factory=list)

    def read(self, reader: MetroReader, version: int = LEVEL_VERSION_REDUX):
        while reader.more():
            child = Chunk()
            child.read(reader)

            mesh = LevelMesh()
            mesh.read(child.reader, version)

            self.meshes.append(mesh)


@dataclasses.dataclass
class LevelMaterials:
    materials: List[LevelMaterial] = dataclasses.field(default_factory=list)

    def read(self, reader: MetroReader):
        self.materials = []

        for _ in range(reader.read_u16()):
            mat = LevelMaterial()
            mat.read(reader)

            self.materials.append(mat)


@dataclasses.dataclass
class LevelVertexBuffer:
    vertex: List[LevelVertex] = dataclasses.field(default_factory=list)

    def read(self, reader: MetroReader, version: int = LEVEL_VERSION_REDUX):
        self.vertex = []

        if version > LEVEL_VERSION_REDUX:
            vertex_count = reader.read_u32()
            shadow_vertex_count = reader.read_u32()

        while reader.more():
            vertex = LevelVertex()
            vertex.read(reader)

            self.vertex.append(vertex)


@dataclasses.dataclass
class LevelFacesBuffer:
    faces: List[LevelFace] = dataclasses.field(default_factory=list)

    def read(self, reader: MetroReader, version: int = LEVEL_VERSION_REDUX):
        self.faces = []

        if version > LEVEL_VERSION_REDUX:
            faces_count = reader.read_u32()
            shadow_faces_count = reader.read_u32()

        while reader.more():
            face = LevelFace()
            face.read(reader)

            self.faces.append(face)


@dataclasses.dataclass
class LevelSectors:
    version: LevelVersion = dataclasses.field(default_factory=LevelVersion)
    checksum: LevelChecksum = dataclasses.field(default_factory=LevelChecksum)
    sectors: LevelMeshes = dataclasses.field(default_factory=LevelMeshes)
    materials: LevelMaterials = dataclasses.field(default_factory=LevelMaterials)

    def read(self, reader: MetroReader):
        self.version = LevelVersion()
        self.checksum = LevelChecksum()
        self.sectors = LevelMeshes()
        self.materials = LevelMaterials()

        while reader.more():
            chunk = Chunk()
            chunk.read(reader)

            if chunk.id == LEVEL_VER_ID:
                self.version.read(chunk.reader)

            if chunk.id == LEVEL_CRC_ID:
                self.checksum.read(chunk.reader)

            if chunk.id == LEVEL_REF_ID:
                self.sectors.read(chunk.reader, self.version.version)

            if chunk.id == LEVEL_MAT_ID:
                self.materials.read(chunk.reader)


@dataclasses.dataclass
class LevelGeometry:
    version: LevelVersion = dataclasses.field(default_factory=LevelVersion)
    checksum: LevelChecksum = dataclasses.field(default_factory=LevelChecksum)
    vertex_buffer: LevelVertexBuffer = dataclasses.field(default_factory=LevelVertexBuffer)
    faces_buffer: LevelFacesBuffer = dataclasses.field(default_factory=LevelFacesBuffer)

    def read(self, reader: MetroReader):
        self.version = LevelVersion()
        self.checksum = LevelChecksum()
        self.vertex_buffer = LevelVertexBuffer()
        self.faces_buffer = LevelFacesBuffer()

        while reader.more():
            chunk = Chunk()
            chunk.read(reader)

            if chunk.id == LEVEL_VER_ID:
                self.version.read(chunk.reader)

            if chunk.id == LEVEL_CRC_ID:
                self.checksum.read(chunk.reader)

            if chunk.id == LEVEL_VB_ID:
                self.vertex_buffer.read(chunk.reader, self.version.version)

            if chunk.id == LEVEL_FB_ID:
                self.faces_buffer.read(chunk.reader, self.version.version)


@dataclasses.dataclass
class Level:
    level_parts: List[LevelPart] = dataclasses.field(default_factory=list)

    def read(self, geom_path: str):
        geom_path = geom_path.strip()
        sect_path = geom_path.replace(".geom_pc", "")

        if not (os.path.isfile(geom_path) and os.path.isfile(sect_path)):
            raise Exception("Level's paths not exists!")

        geom_reader, sect_reader = MetroReader(bin_path=geom_path), MetroReader(bin_path=sect_path)

        self.level_parts = []

        sectors = LevelSectors()
        sectors.read(sect_reader)

        geometry = LevelGeometry()
        geometry.read(geom_reader)

        i = 0

        for section in sectors.sectors.meshes:
            v_offset = section.ref.vertex_offset
            v_size = section.ref.vertex_count

            f_offset = int(section.ref.faces_offset / 3)
            f_size = int(section.ref.faces_count / 3)

            vertex = geometry.vertex_buffer.vertex[v_offset:(v_offset + v_size)]
            faces = geometry.faces_buffer.faces[f_offset:(f_offset + f_size)]

            material = sectors.materials.materials[section.header.shader_id] \
                if section.header.shader_id <= len(sectors.materials.materials) \
                else None

            if not material and section.material:
                material = LevelMaterial(shader=section.material.shader,
                                         texture=section.material.texture,
                                         material=section.material.material,
                                         flags=section.material.flag0 | section.material.flag1)

            if (vertex and faces) and material:
                part = LevelPart(vertex=vertex, faces=faces, material=material)

                self.level_parts.append(part)
