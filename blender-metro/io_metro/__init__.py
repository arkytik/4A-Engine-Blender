bl_info = {
    'name': '4A Engine Tools',
    'author': 'Arkadii',
    'version': (0, 1, 4),
    'blender': (2, 80, 0),
    'category': 'Import-Export',
    'location': 'File > Import/Export',
    'support': 'COMMUNITY',
    'description': 'Import/Export 4A Games Files (Metro Redux / Metro Exodus).'
}


def register():
    from .blender import register

    register()


def unregister():
    from .blender import unregister

    unregister()
