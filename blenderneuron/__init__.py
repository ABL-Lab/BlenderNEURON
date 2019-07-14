try:
    import bpy
    inside_blender = True
except:
    inside_blender = False

if inside_blender:
    from bpy.app.handlers import persistent

    import blenderneuron
    from blenderneuron.commnode import CommNode

    from blenderneuron.blender.operators.connection import *
    from blenderneuron.blender.panels.connection import *
    from blenderneuron.blender.properties.connection import *

    from blenderneuron.blender.operators.rootgroup import *
    from blenderneuron.blender.panels.rootgroup import *
    from blenderneuron.blender.properties.rootgroup import *

    from blenderneuron.blender.utils import register_module_classes

    bl_info = {
        "name": "BlenderNEURON",
        "description": "A Blender GUI for NEURON simulator",
        "author": "Justas Birgiolas",
        "version": (2, 0),
        "blender": (2, 79, 0),
        "location": "View3D > Tools > BlenderNEURON side tab",
        "wiki_url": "BlenderNEURON.org",
        "tracker_url": "https://github.com/JustasB/BlenderNEURON/issues",
        "support": "COMMUNITY",
        "category": "Import-Export",
    }

    @persistent
    def auto_start(scene):
        # Remove auto-execute command after starting
        bpy.app.handlers.scene_update_post.remove(auto_start)

        bpy.ops.wm.blenderneuron_node_start()


    def register():
        try:
            bpy.utils.register_module(__name__)
        except:
            pass

        register_module_classes(blenderneuron.blender.operators.connection)
        register_module_classes(blenderneuron.blender.panels.connection)
        register_module_classes(blenderneuron.blender.properties.connection)

        blenderneuron.blender.properties.connection.register()

        register_module_classes(blenderneuron.blender.operators.rootgroup)
        register_module_classes(blenderneuron.blender.panels.rootgroup)
        register_module_classes(blenderneuron.blender.properties.rootgroup)

        blenderneuron.blender.properties.rootgroup.register()

        # This ensures the server starts on Blender load (self-removing)
        bpy.app.handlers.scene_update_post.append(auto_start)

    def unregister():
        bpy.ops.wm.blenderneuron_node_stop()

        try:
            bpy.utils.unregister_module(__name__)
        except:
            pass

        register_module_classes(blenderneuron.blender.operators.connection, unreg=True)
        register_module_classes(blenderneuron.blender.panels.connection, unreg=True)
        register_module_classes(blenderneuron.blender.properties.connection, unreg=True)

        blenderneuron.blender.connection.properties.unregister()

        register_module_classes(blenderneuron.blender.operators.rootgroup, unreg=True)
        register_module_classes(blenderneuron.blender.panels.rootgroup, unreg=True)
        register_module_classes(blenderneuron.blender.properties.rootgroup, unreg=True)

        blenderneuron.blender.properties.rootgroup.unregister()



# Only for testing from Blender Text Editor
if __name__ == "__main__" and inside_blender:
    register()
