"""
Mesh Common Structures
"""
import dataclasses
from typing import List
from pathlib import Path

from io_metro.blender.formats.math import *
from io_metro.blender.formats.chunk import *
from io_metro.blender.formats.reader import MetroReader
from io_metro.blender.formats.skeleton import Skeleton
from io_metro.blender.formats.config_reader import ConfigReader


class ModelChunkType(enum.Enum):
    HeaderChunk = 1
    MaterialsChunk = 2
    VerticesChunk = 3
    FacesChunk = 4
    SkinnedVerticesChunk = 5
    ChildrenChunk = 9
    ChildrenRefsChunk = 10
    Lod_1_Chunk = 11
    Lod_2_Chunk = 12
    SkeletonBonesCRC = 13
    MeshesInline = 15
    MeshesLinks = 16
    HitPresetAndMtls = 18
    MotionsFolders = 19  # 2033 Vanilla Only
    SkeletonLink = 20
    MeshRef = 21
    SkeletonInline = 24
    PhysXLinks = 25
    TexturesReplacements = 29  # 2033 Vanilla Only
    Voice = 31
    TexturesPresets = 32
    Comment = 36

    """
    34 - motion substs
    38 - fur desk
    """


class ModelType(enum.Enum):
    Std = 0
    Hierarchy = 1
    Skeleton = 2
    Skeleton2 = 3  # SHIT
    Hierarchy_Skinned = 4  # skinned lod mesh hierarchy type
    Skin = 5
    Soft = 8
    ParticlesEffect = 11
    ParticlesSystem = 12
    Skeleton3 = 13


class VertexType(enum.Enum):
    Invalid = 0
    Skin = 1
    Static = 2
    Level = 3
    LevelLegacy = 4
    Particle = 16
    Soft = 17
    Impostor = 19
    SkinNB = 25


@dataclasses.dataclass
class Face:
    a: int = 0
    b: int = 0
    c: int = 0

    def read(self, reader: MetroReader):
        self.a = reader.read_u16()
        self.b = reader.read_u16()
        self.c = reader.read_u16()


@dataclasses.dataclass
class VertexSkinned:
    position: Vec4S = dataclasses.field(default_factory=Vec4S)
    normal: int = 0
    aux0: int = 0
    aux1: int = 0
    bones: Vec4UB = dataclasses.field(default_factory=Vec4UB)
    weights: Vec4UB = dataclasses.field(default_factory=Vec4UB)
    uv: Vec2S = dataclasses.field(default_factory=Vec2S)

    def read(self, reader: MetroReader):
        self.position.read(reader)
        self.normal = reader.read_u32()
        self.aux0 = reader.read_u32()
        self.aux1 = reader.read_u32()
        self.bones.read(reader)
        self.weights.read(reader)
        self.uv.read(reader)


@dataclasses.dataclass
class VertexSkinnedShadow:
    position: Vec4S = dataclasses.field(default_factory=Vec4S)
    bones: Vec4UB = dataclasses.field(default_factory=Vec4UB)
    weights: Vec4UB = dataclasses.field(default_factory=Vec4UB)

    def read(self, reader: MetroReader):
        self.position.read(reader)
        self.bones.read(reader)
        self.weights.read(reader)


@dataclasses.dataclass
class VertexStatic:
    position: Vec3F = dataclasses.field(default_factory=Vec3F)
    normal: int = 0
    aux0: int = 0
    aux1: int = 0
    uv: Vec2F = dataclasses.field(default_factory=Vec2F)

    def read(self, reader: MetroReader):
        self.position.read(reader)

        self.normal = reader.read_u32()
        self.aux0 = reader.read_u32()
        self.aux1 = reader.read_u32()

        self.uv.read(reader)


@dataclasses.dataclass
class VertexStaticShadow:
    position: Vec3F = dataclasses.field(default_factory=Vec3F)
    padding: int = 0

    def read(self, reader: MetroReader):
        self.position.read(reader)
        self.padding = reader.read_u32()


