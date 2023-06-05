import bpy
import bpy_extras


class ModelImporter(bpy.types.Operator, bpy_extras.io_utils.ImportHelper, bpy_extras.object_utils.AddObjectHelper):
    bl_idname = "import_4a.mesh"
    bl_label = "Import 4A Object"
    bl_description = 'Import 4A Engine Compiled Game Model'
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    filename_ext = ".model"

    filter_glob: bpy.props.StringProperty(
        default="*.model",
        options={'HIDDEN'},
        maxlen=255
    )

    def execute(self, context):
        from io_metro.blender.formats.blender import BlenderFactory
        BlenderFactory.import_model(self.filepath)

        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ModelImporter.bl_idname, text='4A Model (.model)')


def register():
    bpy.utils.register_class(ModelImporter)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ModelImporter)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
