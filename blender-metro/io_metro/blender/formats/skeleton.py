import dataclasses

from io_metro.blender.formats.config_reader import *


@dataclasses.dataclass
class ParentMapped:
    parent_bone: str = ""
    self_bone: str = ""

    q: Vec4F = dataclasses.field(default_factory=Vec4F)  # rotation/quaternion
    t: Vec3F = dataclasses.field(default_factory=Vec3F)  # transform/position
    s: Vec3F = dataclasses.field(default_factory=Vec3F)  # scale

    def read(self, reader: ConfigReader):
        self.parent_bone = reader.read_str()
        self.self_bone = reader.read_str()

        self.q = reader.read_vec4f()
        self.t = reader.read_vec3f()
        self.s = reader.read_vec3f()


@dataclasses.dataclass
class BoneBase:
    name: str = ""
    parent: str = ""
    q: Vec4F = dataclasses.field(default_factory=Vec4F)
    t: Vec3F = dataclasses.field(default_factory=Vec3F)

    def read(self, reader: ConfigReader):
        self.name = reader.read_str()
        self.parent = reader.read_str()
        self.q = reader.read_vec4f()
        self.t = reader.read_vec3f()


@dataclasses.dataclass
class Bone(BoneBase):
    bp: int = 0
    bpf: int = 0

    def read(self, reader: ConfigReader):
        super().read(reader)

        if reader.get_type() == ConfigType.Debug:
            self.bp = reader.read_u16("bp")
        else:
            self.bp = reader.read_u8()
            self.bpf = reader.read_u8()


@dataclasses.dataclass
class Locator(BoneBase):
    fl: Bool8 = dataclasses.field(default_factory=Bool8)

    def read(self, reader: ConfigReader):
        super().read(reader)

        self.fl = reader.read_bool8()


@dataclasses.dataclass
class BoneAux(BoneBase):
    fl: Bool8 = dataclasses.field(default_factory=Bool8)

    def read(self, reader: ConfigReader, version: int = 0):
        super().read(reader)

        self.fl = Bool8(0)

        if version >= 16:
            self.fl = reader.read_bool8()


#  Procedural Bones
class MetroProceduralComponent(enum.Enum):
    Invalid = 0
    AxisX = 1
    AxisY = 2
    AxisZ = 3
    OffsetX = 4
    OffsetY = 5
    OffsetZ = 6


class MetroProceduralType(enum.Enum):
    Driven = 0
    Posrot_constrained = 1
    Dynamic = 2
    Lookat_constrained = 3
    Size = 4


class MetroProceduralRotationOrder(enum.Enum):
    Default = 0
    ZYX = 1
    _2 = 2
    _3 = 3
    _4 = 4
    _5 = 5


@dataclasses.dataclass
class MetroProceduralBone:
    type: int = 0
    index_in_array: int = 0

    def read(self, reader: ConfigReader):
        self.type = reader.read_u16()
        self.index_in_array = reader.read_u16()


@dataclasses.dataclass
class MetroDrivenBone:
    bone: str = ""
    driver: str = ""
    twister: str = ""
    driver_parent: str = ""
    component: int = 0

    value_min: float = 0
    value_max: float = 0

    #  proceduralVer >= 1
    refresh_kids: int = 0
    #  proceduralVer >= 5
    use_anim_poses: bool = False

    def read(self, reader: ConfigReader, procedural_ver: int = 0):
        self.bone = reader.read_choose()
        self.driver = reader.read_choose()
        self.driver_parent = reader.read_choose()

        self.component = reader.read_u8()
        self.twister = reader.read_str()

        self.value_min = reader.read_fp32()
        self.value_max = reader.read_fp32()

        if procedural_ver >= 1:
            self.refresh_kids = reader.read_u8()

        if procedural_ver >= 5:
            self.use_anim_poses = reader.read_bool()


