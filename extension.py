import bpy

#======================================================================================================================
class PLYVPLayerPropertyGroup(bpy.types.PropertyGroup):

    blend_mode_items = [
        ("MIX", "Mix", "", "NONE", 0),
        ("DARKEN", "Darken", "", "NONE", 1),
        ("MULTIPLY", "Multiply", "", "NONE", 2),
        ("BURN", "Color Burn", "", "NONE", 3),
        ("LIGHTEN", "Lighten", "", "NONE", 4),
        ("SCREEN", "Screen", "", "NONE", 5),
        ("DODGE", "Color Dodge", "", "NONE", 6),
        ("ADD", "Add", "", "NONE", 7),
        ("OVERLAY", "Overlay", "", "NONE", 8),
        ("SOFT_LIGHT", "Soft Light", "", "NONE", 9),
        ("LINEAR_LIGHT", "Linear Light", "", "NONE", 10),
        ("DIFFERENCE", "Difference", "", "NONE", 11),
        ("SUBTRACT", "Subtract", "", "NONE", 12),
        ("DIVIDE", "Divide", "", "NONE", 13),
        ("HUE", "Hue", "", "NONE", 14),
        ("SATURATION", "Saturation", "", "NONE", 15),
        ("COLOR", "Color", "", "NONE", 16),
        ("VALUE", "Value", "", "NONE", 17),
    ]

    #------------------------------------------------------------------------------------------------------------------
    def on_blend_factor_changed(self, context):
        bpy.ops.custom.plyvpl_action_update_material()

    #------------------------------------------------------------------------------------------------------------------
    def on_blend_mode_changed(self, context):
        bpy.ops.custom.plyvpl_action_update_material()

    #------------------------------------------------------------------------------------------------------------------
    listing_name: bpy.props.StringProperty(name = 'Listing Name',  default='')
    color_attr_index: bpy.props.IntProperty(name = 'Color Attribute Index')
    blend_factor: bpy.props.FloatProperty(name = 'Blend Factor', default = 0.5, min = 0, max = 1, step = 1, update = on_blend_factor_changed)
    blend_mode: bpy.props.EnumProperty(name = 'Blend Mode', items = blend_mode_items, default = 'MIX', update = on_blend_mode_changed)

#======================================================================================================================
class PLYVPLExtensionPropertyGroup(bpy.types.PropertyGroup):

    def on_active_index_change(self, context):
        attribs = bpy.context.object.data.color_attributes
        idx = -1
        if self.active_index >= 0 and self.active_index < len(self.layers):
            idx = self.layers[self.active_index].color_attr_index
        if idx >= 0 and idx < len(attribs):
            attribs.active_color_index = idx

    #------------------------------------------------------------------------------------------------------------------
    active_index: bpy.props.IntProperty(name = 'Active Layer Index', update = on_active_index_change)
    layers: bpy.props.CollectionProperty(name = 'Layers', type = PLYVPLayerPropertyGroup)


#======================================================================================================================