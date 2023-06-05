import dataclasses

from io_metro.blender.formats.reader import MetroReader


@dataclasses.dataclass
class Vec2B:
    x: int = 0
    y: int = 0

    def read(self, reader: MetroReader):
        self.x = reader.read_i8()
        self.y = reader.read_i8()


@dataclasses.dataclass
class Vec3B:
    x: int = 0
    y: int = 0
    z: int = 0

    def read(self, reader: MetroReader):
        self.x = reader.read_i8()
        self.y = reader.read_i8()
        self.z = reader.read_i8()


@dataclasses.dataclass
class Vec4B:
    x: int = 0
    y: int = 0
    z: int = 0
    w: int = 0

    def read(self, reader: MetroReader):
        self.x = reader.read_i8()
        self.y = reader.read_i8()
        self.z = reader.read_i8()
        self.w = reader.read_i8()


@dataclasses.dataclass
class Vec2UB:
    x: int = 0
    y: int = 0

    def read(self, reader: MetroReader):
        self.x = reader.read_u8()
        self.y = reader.read_u8()


@dataclasses.dataclass
class Vec3UB:
    x: int = 0
    y: int = 0
    z: int = 0

    def read(self, reader: MetroReader):
        self.x = reader.read_u8()
        self.y = reader.read_u8()
        self.z = reader.read_u8()


@dataclasses.dataclass
class Vec4UB:
    x: int = 0
    y: int = 0
    z: int = 0
    w: int = 0

    def read(self, reader: MetroReader):
        self.x = reader.read_u8()
        self.y = reader.read_u8()
        self.z = reader.read_u8()
        self.w = reader.read_u8()


@dataclasses.dataclass
class Vec2S:
    x: int = 0
    y: int = 0

    def read(self, reader: MetroReader):
        self.x = reader.read_i16()
        self.y = reader.read_i16()


@dataclasses.dataclass
class Vec3S:
    x: int = 0
    y: int = 0
    z: int = 0

    def read(self, reader: MetroReader):
        self.x = reader.read_i16()
        self.y = reader.read_i16()
        self.z = reader.read_i16()


@dataclasses.dataclass
class Vec4S:
    x: int = 0
    y: int = 0
    z: int = 0
    w: int = 0

    def read(self, reader: MetroReader):
        self.x = reader.read_i16()
        self.y = reader.read_i16()
        self.z = reader.read_i16()
        self.w = reader.read_i16()


@dataclasses.dataclass
class Vec2I:
    x: int = 0
    y: int = 0

    def read(self, reader: MetroReader):
        self.x = reader.read_i32()
        self.y = reader.read_i32()


@dataclasses.dataclass
class Vec3I:
    x: int = 0
    y: int = 0
    z: int = 0

    def read(self, reader: MetroReader):
        self.x = reader.read_i32()
        self.y = reader.read_i32()
        self.z = reader.read_i32()


@dataclasses.dataclass
class Vec4I:
    x: int = 0
    y: int = 0
    z: int = 0
    w: int = 0

    def read(self, reader: MetroReader):
        self.x = reader.read_i32()
        self.y = reader.read_i32()
        self.z = reader.read_i32()
        self.w = reader.read_i32()


@dataclasses.dataclass
class Vec2F:
    x: float = 0
    y: float = 0

    def read(self, reader: MetroReader):
        self.x = reader.read_fp32()
        self.y = reader.read_fp32()


@dataclasses.dataclass
class Vec3F:
    x: float = 0
    y: float = 0
    z: float = 0

    def read(self, reader: MetroReader):
        self.x = reader.read_fp32()
        self.y = reader.read_fp32()
        self.z = reader.read_fp32()

    def __add__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z

    def __sub__(self, other):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z


@dataclasses.dataclass
class Vec4F:
    x: float = 0
    y: float = 0
    z: float = 0
    w: float = 0

    def read(self, reader: MetroReader):
        self.x = reader.read_fp32()
        self.y = reader.read_fp32()
        self.z = reader.read_fp32()
        self.w = reader.read_fp32()


@dataclasses.dataclass
class Matrix:
    a: float = 0
    b: float = 0
    c: float = 0

    def read(self, reader: MetroReader):
        self.a = reader.read_fp32()
        self.b = reader.read_fp32()
        self.c = reader.read_fp32()


@dataclasses.dataclass
class Matrix3:
    a: Matrix = dataclasses.field(default_factory=Matrix)
    b: Matrix = dataclasses.field(default_factory=Matrix)
    c: Matrix = dataclasses.field(default_factory=Matrix)

    def read(self, reader: MetroReader):
        self.a.read(reader)
        self.b.read(reader)
        self.c.read(reader)


@dataclasses.dataclass
class Matrix4:
    a: Matrix = dataclasses.field(default_factory=Matrix)
    b: Matrix = dataclasses.field(default_factory=Matrix)
    c: Matrix = dataclasses.field(default_factory=Matrix)
    d: Matrix = dataclasses.field(default_factory=Matrix)

    def read(self, reader: MetroReader):
        self.a.read(reader)
        self.b.read(reader)
        self.c.read(reader)
        self.d.read(reader)


@dataclasses.dataclass
class BBox:
    minimal: Vec3F = dataclasses.field(default_factory=Vec3F)
    maximum: Vec3F = dataclasses.field(default_factory=Vec3F)

    def read(self, reader: MetroReader):
        self.minimal.read(reader)
        self.maximum.read(reader)


@dataclasses.dataclass
class BSphere:
    center: Vec3F = dataclasses.field(default_factory=Vec3F)
    radius: float = 0

    def read(self, reader: MetroReader):
        self.center.read(reader)
        self.radius = reader.read_fp32()


@dataclasses.dataclass
class OBBox:
    rotation: Matrix3 = dataclasses.field(default_factory=Matrix3)
    offset: Vec3F = dataclasses.field(default_factory=Vec3F)
    hsize: Vec3F = dataclasses.field(default_factory=Vec3F)

    def read(self, reader: MetroReader):
        self.rotation.read(reader)
        self.offset.read(reader)
        self.hsize.read(reader)