@dataclasses.dataclass
class MetroDynamicBone:
    bone: str = ""
    inertia: float = 0
    damping: float = 0

    #  if proceduralVer >= 9
    pos_min_limits: Vec3F = dataclasses.field(default_factory=Vec3F)
    pos_max_limits: Vec3F = dataclasses.field(default_factory=Vec3F)
    rot_min_limits: Vec3F = dataclasses.field(default_factory=Vec3F)
    rot_max_limits: Vec3F = dataclasses.field(default_factory=Vec3F)

    #  if proceduralVer < 9
    constraints: Vec3F = dataclasses.field(default_factory=Vec3F)
    #  if proceduralVer >= 6
    rot_limits: Vec3F = dataclasses.field(default_factory=Vec3F)

    #  if proceduralVer >= 4
    use_world_pos: bool = False

    def read(self, reader: ConfigReader, procedural_ver: int = 0):
        self.bone = reader.read_str()
        self.inertia = reader.read_fp32()
        self.damping = reader.read_fp32()

        if procedural_ver >= 9:
            self.pos_min_limits = reader.read_vec3f()
            self.pos_max_limits = reader.read_vec3f()
            self.rot_min_limits = reader.read_vec3f()
            self.rot_max_limits = reader.read_vec3f()

        if procedural_ver < 9:
            self.constraints = reader.read_vec3f()

        if procedural_ver >= 6:
            self.rot_limits = reader.read_vec3f()

        if procedural_ver >= 4:
            self.use_world_pos = reader.read_bool()


@dataclasses.dataclass
class ParentBone:
    bone: str = ""
    weight: float = 0

    def read(self, reader: ConfigReader):
        self.bone = reader.read_str()
        self.weight = reader.read_fp32()


@dataclasses.dataclass
class ParentBones:
    bone_names: str = ""
    bone_strs: List[ParentBone] = dataclasses.field(default_factory=list)
    axis: int = 0  # MetroProceduralComponent

    def read(self, reader: ConfigReader):
        self.bone_strs = []
        self.bone_names = reader.read_str()

        bone_strs_array, bone_strs_count = reader.read_array("bone_strs")

        for i in range(bone_strs_count):
            rec = bone_strs_array.read_section(f"rec_{i:04d}")

            pb = ParentBone()
            pb.read(rec)

            self.bone_strs.append(pb)

        self.axis = reader.read_u8()


@dataclasses.dataclass
class MetroConstrainedBone:
    bone: str = ""  # choose
    position: ParentBones = dataclasses.field(default_factory=ParentBones)
    orientation: ParentBones = dataclasses.field(default_factory=ParentBones)
    bone_id: int = 0
    root_id: int = 0
    rotation_order: int = 0  # MetroProceduralRotationOrder
    look_at_axis: int = 0  # MetroProceduralComponent
    pos_axis: int = 0  # MetroProceduralComponent
    rot_axis: int = 0  # MetroProceduralComponent
    refresh_kids: int = 0
    use_anim_poses: bool = False

    #  v7
    pos_limits: Vec3F = dataclasses.field(default_factory=Vec3F)
    rot_limits: Vec3F = dataclasses.field(default_factory=Vec3F)

    #  > v7
    pos_min_limits: Vec3F = dataclasses.field(default_factory=Vec3F)
    pos_max_limits: Vec3F = dataclasses.field(default_factory=Vec3F)
    rot_min_limits: Vec3F = dataclasses.field(default_factory=Vec3F)
    rot_max_limits: Vec3F = dataclasses.field(default_factory=Vec3F)
    up_type: int = 0
    up: ParentBones = dataclasses.field(default_factory=ParentBones)

    def read(self, reader: ConfigReader, version: int = 0):
        self.bone = reader.read_str()
        self.position.read(reader)
        self.orientation.read(reader)
        self.bone_id = reader.read_u16()
        self.root_id = reader.read_u16()
        self.rotation_order = reader.read_u8()
        self.look_at_axis = reader.read_u8()
        self.pos_axis = reader.read_u8()
        self.rot_axis = reader.read_u8()
        self.refresh_kids = reader.read_u8()
        self.use_anim_poses = reader.read_bool()

        if version == 7:
            self.pos_limits = reader.read_vec3f()
            self.rot_limits = reader.read_vec3f()

        if version > 7:
            self.pos_min_limits = reader.read_vec3f()
            self.pos_max_limits = reader.read_vec3f()
            self.rot_min_limits = reader.read_vec3f()
            self.rot_max_limits = reader.read_vec3f()
            self.up_type = reader.read_u8()
            self.up.read(reader)


