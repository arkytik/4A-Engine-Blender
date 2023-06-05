import io_metro.blender.level.imp as level
import io_metro.blender.model.imp as model


def register():
    level.register()
    model.register()


def unregister():
    level.unregister()
    model.unregister()
