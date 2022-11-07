# VertexPaintLayers


This Blender add-on creates a new panel in the side bar where you can manage Colour Attributes as if they were layered.

### Installation

Grab the zip from releases (see right-side) and install like any other Blender add-on.

### Usage

*Layers and Color Attributes*

Use [+] / [-] buttons to add or remove new layers. This will create or remove an associated colour attribute. Use the `Sync Color Attributes` button if you created colour attributes via the objects data properties panel and want them added as layers. Keep in mind though that if you were to remove that layer the colour attribute would be removed too.

The up/down arrow buttons can be used to move layers. This does not affect the position of the actual attribute in the list of attributes.

*Preview Material*

![](/img/000.png) 

A new material called `Material (Vertex Paint Layers)` will be added to the object. This material is used for previewing the mixed layers when _Viewport Shading: *Material Preview*_ is on. ![](/img/001.png)

You can switch to ![](/img/002.png) _Viewport Shading: *Solid*_ to view the colour of an individual layer while in `Vertex Paint` mode.

![](/img/003.png) 


Use the `Unlit` and `Shaded` buttons to change what the final preview material looks like. They are basically the same except that the Shaded version has a Principled BSDF node added before the output.


![](/img/004.png) 