@dataclasses.dataclass
class ModelHeader:
    version: int = MetroVersion.OG_2033_Release.value
    type: int = 0
    shader_id: int = 0
    border_box: BBox = dataclasses.field(default_factory=BBox)
    border_sphere: BSphere = dataclasses.field(default_factory=BSphere)
    check_sum: int = 0
    invalid_lod: float = 0
    flags: int = 0
    vertex_scale: float = 0
    texture_density: float = 0

    def read(self, reader: MetroReader):
        self.version = reader.read_u8()
        self.type = reader.read_u8()
        self.shader_id = reader.read_u16()
        self.border_box.read(reader)
        self.border_sphere.read(reader)
        self.check_sum = reader.read_u32()
        self.invalid_lod = reader.read_fp32()
        self.flags = reader.read_u32()
        self.vertex_scale = reader.read_fp32()
        self.texture_density = reader.read_fp32()

        if self.version == 29 or self.version == MetroVersion.Arktika1_Early.value:
            t = self.border_box.maximum - self.border_box.minimal
            self.vertex_scale = max(abs(t.x), abs(t.y), abs(t.z))

        if self.version < 29:
            self.vertex_scale = 12

    def get_type(self):
        return ModelType(self.type)

    def get_version(self):
        return MetroVersion(self.version)


@dataclasses.dataclass
class ModelMaterial:
    texture: str = ""
    shader: str = ""
    material: str = ""

    name: str = ""
    flag0: int = 0
    flag1: int = 0

    is_collision: bool = False

    def read(self, reader: MetroReader, header: ModelHeader):
        self.texture = reader.make_content_path(fr"textures\{reader.read_str()}")

        self.shader = reader.read_str()
        self.material = reader.read_str()

        if header and header.version >= MetroVersion.OG_LastLight_Release.value:
            self.name = reader.read_str()
            self.flag0 = reader.read_u16()

            if reader.more():
                self.flag1 = reader.read_u16()
            else:
                self.flag1 = -1

            self.is_collision = 0 != (self.flag0 & 8)


@dataclasses.dataclass
class ModelVertex:
    vertex: List[VertexStatic] = dataclasses.field(default_factory=list)
    shadow_vertex: List[VertexStaticShadow] = dataclasses.field(default_factory=list)

    vertex_type: int = 0
    vertex_count: int = 0
    shadow_vertex_count: int = 0

    def read(self, reader: MetroReader, header: ModelHeader):
        self.vertex_type = reader.read_u32()
        self.vertex_count = reader.read_u32()

        if header and header.version >= MetroVersion.Arktika1_Early.value:
            self.shadow_vertex_count = reader.read_u16()

        if self.vertex_type != VertexType.Static.value:
            raise Exception(
                f"Incorrect Vertex Type: {self.vertex_type} <> {VertexType.Static.value}; VC: {self.vertex_count}")

        self.vertex = []
        self.shadow_vertex = []

        for i in range(self.vertex_count):
            v = VertexStatic()
            v.read(reader)

            self.vertex.append(v)

        for i in range(self.shadow_vertex_count):
            v = VertexStaticShadow()
            v.read(reader)

            self.shadow_vertex.append(v)


@dataclasses.dataclass
class ModelFaces:
    faces: List[Face] = dataclasses.field(default_factory=list)
    shadow_faces: List[Face] = dataclasses.field(default_factory=list)

    faces_count: int = 0
    shadow_faces_count: int = 0

    def read(self, reader: MetroReader, header: ModelHeader):
        if header and header.get_type() == ModelType.Skin:
            self.faces_count = reader.read_u16()
        else:
            self.faces_count = reader.read_u32()

        if header and header.version >= MetroVersion.Arktika1_Early.value:
            self.shadow_faces_count = reader.read_u16()
        else:
            self.faces_count = int(self.faces_count / 3)

        self.faces = []
        self.shadow_faces = []

        for i in range(self.faces_count):
            f = Face()
            f.read(reader)

            self.faces.append(f)

        for i in range(self.shadow_faces_count):
            f = Face()
            f.read(reader)

            self.shadow_faces.append(f)