@dataclasses.dataclass
class MetroParamBone:
    bone: str = ""  # choose
    parent: str = ""  # choose
    param: str = ""  # choose
    component: int = 0  # MetroProceduralComponent

    def read(self, reader: ConfigReader):
        self.bone = reader.read_str()
        self.parent = reader.read_str()
        self.param = reader.read_str()
        self.component = reader.read_u8()


@dataclasses.dataclass
class MetroPartition:
    name: str = ""
    in_fl: List[int] = dataclasses.field(default_factory=list)

    def read(self, reader: ConfigReader):
        self.name = reader.read_str()
        self.in_fl = reader.read_array_u8()


@dataclasses.dataclass
class MetroIkLock:
    chain_idx: int = 0
    pos_weight: float = 0
    rot_weight: float = 0

    def read(self, reader: ConfigReader):
        self.chain_idx = reader.read_u16()
        self.pos_weight = reader.read_fp32()
        self.rot_weight = reader.read_fp32()


@dataclasses.dataclass
class MetroIkChain:
    FlagForwardKnee = 0x1
    FlagProcedural = 0x2
    FlagFixedKneeDir = 0x4
    FlagGroundAlignDisabled = 0x8
    Flag3D = 0x10
    FlagKneeDirFromLower = 0x20
    FlagGroundClamp = 0x40
    FlagGroundLocator3D = 0x80

    name: str = ""
    b0: int = 0
    b1: int = 0
    b2: int = 0
    knee_dir: Vec3F = dataclasses.field(default_factory=Vec3F)
    knee_lim: float = 0

    #  arktika & exodus
    upper_limb_bone: int = 0
    lower_limb_bone: int = 0
    max_length: float = 0
    flags: int = 0

    #  if flags & 0x100
    ground_locator: int = 0

    def read(self, reader: ConfigReader, version: int = 0):
        self.name = reader.read_str()
        self.b0 = reader.read_u16()
        self.b1 = reader.read_u16()
        self.b2 = reader.read_u16()
        self.knee_dir = reader.read_vec3f()
        self.knee_lim = reader.read_fp32()

        if version > 8:
            self.upper_limb_bone = reader.read_u16()
            self.lower_limb_bone = reader.read_u16()
            self.max_length = reader.read_fp32()
            self.flags = reader.read_u32()

            if self.flags and self.flags & 0x100:
                self.ground_locator = reader.read_u16()


@dataclasses.dataclass
class MetroFixedBone:
    id: int = 0

    def read(self, reader: ConfigReader):
        self.id = reader.read_u16()


@dataclasses.dataclass
class MetroSkelParam:
    name: str = ""
    begin: float = 0
    end: float = 0
    loop: float = 0

    def read(self, reader: ConfigReader):
        self.name = reader.read_str()
        self.begin = reader.read_fp32()
        self.end = reader.read_fp32()
        self.loop = reader.read_fp32()


@dataclasses.dataclass
class MetroWeightedMotion:
    motion: str = ""
    weight: float = 0

    def read(self, reader: ConfigReader):
        self.motion = reader.read_str()
        self.weight = reader.read_fp32()


@dataclasses.dataclass
class MotionsCollection:
    name: str = ""
    path: str = ""
    motions: List[MetroWeightedMotion] = dataclasses.field(default_factory=list)

    def read(self, reader: ConfigReader):
        self.motions = []
        self.name = reader.read_str()
        self.path = reader.read_str()

        mots_array, mots_count = reader.read_array("mots")

        for i in range(mots_count):
            rec = mots_array.read_section(f"rec_{i:04d}")

            mw = MetroWeightedMotion()
            mw.read(rec)

            self.motions.append(mw)


