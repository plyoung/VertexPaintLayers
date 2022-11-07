import bpy

from mathutils import Vector

#======================================================================================================================
class PLYVPL_OT_action_sync_attribs(bpy.types.Operator):
    
    bl_idname = "custom.plyvpl_action_sync_attribs"
    bl_label = "Sync Color Attributes"
    bl_description = "Sync the layers and colour attributes, adding missing layers and renaming attributes based on layer names."
    bl_options = {'REGISTER'}

    def execute(self, context):

        self.report({'INFO'}, "Sync Vertext Paint Layers with Color Attributes")

        obj = context.object
        addon_extension = obj.plyvpl_addon_extension
        color_attribs = obj.data.color_attributes
        attrib_count = len(color_attribs)

        # check that there is a layer entry for every attribute
        for idx in range(0, attrib_count):
            found = False
            for layer in addon_extension.layers:
                if layer.color_attr_index == idx:
                    found = True
                    if len(layer.listing_name) == 0:
                        layer.listing_name = color_attribs[idx].name
                    break
            if not found:
                layer = addon_extension.layers.add()
                layer.listing_name = color_attribs[idx].name
                layer.color_attr_index = idx

        # remove the layer pointing to removed attributes
        layers_len = len(addon_extension.layers)
        for idx in range(layers_len - 1, -1, -1):
            if addon_extension.layers[idx].color_attr_index >= attrib_count:
                addon_extension.layers.remove(idx)

        # rename attributes based on layer names, but first rename all attribs to 
        # something totally different to avoid name clash during real renaming
        for idx in range(0, attrib_count):
            obj.data.color_attributes[idx].name = '_temp_' + str(idx) + '_' + obj.data.color_attributes[idx].name

        # now the real rename
        for layer in addon_extension.layers:
            if len(layer.listing_name) > 0:
                obj.data.color_attributes[layer.color_attr_index].name = layer.listing_name
            # this is in case there was dupe name since attrib would then get a .001, .002 etc
            layer.listing_name = obj.data.color_attributes[layer.color_attr_index].name

        # make the 1st layer selected if there are layers
        if len(addon_extension.layers) > 0:
            addon_extension.active_index = 0
        else:
            addon_extension.active_index = -1

        bpy.ops.custom.plyvpl_action_update_material()

        return {"FINISHED"}

#======================================================================================================================
class PLYVPL_OT_action_update_material(bpy.types.Operator):
    
    bl_idname = "custom.plyvpl_action_update_material"
    bl_label = "Update Material"
    bl_description = "Update the material with selected shading"
    bl_options = {'REGISTER'}

    material_name = "Material (Vertex Paint Layers)"

    action: bpy.props.EnumProperty(
        items=(
            ('INVALID', "Invalid", ""),
            ('UNLIT', "Unlit", ""),
            ('SHADED', "Shaded", ""),
        )
    )

    #------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def register():
        bpy.types.Scene.plyvpl_material_shading = bpy.props.EnumProperty(name = '', 
            items=(
                ('INVALID', "Invalid", ""),
                ('UNLIT', "Unlit", ""),
                ('SHADED', "Shaded", ""),
            )
        )

    @staticmethod
    def unregister():
        del bpy.types.Scene.plyvpl_material_shading

    #------------------------------------------------------------------------------------------------------------------
    def invoke(self, context, event):
        bpy.types.Scene.plyvpl_material_shading = self.action
        return self.execute(context)

    def execute(self, context):
        obj = context.object
                
        if bpy.types.Scene.plyvpl_material_shading == 'INVALID':
            bpy.types.Scene.plyvpl_material_shading = 'UNLIT' if self.action == 'INVALID' else self.action

        try:
            addon_extension = obj.plyvpl_addon_extension
            color_attribs = obj.data.color_attributes
        except:
            self.report({'ERROR'}, "Invalid object selected")
            return {"CANCELLED"}

        layers = addon_extension.layers

        self.report({'INFO'}, "Updating Vertext Paint Layers Material: " + str(bpy.types.Scene.plyvpl_material_shading))

        # create material if needed
        mat = (bpy.data.materials.get(self.material_name) or bpy.data.materials.new(self.material_name))        
        mat.use_nodes = True

        # check that the material is on the object
        if obj.data.materials.find(self.material_name) < 0:
            obj.data.materials.append(mat)

        # setup the material        
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links        
        nodes.clear()
        main_node = nodes.new("ShaderNodeOutputMaterial")
        
        if bpy.types.Scene.plyvpl_material_shading == 'SHADED':
            node = nodes.new("ShaderNodeBsdfPrincipled")
            node.location = Vector(( main_node.location.x - node.width * 1.5, main_node.location.y ))
            links.new(main_node.inputs[0], node.outputs[0])
            main_node = node

        if len(layers) == 0:
            return {"FINISHED"}

        # if only one layer then link vertex color to output direct        
        if len(layers) == 1:            
            color_node = nodes.new("ShaderNodeVertexColor")       
            color_node.layer_name = color_attribs[layers[0].color_attr_index].name
            color_node.location = Vector(( main_node.location.x - color_node.width * 1.5, main_node.location.y ))
            links.new(main_node.inputs[0], color_node.outputs[0])
            return {"FINISHED"}

        prev_mix_node = None
        location = Vector(( main_node.location.x, main_node.location.y ))
        for idx in range(0, len(layers)):

            color_node = nodes.new("ShaderNodeVertexColor")
            color_node.layer_name = color_attribs[layers[idx].color_attr_index].name
            color_node.location = location
            color_node.location.x -= color_node.width * 1.5

            # if last then no mix node for it. connect direct to prev mix node
            if idx == len(layers) - 1:
                links.new(mix_node.inputs[1], color_node.outputs[0])
                break

            mix_node = nodes.new("ShaderNodeMixRGB")
            mix_node.blend_type = layers[idx].blend_mode
            mix_node.inputs[0].default_value = layers[idx].blend_factor
            mix_node.location = location
            mix_node.location.x -= mix_node.width * 1.5
            
            links.new(mix_node.inputs[2], color_node.outputs[0])

            if prev_mix_node is None:
                links.new(main_node.inputs[0], mix_node.outputs[0])
            else:
                links.new(prev_mix_node.inputs[1], mix_node.outputs[0])

            prev_mix_node = mix_node
            
            location.x -= color_node.width * 1.5
            color_node.location.x = location.x - color_node.width * 1.5
            color_node.location.y = location.y - mix_node.height * 2

        return {"FINISHED"}

