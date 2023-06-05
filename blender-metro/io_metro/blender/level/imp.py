import bpy
import bpy_extras


class LevelImporter(bpy.types.Operator, bpy_extras.io_utils.ImportHelper, bpy_extras.object_utils.AddObjectHelper):
    bl_idname = "import_4a.level"
    bl_label = "Import 4A Level Geometry"
    bl_description = 'Import 4A Engine Compiled Level Geometry'
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    filename_ext = ".geom_pc"

    filter_glob: bpy.props.StringProperty(
        default="*.geom_pc",
        options={'HIDDEN'},
        maxlen=255
    )

    def execute(self, context):
        from io_metro.blender.formats.blender import BlenderFactory
        BlenderFactory.import_level(self.filepath)

        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(LevelImporter.bl_idname, text='4A Level Geometry (.geom_pc)')


def register():
    bpy.utils.register_class(LevelImporter)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(LevelImporter)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
