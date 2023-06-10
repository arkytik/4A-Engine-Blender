import bpy
import math
import bmesh
import dataclasses

from mathutils import Vector, Matrix, Quaternion

from io_metro.blender.utils import *
from io_metro.blender.formats.model import *
from io_metro.blender.formats.level import *
from io_metro.blender.formats.texture_tool import convert_metro_texture


@dataclasses.dataclass
class BlenderBone:
    name: str = ""
    bone_parent: str = ""

    position: Vector = dataclasses.field(default_factory=Vector)
    rotation: Quaternion = dataclasses.field(default_factory=Quaternion)


@dataclasses.dataclass
class BlenderPoly:
    pos: Vector = dataclasses.field(default_factory=Vector)
    uv: Vector = dataclasses.field(default_factory=Vector)
    normal: Vector = dataclasses.field(default_factory=Vector)

    bone: BlenderBone = dataclasses.field(default_factory=BlenderBone)
    weight: float = 0


@dataclasses.dataclass
class BlenderFace:
    a: int = 0
    b: int = 0
    c: int = 0


@dataclasses.dataclass
class BlenderMaterial:
    texture: str = ""
    shader: str = ""


class BlenderUtils:
    @staticmethod
    def decode_uv(uv: Vec2F) -> Vector:
        return Vector((uv.x, uv.y))

    @staticmethod
    def decode_level_uv(uv0: Vec2S, uv1: Vec2S) -> [Vector, Vector]:
        scale_factor = 1024.0
        light_scale_factor = 32767.0

        x0 = uv0.x / scale_factor
        y0 = uv0.y / scale_factor

        x1 = uv1.x / light_scale_factor
        y1 = uv1.y / light_scale_factor

        return Vector((x0, y0)), Vector((x1, y1))

    @staticmethod
    def decode_skinned_uv(uv: Vec2S) -> Vector:
        scale_factor = 2048.0

        x = uv.x / scale_factor
        y = uv.y / scale_factor

        return Vector((x, y))

    @staticmethod
    def decode_normal(normal: int) -> [Vector, int]:
        x = (((normal & 0x00FF0000) >> 16) / 255) * 2 - 1
        y = (((normal & 0x0000FF00) >> 8) / 255) * 2 - 1
        z = (((normal & 0x000000FF) >> 0) / 255) * 2 - 1
        vao = ((normal & 0xFF000000) >> 24) / 255

        return Vector((x, z, y)), vao

    @staticmethod
    def decode_position(pos: Vec3F) -> Vector:
        x = pos.x
        y = pos.z
        z = pos.y

        return Vector((-x, y, z))

    @staticmethod
    def decode_skinned_position(pos: Vec4S) -> Vector:
        scale_factor = 2720.0

        x = pos.x / scale_factor
        y = pos.z / scale_factor
        z = pos.y / scale_factor

        return Vector((-x, y, z))


@dataclasses.dataclass
class BlenderMesh:
    name: str = ""
    vertex: List[BlenderPoly] = dataclasses.field(default_factory=list)
    faces: List[BlenderFace] = dataclasses.field(default_factory=list)

    material: BlenderMaterial = dataclasses.field(default_factory=BlenderMaterial)

    def create_mesh(self):
        def create_blender_object(mesh):
            # create a new mesh object and link it to the scene
            obj = create_object(f"{self.name}_object", mesh)

            # add material
            dds_path = convert_metro_texture(self.material.texture)

            new_material = bpy.data.materials.new(name=f"{self.name}_material")
            new_material.use_nodes = True

            if dds_path:
                shader = new_material.node_tree.nodes["Principled BSDF"]

                new_texture = new_material.node_tree.nodes.new('ShaderNodeTexImage')
                new_texture.image = bpy.data.images.load(dds_path)

                new_material.node_tree.links.new(shader.inputs['Base Color'], new_texture.outputs['Color'])

            if obj.data.materials:
                obj.data.materials[0] = new_material
            else:
                obj.data.materials.append(new_material)

            return obj

        def create_blender_armature():
            armature_data = bpy.data.armatures.new('4A_Armature')
            armature_object = bpy.data.objects.new('4A_Armature', armature_data)
            bpy.context.collection.objects.link(armature_object)

            bpy.context.view_layer.objects.active = armature_object

            return armature_object, armature_data

        blender_armature, blender_armature_data = None, None

        #  create bmesh
        bm = bmesh.new()

        #  vertex
        for tri in self.vertex:
            v = bm.verts.new((tri.pos.x, tri.pos.y, tri.pos.z))
            v.normal = Vector((tri.normal.x, tri.normal.y, tri.normal.z))

            if tri.bone and tri.bone.name != "":
                blender_armature, blender_armature_data = create_blender_armature()

        bm.verts.ensure_lookup_table()
        bm.verts.index_update()

        #  faces
        for face in self.faces:
            try:
                face = bm.faces.new((bm.verts[face.a], bm.verts[face.b], bm.verts[face.c]))
                face.smooth = True
            except ValueError:  # Same Face
                pass

        bm.faces.ensure_lookup_table()
        bm.normal_update()

        #  create uv
        uv_layer = bm.loops.layers.uv.new(f"{self.name}_uv")

        for face in bm.faces:
            for loop in face.loops:
                uv_coord = self.vertex[loop.vert.index].uv
                loop[uv_layer].uv = (
                    uv_coord.x,
                    1 - uv_coord.y
                )

        #  create mesh
        bpy_mesh = bpy.data.meshes.new(f"{self.name}_mesh")

        bpy_mesh.use_auto_smooth = True
        bpy_mesh.auto_smooth_angle = math.pi

        # fill the mesh data with the bmesh data
        bm.to_mesh(bpy_mesh)
        bm.free()

        # make blender object
        blender_object = create_blender_object(bpy_mesh)

        if blender_armature:
            blender_object.parent = blender_armature
            blender_object.parent_type = 'ARMATURE'


