import bpy


def is_blender_2_77():
    return bpy.app.version <= (2, 77, 0)


def is_blender_2_80():
    return bpy.app.version >= (2, 80, 0)


def is_blender_2_90():
    return bpy.app.version >= (2, 90, 0)


def is_blender_2_93():
    return bpy.app.version >= (2, 93, 0)


def is_blender_3():
    return bpy.app.version >= (3, 0, 0)


def is_blender_34():
    return bpy.app.version >= (3, 4, 0)


def link_object(obj):
    if is_blender_2_80():
        bpy.context.scene.collection.objects.link(obj)
    else:
        if not bpy.context.scene.objects.get(obj.name):
            bpy.context.scene.objects.link(obj)


def create_object(name, data):
    bpy_object = bpy.data.objects.new(name, data)
    link_object(bpy_object)

    return bpy_object