@dataclasses.dataclass
class ModelSkinnedVertex:
    bone_count: int = 0
    vertex_count: int = 0
    shadow_vertex_count: int = 0

    bone_IDs: List[int] = dataclasses.field(default_factory=list)
    bone_OBBs: List[OBBox] = dataclasses.field(default_factory=list)

    skinned_vertex: List[VertexSkinned] = dataclasses.field(default_factory=list)
    skinned_vertex_shadow: List[VertexSkinnedShadow] = dataclasses.field(default_factory=list)

    def read(self, reader: MetroReader, header: ModelHeader):
        self.bone_count = reader.read_u8()

        self.bone_IDs = [reader.read_u8() for i in range(self.bone_count)]
        self.bone_OBBs = []

        for i in range(self.bone_count):
            obb = OBBox()
            obb.read(reader)

            self.bone_OBBs.append(obb)

        self.vertex_count = reader.read_u32()

        if header and header.version >= MetroVersion.Arktika1_Early.value:
            self.shadow_vertex_count = reader.read_u16()

        self.skinned_vertex = []
        self.skinned_vertex_shadow = []

        for i in range(self.vertex_count):
            v = VertexSkinned()
            v.read(reader)

            self.skinned_vertex.append(v)

        for i in range(self.shadow_vertex_count):
            v = VertexSkinnedShadow()
            v.read(reader)

            self.skinned_vertex_shadow.append(v)


@dataclasses.dataclass
class ModelCRC:
    crc: int = 0

    def read(self, reader: MetroReader):
        self.crc = reader.read_u32()


@dataclasses.dataclass
class ModelBase:
    header: ModelHeader = dataclasses.field(default_factory=ModelHeader)
    material: ModelMaterial = dataclasses.field(default_factory=ModelMaterial)


@dataclasses.dataclass
class ModelStd(ModelBase):
    vertex: ModelVertex = dataclasses.field(default_factory=ModelVertex)
    faces: ModelFaces = dataclasses.field(default_factory=ModelFaces)

    def read(self, reader: MetroReader):
        while reader.more():
            chunk = Chunk()
            chunk.read(reader)

            if chunk.id == ModelChunkType.HeaderChunk.value:
                self.header = ModelHeader()
                self.header.read(chunk.reader)

            if chunk.id == ModelChunkType.MaterialsChunk.value:
                self.material = ModelMaterial()
                self.material.read(chunk.reader, self.header)

            if chunk.id == ModelChunkType.VerticesChunk.value:
                self.vertex.read(chunk.reader, self.header)

            if chunk.id == ModelChunkType.FacesChunk.value:
                self.faces.read(chunk.reader, self.header)


@dataclasses.dataclass
class Mesh(ModelBase):
    skinned_vertex: ModelSkinnedVertex = dataclasses.field(default_factory=ModelSkinnedVertex)
    faces: ModelFaces = dataclasses.field(default_factory=ModelFaces)

    def read(self, reader: MetroReader):
        while reader.more():
            chunk = Chunk()
            chunk.read(reader)

            if chunk.id == ModelChunkType.HeaderChunk.value:
                self.header = ModelHeader()
                self.header.read(chunk.reader)

            if chunk.id == ModelChunkType.MaterialsChunk.value:
                self.material = ModelMaterial()
                self.material.read(chunk.reader, self.header)

            if chunk.id == ModelChunkType.SkinnedVerticesChunk.value:
                self.skinned_vertex.read(chunk.reader, self.header)

            if chunk.id == ModelChunkType.FacesChunk.value:
                self.faces.read(chunk.reader, self.header)


