import bpy
import mathutils
from bpy import context as C
import numpy as np
import random

from bpy.props import FloatProperty
from bpy.props import IntProperty

bl_info = {
    "name": "Awesomium Tools",
    "author": "MrKuBu",
    "location": "3D View > Properties > AWTool",
    "description": "Easy working for blendshapes and other. ",
    "tracker_url": "https://mrkubu.github.io/",  
    "category": "Animation",
    "blender": (2, 80, 0),
}

bpy.types.Scene.RotateRangeStartX = FloatProperty (
    name="Rotate Start X",
    description="RotateRangeStartX value",
    default=-0.1,
    min=-1,
    max=0
)

bpy.types.Scene.RotateRangeEndX = FloatProperty (
    name="Rotate End X",
    description="RotateRangeEndX value",
    default=0.1,
    min=0,
    max=1
)

bpy.types.Scene.RotateRangeStartY = FloatProperty (
    name="Rotate Start Y",
    description="RotateRangeStartY value",
    default=-0.05,
    min=-1,
    max=0
)

bpy.types.Scene.RotateRangeEndY = FloatProperty (
    name="Rotate End Y",
    description="RotateRangeEndY value",
    default=0.05,
    min=0,
    max=1
)

bpy.types.Scene.RotateRangeStartZ = FloatProperty (
    name="Rotate Start Z",
    description="RotateRangeStartZ value",
    default=-0.1,
    min=-1,
    max=0
)

bpy.types.Scene.RotateRangeEndZ = FloatProperty (
    name="Rotate End Z",
    description="RotateRangeEndZ value",
    default=0.1,
    min=0,
    max=1
)

bpy.types.Scene.ScaleEnd = FloatProperty (
    name="Scale End",
    description="ScaleEnd value",
    default=0.1,
    min=0,
    max=1
)

bpy.types.Scene.ScaleRangeStart = FloatProperty (
    name="Scale Start",
    description="ScaleRangeStart value",
    default=-0.1,
    min=-1,
    max=0
)

bpy.types.Scene.PosRangeStart = FloatProperty (
    name="Pos Start",
    description="PosRangeStart value",
    default=0,
    min=-1,
    max=0
)
bpy.types.Scene.PosRangeEnd = FloatProperty (
    name="Pos End",
    description="PosRangeEnd value",
    default=0,
    min=0,
    max=1
)

bpy.types.Scene.RateRangeGen = IntProperty (
    name="RateRangeGen",
    description="RateRangeGen value",
    default=1,
    min=1,
    max=1000
)

bpy.types.Scene.MaximumFrames= IntProperty (
    name="MaximumFrames",
    description="MaximumFrames value",
    default=100,
    min=1,
    max=100000
)

def copy_all_shape_keys():
    if len(bpy.context.selected_objects) == 2:
        source = bpy.context.selected_objects[1]
        dest = bpy.context.active_object
        for v in bpy.context.selected_objects:
            if v is not dest:
                source = v
                break
        
        # DEBUG
        #print("Source: ", source.name)
        #print("Model to transfer: ", dest.name)
        
        if source.data.shape_keys is None:
            print("Source object has no shape keys!") 
        else:
            for idx in range(1, len(source.data.shape_keys.key_blocks)):
                source.active_shape_key_index = idx
                print("Copying Shape Key - ", source.active_shape_key.name)
                bpy.ops.object.shape_key_transfer()

def LashesGen(context):
    obj = bpy.context.selected_objects[0]
    def stop_playback(scene):
        if scene.frame_current%scene.RateRangeGen==0:
            bpy.ops.object.duplicate({"object" : obj,"selected_objects" : [obj]}, linked=False)
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            i=len(bpy.context.selected_objects)-1
            bpy.context.selected_objects[i].animation_data_clear()
            print(dir(bpy.context.selected_objects[i]))
            bpy.context.selected_objects[i].rotation_euler[0] += random.uniform(scene.RotateRangeStartX, scene.RotateRangeEndX)
            bpy.context.selected_objects[i].rotation_euler[1] += random.uniform(scene.RotateRangeStartY, scene.RotateRangeEndY)
            bpy.context.selected_objects[i].rotation_euler[2] += random.uniform(scene.RotateRangeStartZ, scene.RotateRangeEndZ)+((scene.frame_current-scene.MaximumFrames/2)*0.01)
            bpy.context.selected_objects[i].scale[0] += random.uniform(scene.ScaleRangeStart, scene.ScaleEnd)
            bpy.context.selected_objects[i].scale[1] += random.uniform(scene.ScaleRangeStart, scene.ScaleEnd)
            bpy.context.selected_objects[i].scale[2] += random.uniform(scene.ScaleRangeStart, scene.ScaleEnd)
            bpy.context.selected_objects[i].location[2]+= random.uniform(scene.PosRangeStart, scene.PosRangeEnd)
        if scene.frame_current == scene.MaximumFrames:
            bpy.ops.screen.animation_cancel(restore_frame=True)
            bpy.app.handlers.frame_change_pre.remove(stop_playback)

    bpy.app.handlers.frame_change_pre.append(stop_playback)
    bpy.ops.screen.animation_play()

class AWTools_CleanDrivers(bpy.types.Operator):
    """Clear driver from shapekeys"""
    bl_idname = "awt.cleandrivers"
    bl_label = "Clear drivers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        assert bpy.context.mode == 'OBJECT', "Must be in object mode!"

        for ob in bpy.context.selected_objects:
            if not ob.data.shape_keys: continue

            for b in C.active_object.data.shape_keys.key_blocks:
                b.driver_remove('value')
            
        return {'FINISHED'}

