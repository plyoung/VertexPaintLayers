import bpy

from .operator import *
from .extension import *

#======================================================================================================================
class PLYVPL_UL_layers(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        obj = context.object
        color_attribs = obj.data.color_attributes
        attrib = None
        if item.color_attr_index >= 0 and item.color_attr_index < len(color_attribs):
            attrib = color_attribs[item.color_attr_index]

        row = layout.split(factor = 0.6)
        row.prop(item, 'listing_name', text='', icon='GROUP_VCOL', emboss=False)

        sub = row.row()
        sub.alignment = 'RIGHT'
        sub.enabled = False
        if attrib:
            sub.label(text=attrib.name, translate = False)
        else:
            sub.label(text='', translate = False, icon='ERROR')
            

#======================================================================================================================
class PLYVPL_MT_context_menu(bpy.types.Menu):
    bl_label = "Layers Specials"

    def draw(self, context):
        layout = self.layout
        layout.operator(PLYVPL_OT_action_sync_attribs.bl_idname, icon='GROUP_VCOL', text="Sync Color Attributes")
        layout.operator(PLYVPL_OT_action_update_material.bl_idname, icon='MATSPHERE', text="Update Material (Unlit)").action = "UNLIT"
        layout.operator(PLYVPL_OT_action_update_material.bl_idname, icon='SHADING_RENDERED', text="Update Material (Shaded)").action = "SHADED"

#======================================================================================================================
class PLYVPL_PT_Panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Vertex Paint Layers"
    bl_category = "VPL"

    def draw(self, context):

        obj = context.object
        if obj is None: return

        layout = self.layout
        addon_extension = obj.plyvpl_addon_extension

        if addon_extension.active_index >= 0 and addon_extension.active_index < len(addon_extension.layers):
            active_layer = addon_extension.layers[addon_extension.active_index]
            row = layout.row()
            sub = row.split(factor=0.5)
            sub.prop(active_layer, "blend_factor", text = "Blend")
            sub.prop(active_layer, "blend_mode", text = "")

        row = layout.row()        
        row.template_list(PLYVPL_UL_layers.__name__, "", addon_extension, "layers", addon_extension, "active_index")
        
        col = row.column(align=True)
        col.operator(PLYVPL_OT_list_actions.bl_idname, icon='ADD', text="").action = 'ADD'
        col.operator(PLYVPL_OT_list_actions.bl_idname, icon='REMOVE', text="").action = 'REMOVE'
        col.separator()
        col.operator(PLYVPL_OT_list_actions.bl_idname, icon='TRIA_UP', text="").action = 'UP'
        col.operator(PLYVPL_OT_list_actions.bl_idname, icon='TRIA_DOWN', text="").action = 'DOWN'
        col.separator()
        col.menu(PLYVPL_MT_context_menu.__name__, icon='DOWNARROW_HLT', text="")
        
        row = layout.row()
        col = row.column()
        col.operator(PLYVPL_OT_action_update_material.bl_idname, icon='MATSPHERE', text="Unlit").action = "UNLIT"
        col = row.column()
        col.operator(PLYVPL_OT_action_update_material.bl_idname, icon='SHADING_RENDERED', text="Shaded").action = "SHADED"
        row = layout.row()
        row.operator(PLYVPL_OT_action_sync_attribs.bl_idname, icon='GROUP_VCOL', text="Sync Color Attributes")

#======================================================================================================================