class BlenderFactory:
    @staticmethod
    def import_model(model_path: str, lod_type: int = 0):
        reader = MetroReader(bin_path=model_path)

        model = Model()
        model.read(reader)

        blender_meshes = BlenderFactory.convert_model_to_blender_meshes(model, lod_type)

        for blender_mesh in blender_meshes:
            blender_mesh.create_mesh()

    @staticmethod
    def import_level(geom_path: str):
        level = Level()
        level.read(geom_path)

        blender_meshes = BlenderFactory.convert_level_to_blender_meshes(level)

        for blender_mesh in blender_meshes:
            blender_mesh.create_mesh()

    @staticmethod
    def convert_level_to_blender_meshes(level: Level) -> List[BlenderMesh]:
        def convert_part(part: LevelPart):
            mesh = BlenderMesh()
            mesh.name = "4A_Level"
            mesh.material = BlenderMaterial(part.material.texture, part.material.shader)

            for vertex in part.vertex:
                poly = BlenderPoly()
                poly.pos = BlenderUtils.decode_position(vertex.position)
                poly.uv, light_map_uv = BlenderUtils.decode_level_uv(vertex.uv0, vertex.uv1)
                poly.normal, vao = BlenderUtils.decode_normal(vertex.normal)

                mesh.vertex.append(poly)

            for face in part.faces:
                face = BlenderFace(face.a, face.b, face.c)

                mesh.faces.append(face)

            return mesh

        r = []

        for lvl in level.level_parts:
            bm = convert_part(lvl)
            r.append(bm)

        return r

    @staticmethod
    def convert_model_to_blender_meshes(model: Model, lod_type: int = 0) -> List[BlenderMesh]:
        def convert_static(std: ModelStd):
            mesh = BlenderMesh()
            mesh.name = std.material.name
            mesh.material = BlenderMaterial(std.material.texture, std.material.shader)

            for vertex in std.vertex.vertex:
                poly = BlenderPoly()
                poly.pos = BlenderUtils.decode_position(vertex.position)
                poly.uv = BlenderUtils.decode_uv(vertex.uv)
                poly.normal, vao = BlenderUtils.decode_normal(vertex.normal)

                mesh.vertex.append(poly)

            for face in std.faces.faces:
                face = BlenderFace(face.a, face.b, face.c)

                mesh.faces.append(face)

            return mesh

        def convert_mesh(skl: Mesh, skeleton: ModelSkeleton = None):
            mesh = BlenderMesh()
            mesh.name = skl.material.name
            mesh.material = BlenderMaterial(skl.material.texture, skl.material.shader)

            for vertex in skl.skinned_vertex.skinned_vertex:
                poly = BlenderPoly()
                poly.pos = BlenderUtils.decode_skinned_position(vertex.position)
                poly.uv = BlenderUtils.decode_skinned_uv(vertex.uv)
                poly.normal, vao = BlenderUtils.decode_normal(vertex.normal)

                mesh.vertex.append(poly)

            for face in skl.faces.faces:
                face = BlenderFace(face.a, face.b, face.c)

                mesh.faces.append(face)

            return mesh

        r = []

        if not model:
            return r

        if model.visuals:
            for visual in model.visuals:
                bm = convert_static(visual)
                r.append(bm)

        if model.meshes:
            for sk_mesh in model.meshes:
                bm = convert_mesh(sk_mesh)
                r.append(bm)

        if model.model_skeleton:
            if model.model_skeleton.lod0 and lod_type == 0:
                for sk_mesh in model.model_skeleton.lod0:
                    bm = convert_mesh(sk_mesh, model.model_skeleton)
                    r.append(bm)

            if model.model_skeleton.lod1 and lod_type == 1:
                for sk_mesh in model.model_skeleton.lod1:
                    bm = convert_mesh(sk_mesh, model.model_skeleton)
                    r.append(bm)

            if model.model_skeleton.lod2 and lod_type == 2:
                for sk_mesh in model.model_skeleton.lod2:
                    bm = convert_mesh(sk_mesh, model.model_skeleton)
                    r.append(bm)

        return r
