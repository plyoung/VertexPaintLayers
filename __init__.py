bl_info = {
    "name" : "Vertex Paint Layers",
    "author" : "PL Young",
    "descrtion" : "Vertex painting layers",
    "blender" : (3, 3, 0),
    "version" : (1, 0, 2),
    "location" : "View 3D > Tool Shelf > Vertex Paint Layers",
    "warning" : "",
    "category" : "3D View"
}

# if "bpy" in locals():
#     import importlib
#     importlib.reload(extension)
#     importlib.reload(operator)
#     importlib.reload(panel)

import bpy

from .panel import *
from .operator import *
from .extension import *

classes = ( 
    PLYVPL_MT_context_menu, 
    PLYVPL_PT_Panel, 
    PLYVPL_UL_layers, 
    PLYVPL_OT_list_actions, 
    PLYVPL_OT_action_sync_attribs,
    PLYVPL_OT_action_update_material,
    PLYVPLayerPropertyGroup, 
    PLYVPLExtensionPropertyGroup, 
)

#------------------------------------------------------------------------------------------------------------------
def register() -> None:

    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except RuntimeError:
            pass 

    bpy.types.Object.plyvpl_addon_extension = bpy.props.PointerProperty(type=PLYVPLExtensionPropertyGroup)

#------------------------------------------------------------------------------------------------------------------
def unregister() -> None:

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
        
    del bpy.types.Object.plyvpl_addon_extension

#------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    register()
