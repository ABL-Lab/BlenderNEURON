try:
    import bpy
    from bpy.app.handlers import persistent

    import blenderneuron
    from blenderneuron.commnode import CommNode

    from blenderneuron.addon.operators import *
    from blenderneuron.addon.panels import *
    from blenderneuron.addon.properties import *

    from blenderneuron.addon.utils import register_module_classes

    inside_blender = True
except:
    inside_blender = False

if inside_blender:

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

        register_module_classes(blenderneuron.addon.operators)
        register_module_classes(blenderneuron.addon.panels)
        register_module_classes(blenderneuron.addon.properties)

        # Load config properties
        bpy.types.Scene.BlenderNEURON_properties = \
            bpy.props.PointerProperty(type=blenderneuron_properties)

        # This ensures the server starts on Blender load (self-removing)
        bpy.app.handlers.scene_update_post.append(auto_start)

    def unregister():
        bpy.ops.wm.blenderneuron_node_stop()

        try:
            bpy.utils.unregister_module(__name__)
        except:
            pass

        register_module_classes(blenderneuron.addon.operators, unreg=True)
        register_module_classes(blenderneuron.addon.panels, unreg=True)
        register_module_classes(blenderneuron.addon.properties, unreg=True)

        del bpy.types.Scene.BlenderNEURON_properties

# Only for testing from Blender Text Editor
if __name__ == "__main__" and inside_blender:
    register()