@dataclasses.dataclass
class Skeleton:
    procedural_ver: int = 0
    checksum: int = 0
    version: int = 0

    parent_skeleton: str = ""
    source_info: str = ""
    motions: str = ""
    face_fx: str = ""
    pfnn: str = ""

    has_as: bool = False

    parent_bone_maps: List[ParentMapped] = dataclasses.field(default_factory=list)

    bones_aux: List[BoneAux] = dataclasses.field(default_factory=list)
    locators: List[Locator] = dataclasses.field(default_factory=list)
    bones: List[Bone] = dataclasses.field(default_factory=list)

    constrained_bones: List[MetroConstrainedBone] = dataclasses.field(default_factory=list)
    procedural_bones: List[MetroProceduralBone] = dataclasses.field(default_factory=list)
    dynamic_bones: List[MetroDynamicBone] = dataclasses.field(default_factory=list)
    driven_bones: List[MetroDrivenBone] = dataclasses.field(default_factory=list)
    param_bones: List[MetroParamBone] = dataclasses.field(default_factory=list)

    motions_col: List[MotionsCollection] = dataclasses.field(default_factory=list)
    fixed_bones: List[MetroFixedBone] = dataclasses.field(default_factory=list)
    partitions: List[MetroPartition] = dataclasses.field(default_factory=list)
    ik_chains: List[MetroIkChain] = dataclasses.field(default_factory=list)
    params: List[MetroSkelParam] = dataclasses.field(default_factory=list)
    ik_locks: List[MetroIkLock] = dataclasses.field(default_factory=list)

    inv_bind_pose: List[Matrix4] = dataclasses.field(default_factory=list)
    motions_str: str = ""

    def read(self, reader: ConfigReader):
        def read_ddk():
            if self.version >= 7:
                self.driven_bones = []
                driven_bones_array, driven_bones_count = skeleton_section.read_array("driven_bones")

                for j in range(driven_bones_count):
                    sec = driven_bones_array.read_section(f"rec_{j:04d}")

                    driven_bone = MetroDrivenBone()
                    driven_bone.read(sec)

                    self.driven_bones.append(driven_bone)

            if self.version >= 8:
                self.dynamic_bones = []
                dynamic_bones_array, dynamic_bones_count = skeleton_section.read_array("dynamic_bones")

                for j in range(dynamic_bones_count):
                    sec = dynamic_bones_array.read_section(f"rec_{j:04d}")

                    dynamic_bone = MetroDynamicBone()
                    dynamic_bone.read(sec)

                    self.dynamic_bones.append(dynamic_bone)

            if self.version >= 9:
                self.constrained_bones = []
                constrained_bones_array, constrained_bones_count = skeleton_section.read_array("constrained_bones")

                for j in range(constrained_bones_count):
                    sec = constrained_bones_array.read_section(f"rec_{j:04d}")

                    constrained_bone = MetroConstrainedBone()
                    constrained_bone.read(sec)

                    self.constrained_bones.append(constrained_bone)

        skeleton_section = reader.read_section("skeleton")

        if not skeleton_section or not skeleton_section.more():
            raise Exception("Skeleton Section In Nullable!")

        self.version = skeleton_section.read_u32()
        self.checksum = skeleton_section.read_u32()

        if self.version <= 14:
            self.face_fx = skeleton_section.read_str()

        if self.version >= 17:
            self.pfnn = skeleton_section.read_str()

        if self.version >= 21:
            self.has_as = skeleton_section.read_bool()

        self.motions = skeleton_section.read_str()

        if self.version >= 13:
            self.source_info = skeleton_section.read_str()

        if self.version >= 14:
            self.parent_skeleton = skeleton_section.read_str()
            self.parent_bone_maps = []

            parent_bones_maps_array, parent_bones_maps_count = skeleton_section.read_array("parent_bone_maps")

            for _ in range(parent_bones_maps_count):
                p_map = ParentMapped()
                p_map.read(parent_bones_maps_array)

                self.parent_bone_maps.append(p_map)

        self.bones = []
        self.locators = []

        bones_array, bones_count = skeleton_section.read_array("bones")
        for i in range(bones_count):
            rec = bones_array.read_section(f"rec_{i:04d}")

            bone = Bone()
            bone.read(rec)

            self.bones.append(bone)

        locators_array, locators_count = skeleton_section.read_array("locators")
        for i in range(locators_count):
            rec = locators_array.read_section(f"rec_{i:04d}")

            locator = Locator()
            locator.read(rec)

            self.locators.append(locator)

        if self.version >= 6:
            self.bones_aux = []

            bones_aux_array, bones_aux_count = skeleton_section.read_array("aux_bones")
            for i in range(bones_aux_count):
                rec = bones_aux_array.read_section(f"rec_{i:04d}")

                bone_aux = BoneAux()
                bone_aux.read(rec, self.version)

                self.bones_aux.append(bone_aux)

        if self.version >= 11:
            self.procedural_ver = skeleton_section.read_u32()

            if self.procedural_ver > 1:
                self.procedural_bones = []

                procedural_bones_array, procedural_bones_count = skeleton_section.read_array("procedural_bones")
                for i in range(procedural_bones_count):
                    rec = procedural_bones_array.read_section(f"rec_{i:04d}")

                    procedural_bone = MetroProceduralBone()
                    procedural_bone.read(rec)

                    self.procedural_bones.append(procedural_bone)

            read_ddk()

            if self.version >= 20:
                self.param_bones = []

                param_bones_array, param_bones_count = skeleton_section.read_array("param_bones")
                for i in range(param_bones_count):
                    rec = param_bones_array.read_section(f"rec_{i:04d}")

                    param_bone = MetroParamBone()
                    param_bone.read(rec)

                    self.param_bones.append(param_bone)
        else:
            read_ddk()

        self.partitions = []

        partitions_array, partitions_count = skeleton_section.read_array("partitions")
        for i in range(partitions_count):
            rec = partitions_array.read_section(f"rec_{i:04d}")

            partition = MetroPartition()
            partition.read(rec)

            self.partitions.append(partition)

        self.ik_chains = []

        ik_chains_array, ik_chains_count = skeleton_section.read_array("ik_chains")
        for i in range(ik_chains_count):
            rec = ik_chains_array.read_section(f"rec_{i:04d}")

            ik_chain = MetroIkChain()
            ik_chain.read(rec)

            self.ik_chains.append(ik_chain)

        self.fixed_bones = []

        fixed_bones_array, fixed_bones_count = skeleton_section.read_array("fixed_bones")
        for i in range(fixed_bones_count):
            rec = fixed_bones_array.read_section(f"rec_{i:04d}")

            fb = MetroFixedBone()
            fb.read(rec)

            self.fixed_bones.append(fb)

        self.params = []

        params_array, params_count = skeleton_section.read_array("params")
        for i in range(params_count):
            rec = params_array.read_section(f"rec_{i:04d}")

            param = MetroSkelParam()
            param.read(rec)

            self.params.append(param)

        self.motions_col = []

        motions_col_array, motions_col_count = skeleton_section.read_array("mcolls")
        for i in range(motions_col_count):
            rec = motions_col_array.read_section(f"rec_{i:04d}")

            motion_col = MotionsCollection()
            motion_col.read(rec)

            self.motions_col.append(motion_col)

        if self.version == 5:
            dbg_show_obbs = skeleton_section.read_array_u32()
            dbg_show_bones = skeleton_section.read_array_u32()
            dbg_show_names = skeleton_section.read_array_u32()
            dbg_show_axis = skeleton_section.read_array_u32()
            dbg_show_links = skeleton_section.read_array_u32()

            print(dbg_show_obbs, dbg_show_bones, dbg_show_names, dbg_show_axis, dbg_show_links)

        if reader.more() or skeleton_section.more():
            raise Exception(f"Not All Skeleton Data Read: R[{reader.get_reader().offset} <> {reader.get_reader().size}] OR S[{skeleton_section.get_reader().offset} <> {skeleton_section.get_reader().size}]")