@dataclasses.dataclass
class ModelSkeleton:
    crc: ModelCRC = dataclasses.field(default_factory=ModelCRC)
    skeleton: Skeleton = dataclasses.field(default_factory=Skeleton)

    lod0: List[Mesh] = dataclasses.field(default_factory=list)
    lod1: List[Mesh] = dataclasses.field(default_factory=list)
    lod2: List[Mesh] = dataclasses.field(default_factory=list)

    def read(self, reader: MetroReader):
        def read_lod(lod_reader: MetroReader, lod_n: List[Mesh]):
            m = Model()
            m.read(lod_reader)

            lod_n.extend(m.meshes)

        while reader.more():
            chunk = Chunk()
            chunk.read(reader)

            if chunk.id == ModelChunkType.SkeletonBonesCRC.value:
                self.crc.read(reader)

            if chunk.id == ModelChunkType.SkeletonLink:
                sk_path = chunk.reader.make_content_path(fr"meshes\{chunk.reader.read_str()}.skeleton.bin")

                sk_reader = MetroReader(bin_path=sk_path)
                config_reader = ConfigReader(sk_reader)

                self.skeleton.read(config_reader)

            if chunk.id == ModelChunkType.MeshesLinks.value:
                links_count = chunk.reader.read_u32()

                if links_count != 3:
                    raise Exception(f"Links Count Must Be 3: {links_count} <> 3")

                lod0_path, lod1_path, lod2_path = [
                    chunk.reader.make_content_path(fr"meshes\{chunk.reader.read_str()}.mesh")
                    for i in range(links_count)
                ]

                if lod0_path:
                    lod0_reader = MetroReader(bin_path=lod0_path)
                    read_lod(lod0_reader, self.lod0)

                if lod1_path:
                    lod1_reader = MetroReader(bin_path=lod1_path)
                    read_lod(lod1_reader, self.lod1)

                if lod2_path:
                    lod2_reader = MetroReader(bin_path=lod2_path)
                    read_lod(lod2_reader, self.lod2)

            if chunk.id == ModelChunkType.MeshesInline.value:
                lod0_chunk = Chunk()
                lod0_chunk.read(chunk.reader)

                lod1_chunk = Chunk()
                lod1_chunk.read(chunk.reader)

                lod2_chunk = Chunk()
                lod2_chunk.read(chunk.reader)

                #  LOD0
                self.lod0 = []

                while lod0_chunk.reader.more():
                    part_chunk = Chunk()
                    part_chunk.read(lod0_chunk.reader)

                    read_lod(part_chunk.reader, self.lod0)

                #  LOD1
                self.lod1 = []

                while lod1_chunk.reader.more():
                    part_chunk = Chunk()
                    part_chunk.read(lod1_chunk.reader)

                    read_lod(part_chunk.reader, self.lod1)

                #  LOD2
                self.lod2 = []

                while lod2_chunk.reader.more():
                    part_chunk = Chunk()
                    part_chunk.read(lod2_chunk.reader)

                    read_lod(part_chunk.reader, self.lod2)


class Model:
    meshes: List[Mesh] = dataclasses.field(default_factory=list)
    visuals: List[ModelStd] = dataclasses.field(default_factory=list)
    model_skeleton: ModelSkeleton = dataclasses.field(default_factory=ModelSkeleton)

    def __init__(self):
        self.meshes = []
        self.visuals = []
        self.model_skeleton = ModelSkeleton()

    def read(self, reader: MetroReader):
        header = self._read_header(reader)

        if not header:
            return

        m_type = header.get_type()
        reader.offset = 0

        if m_type == ModelType.Std:
            self._read_std(reader)

        if m_type == ModelType.Skin:
            self._read_skin(reader)

        if m_type == ModelType.Skeleton or m_type == ModelType.Skeleton2 or m_type == ModelType.Skeleton3:
            self._read_skeleton(reader)

        if m_type == ModelType.Hierarchy or m_type == ModelType.Hierarchy_Skinned:
            self._read_hierarchy(reader)

    def _read_header(self, reader: MetroReader):
        chunk = Chunk.find_chunk_by_id(reader, ModelChunkType.HeaderChunk.value)

        if not chunk:
            return

        header = ModelHeader()
        header.read(chunk.reader)

        return header

    def _read_std(self, reader: MetroReader):
        std = ModelStd()
        std.read(reader)

        self.visuals.append(std)

    def _read_skin(self, reader: MetroReader):
        mesh = Mesh()
        mesh.read(reader)

        self.meshes.append(mesh)

    def _read_skeleton(self, reader: MetroReader):
        self.model_skeleton = ModelSkeleton()
        self.model_skeleton.read(reader)

    def _read_hierarchy(self, reader: MetroReader):
        children = Chunk.find_chunk_by_id(reader, ModelChunkType.ChildrenChunk.value)

        if not children:
            return

        reader = children.reader

        while reader.more():
            child = Chunk()
            child.read(reader)

            self.read(child.reader)