#======================================================================================================================
class PLYVPL_OT_list_actions(bpy.types.Operator):
    
    bl_idname = "custom.plyvpl_list_actions"
    bl_label = "Action"
    bl_description = "Action"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
        )
    )

    #------------------------------------------------------------------------------------------------------------------
    def invoke(self, context, event):

        obj = context.object
        addon_extension = obj.plyvpl_addon_extension
        color_attribs = obj.data.color_attributes

        if self.action == 'ADD':
            self.action_add(obj, addon_extension, color_attribs)
        elif self.action == 'REMOVE':
            self.action_remove(obj, addon_extension, color_attribs)
        elif self.action == 'UP':
            self.action_move_up(obj, addon_extension, color_attribs)
        elif self.action == 'DOWN':
            self.action_move_down(obj, addon_extension, color_attribs)

        return {"FINISHED"}

    #------------------------------------------------------------------------------------------------------------------
    def action_add(self, obj, addon_extension, color_attribs):
        self.report({'INFO'}, "Add new Vertext Paint Layer and Color Attribute")
        
        # add attribute
        bpy.ops.geometry.color_attribute_add(domain = 'CORNER', data_type = 'BYTE_COLOR')

        # force resync to pick up new atribute and make associated layer active
        active_color_index = color_attribs.active_color_index
        bpy.ops.custom.plyvpl_action_sync_attribs()

        # find which layer should be force selected and move it to top
        active_index = -1
        for idx in range(0, len(addon_extension.layers)):
            if addon_extension.layers[idx].color_attr_index == active_color_index:
                active_index = idx
                break

        if active_index >= 0:
            addon_extension.layers.move(active_index, 0)
            addon_extension.active_index = 0

        bpy.ops.custom.plyvpl_action_update_material()

    #------------------------------------------------------------------------------------------------------------------
    def action_remove(self, obj, addon_extension, color_attribs):
        self.report({'INFO'}, "Remove selected Vertext Paint Layer and Color Attribute")
        if addon_extension.active_index < 0 or addon_extension.active_index >= len(addon_extension.layers):
            return

        layer_idx = addon_extension.active_index
        attrib_idx = addon_extension.layers[layer_idx].color_attr_index

        # make sure color atrib is selected then delete it via ops
        try:
            color_attribs.active_color_index = attrib_idx
            bpy.ops.geometry.color_attribute_remove()
        except:
            pass
        
        # all color_attr_index after attrib_idx are now wrong by one
        for idx in range(0, len(addon_extension.layers)):
            if addon_extension.layers[idx].color_attr_index > attrib_idx:
                addon_extension.layers[idx].color_attr_index -= 1

        # select a layer one lower in list so that one being deleted is not longer selected
        addon_extension.active_index = layer_idx - 1
        if addon_extension.active_index < 0 and len(addon_extension.layers) - 1 > 0:
            addon_extension.active_index = 0
               
        # remove the layer
        addon_extension.layers.remove(layer_idx)

        bpy.ops.custom.plyvpl_action_update_material()

    #------------------------------------------------------------------------------------------------------------------
    def action_move_up(self, obj, addon_extension, color_attribs):
        self.report({'INFO'}, "Move Vertext Paint Layer up")
        idx = addon_extension.active_index
        if idx > 0:
            addon_extension.layers.move(idx, idx - 1)
            addon_extension.active_index = idx - 1
            bpy.ops.custom.plyvpl_action_update_material()

    #------------------------------------------------------------------------------------------------------------------
    def action_move_down(self, obj, addon_extension, color_attribs):
        self.report({'INFO'}, "Move Vertext Paint Layer down")        
        idx = addon_extension.active_index
        if idx < len(addon_extension.layers) - 1:
            addon_extension.layers.move(idx, idx + 1)
            addon_extension.active_index = idx + 1
            bpy.ops.custom.plyvpl_action_update_material()

#======================================================================================================================