class AWTools_CleanEmptyBlendshapes(bpy.types.Operator):
    """Clear empty shapekeys"""
    bl_idname = "awt.cleanlessblends"
    bl_label = "Clear empty shapes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tolerance = 0.001

        assert bpy.context.mode == 'OBJECT', "Must be in object mode!"

        for ob in bpy.context.selected_objects:
            if ob.type != 'MESH': continue
            if not ob.data.shape_keys: continue
            if not ob.data.shape_keys.use_relative: continue

            kbs = ob.data.shape_keys.key_blocks
            nverts = len(ob.data.vertices)
            to_delete = []

            cache = {}

            locs = np.empty(3*nverts, dtype=np.float32)

            for kb in kbs:
                if kb == kb.relative_key: continue

                kb.data.foreach_get("co", locs)

                if kb.relative_key.name not in cache:
                    rel_locs = np.empty(3*nverts, dtype=np.float32)
                    kb.relative_key.data.foreach_get("co", rel_locs)
                    cache[kb.relative_key.name] = rel_locs
                rel_locs = cache[kb.relative_key.name]

                locs -= rel_locs
                if (np.abs(locs) < tolerance).all():
                    to_delete.append(kb.name)

            for kb_name in to_delete:
                ob.shape_key_remove(ob.data.shape_keys.key_blocks[kb_name])
                
        return {'FINISHED'}

class AWTools_TransferBlendshapes(bpy.types.Operator):
    """Transfer blendshapes 1 to 2 model"""
    bl_idname = "awt.transferblend"
    bl_label = "Transfer blendshapes 1 to 2"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        copy_all_shape_keys()

        return {'FINISHED'}

class AWTools_Renamer(bpy.types.PropertyGroup):
    Key: bpy.props.StringProperty(name="Key")
    ReplaceName: bpy.props.StringProperty(name="Replace Name")

class AWTools_RenameBlendshapes(bpy.types.Operator):
    """Rename shapes"""
    bl_idname = "awt.renameshapes"
    bl_label = "Rename blendshapes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        key_value = context.scene.Renamer.Key
        replace_name_value = context.scene.Renamer.ReplaceName

        # DEBUG
        #print("Key:", key_value)
        #print("Replace Name:", replace_name_value)

        selected_object = bpy.context.object
        shape_keys = selected_object.data.shape_keys.key_blocks

        for key in shape_keys:
            key.name = key.name.replace(key_value, replace_name_value)

        return {'FINISHED'}


class AWTools_EyelashesGenerator(bpy.types.Operator):
    """Generate eye lashes (BezierCurve and mesh)"""
    bl_idname = "awt.eyelashesgen"
    bl_label = "Eyelashes Create"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        LashesGen(context)
        return {'FINISHED'}

class AWTools_ui(bpy.types.Panel):
    bl_label = "Awesomium tools"
    bl_idname = "OBJECT_PT_panel"
    bl_category = "AWTool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Cleaner (Select mesh)")
        
        row = layout.row()
        row.operator("awt.cleandrivers", text="Clear all driver shape keys", icon="PANEL_CLOSE")
        row = layout.row()
        row.operator("awt.cleanlessblends", text="Clear empty shape keys", icon="FULLSCREEN_EXIT")

        layout.separator()
        layout.label(text="Transfer shapekey (Select [1]parent and [2]child )")
        row = layout.row()
        row.operator("awt.transferblend", text="Transfer", icon="TRACKING_FORWARDS_SINGLE")
        
        layout.separator()
        layout.label(text="Renamer shapekeys")

        scene = context.scene
        renamescene = scene.Renamer
        
        row = layout.row()
        row.prop(renamescene, "Key")
        
        row = layout.row()
        row.prop(renamescene, "ReplaceName")

        row = layout.row()
        row.operator("awt.renameshapes", text="Rename", icon="OUTLINER_DATA_GP_LAYER")

        # DEBUG
        #key_value = renamescene.Key
        #replace_name_value = renamescene.ReplaceName
        #print("Key:", key_value)
        #print("Replace Name:", replace_name_value)

        layout.separator()
        layout.label(text="Lashes generator")

        row = layout.row()
        row.prop(scene, "RotateRangeStartX")
        row.prop(scene, "RotateRangeEndX")
        row = layout.row()
        row.prop(scene, "RotateRangeStartY")
        row.prop(scene, "RotateRangeEndY")
        row = layout.row()
        row.prop(scene, "RotateRangeStartZ")
        row.prop(scene, "RotateRangeEndZ")
        
        layout.label(text="Random Scale")
        row = layout.row()
        row.prop(scene, "ScaleRangeStart")
        row.prop(scene, "ScaleEnd")
        layout.label(text="Random Position Interval")
        row = layout.row()
        row.prop(scene, "PosRangeStart")
        row.prop(scene, "PosRangeEnd")
        
        layout.label(text="Rate")
        row = layout.row()
        row.prop(scene, "RateRangeGen")
        layout.label(text="Maximum Frames")
        row = layout.row()
        row.prop(scene, "MaximumFrames")

        row = layout.row()
        row.operator("awt.eyelashesgen", text="Generate eye lashes (BezierCurve and mesh)", icon="SEQ_HISTOGRAM")

classes = (
    AWTools_CleanDrivers,
    AWTools_CleanEmptyBlendshapes,
    AWTools_TransferBlendshapes,
    AWTools_Renamer,
    AWTools_RenameBlendshapes,
    AWTools_EyelashesGenerator,
    AWTools_ui,
)

#register, unregister = bpy.utils.register_classes_factory(classes)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.Renamer = bpy.props.PointerProperty(type=AWTools_Renamer)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.Renamer

if __name__ == "__main__":
    register()
