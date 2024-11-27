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

def copy_all_shape_keys(self):
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
            self.report({'WARNING'}, "Source object has no shape keys!")
        else:
            for idx in range(1, len(source.data.shape_keys.key_blocks)):
                source.active_shape_key_index = idx
                print("Copying Shape Key - ", source.active_shape_key.name)
                bpy.ops.object.shape_key_transfer()
            self.report({'INFO'}, "Sucess transfered shape keys!")

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

def get_rotation_mode(obj):
    if obj.rotation_mode in ('QUATERNION', 'AXIS_ANGLE'):
        return obj.rotation_mode.lower()
    return 'euler'


def get_selected_objects(context):
    if context.mode not in ('OBJECT', 'POSE'):
        return

    if context.mode == 'OBJECT':
        active = context.active_object
        selected = [obj for obj in context.selected_objects if obj != active]

    if context.mode == 'POSE':
        active = context.active_pose_bone
        selected = [bone for bone in context.selected_pose_bones if bone != active]

    selected.append(active)
    return selected


def get_last_dymanic_parent_constraint(obj):
    if not obj.constraints:
        return
    const = obj.constraints[-1]
    if const.name.startswith("DP_") and const.influence == 1:
        return const


def insert_keyframe(obj, frame):
    rotation_mode = get_rotation_mode(obj)
    data_paths = (
         'location',
        f'rotation_{rotation_mode}',
         'scale',
    )
    for data_path in data_paths:
        obj.keyframe_insert(data_path=data_path, frame=frame)


def insert_keyframe_constraint(constraint, frame):
    constraint.keyframe_insert(data_path='influence', frame=frame)


def dp_keyframe_insert_obj(obj):
    obj.keyframe_insert(data_path="location")
    if obj.rotation_mode == 'QUATERNION':
        obj.keyframe_insert(data_path="rotation_quaternion")
    elif obj.rotation_mode == 'AXIS_ANGLE':
        obj.keyframe_insert(data_path="rotation_axis_angle")
    else:
        obj.keyframe_insert(data_path="rotation_euler")
    obj.keyframe_insert(data_path="scale")


def dp_keyframe_insert_pbone(arm, pbone):
    arm.keyframe_insert(data_path='pose.bones["'+pbone.name+'"].location')
    if pbone.rotation_mode == 'QUATERNION':
        arm.keyframe_insert(data_path='pose.bones["'+pbone.name+'"].rotation_quaternion')
    elif pbone.rotation_mode == 'AXIS_ANGLE':
        arm.keyframe_insert(data_path='pose.bones["'+pbone.name+'"].rotation_axis_angel')
    else:
        arm.keyframe_insert(data_path='pose.bones["'+pbone.name+'"].rotation_euler')
    arm.keyframe_insert(data_path='pose.bones["'+pbone.name+'"].scale') 


def dp_create_dynamic_parent_obj(op):
    obj = bpy.context.active_object
    scn = bpy.context.scene
    list_selected_obj = bpy.context.selected_objects

    if len(list_selected_obj) == 2:
        i = list_selected_obj.index(obj)
        list_selected_obj.pop(i)
        parent_obj = list_selected_obj[0]

        dp_keyframe_insert_obj(obj)
        bpy.ops.object.constraint_add_with_targets(type='CHILD_OF')
        last_constraint = obj.constraints[-1]

        if parent_obj.type == 'ARMATURE':
            last_constraint.subtarget = parent_obj.data.bones.active.name
            last_constraint.name = "DP_"+last_constraint.target.name+"."+last_constraint.subtarget
        else:
            last_constraint.name = "DP_"+last_constraint.target.name

        C = bpy.context.copy()
        C["constraint"] = last_constraint
        bpy.ops.constraint.childof_set_inverse(C, constraint=last_constraint.name, owner='OBJECT')

        current_frame = scn.frame_current
        scn.frame_current = current_frame-1
        obj.constraints[last_constraint.name].influence = 0
        obj.keyframe_insert(data_path='constraints["'+last_constraint.name+'"].influence')

        scn.frame_current = current_frame
        obj.constraints[last_constraint.name].influence = 1
        obj.keyframe_insert(data_path='constraints["'+last_constraint.name+'"].influence')

        for ob in list_selected_obj:
            ob.select_set(False)

        obj.select_set(True)
    else:
        op.report({'ERROR'}, "Two objects must be selected")

def dp_create_dynamic_parent_pbone(op):
    arm = bpy.context.active_object
    pbone = bpy.context.active_pose_bone
    scn = bpy.context.scene
    list_selected_obj = bpy.context.selected_objects

    if len(list_selected_obj) == 2 or len(list_selected_obj) == 1:
        if len(list_selected_obj) == 2:
            i = list_selected_obj.index(arm)
            list_selected_obj.pop(i)
            parent_obj = list_selected_obj[0]
            if parent_obj.type == 'ARMATURE':
                parent_obj_pbone = parent_obj.data.bones.active
        else:
            parent_obj = arm
            selected_bones = bpy.context.selected_pose_bones
            selected_bones.remove(pbone)
            parent_obj_pbone = selected_bones[0]

        dp_keyframe_insert_pbone(arm, pbone)
        bpy.ops.pose.constraint_add_with_targets(type='CHILD_OF')
        last_constraint = pbone.constraints[-1]

        if parent_obj.type == 'ARMATURE':
            last_constraint.subtarget = parent_obj_pbone.name
            last_constraint.name = "DP_"+last_constraint.target.name+"."+last_constraint.subtarget
        else:
            last_constraint.name = "DP_"+last_constraint.target.name

        C = bpy.context.copy()
        C["constraint"] = last_constraint
        bpy.ops.constraint.childof_set_inverse(C, constraint=last_constraint.name, owner='BONE')
        
        current_frame = scn.frame_current
        scn.frame_current = current_frame-1
        pbone.constraints[last_constraint.name].influence = 0
        arm.keyframe_insert(data_path='pose.bones["'+pbone.name+'"].constraints["'+last_constraint.name+'"].influence')
        
        scn.frame_current = current_frame
        pbone.constraints[last_constraint.name].influence = 1
        arm.keyframe_insert(data_path='pose.bones["'+pbone.name+'"].constraints["'+last_constraint.name+'"].influence')  
    else:
        op.report({'ERROR'}, "Two objects must be selected")


def disable_constraint(obj, const, frame):
    if type(obj) == bpy.types.PoseBone:
        matrix_final = obj.matrix
    else:
        matrix_final = obj.matrix_world

    insert_keyframe(obj, frame=frame-1)
    insert_keyframe_constraint(const, frame=frame-1)

    const.influence = 0
    if type(obj) == bpy.types.PoseBone:
        obj.matrix = matrix_final
    else:
        obj.matrix_world = matrix_final

    insert_keyframe(obj, frame=frame)
    insert_keyframe_constraint(const, frame=frame)
    return


def dp_clear(obj, pbone):
    dp_curves = []
    dp_keys = []
    for fcurve in obj.animation_data.action.fcurves:
        if "constraints" in fcurve.data_path and "DP_" in fcurve.data_path:
            dp_curves.append(fcurve)

    for f in dp_curves:
        for key in f.keyframe_points:
            dp_keys.append(key.co[0])

    dp_keys = list(set(dp_keys))
    dp_keys.sort()

    for fcurve in obj.animation_data.action.fcurves[:]:
        if fcurve.data_path.startswith("constraints") and "DP_" in fcurve.data_path:
            obj.animation_data.action.fcurves.remove(fcurve)
        else:
            for frame in dp_keys:
                for key in fcurve.keyframe_points[:]:
                    if key.co[0] == frame:
                        fcurve.keyframe_points.remove(key)
            if not fcurve.keyframe_points:
                obj.animation_data.action.fcurves.remove(fcurve)

    if pbone:
        obj = pbone
    for const in obj.constraints[:]:
        if const.name.startswith("DP_"):
            obj.constraints.remove(const)

import bpy

def set_custom_shape_to_bones(custom_object_name):
    # Ensure the custom object exists
    custom_object = bpy.data.objects.get(custom_object_name)
    if not custom_object:
        print(f"Object '{custom_object_name}' does not exist.")
        return {'CANCELLED'}

    # Ensure we are dealing with an armature and are in Pose Mode
    if bpy.context.active_object.type != 'ARMATURE' or bpy.context.mode != 'POSE':
        print("Must be in Pose Mode with an armature selected.")
        return {'CANCELLED'}
    
    armature = bpy.context.active_object
    selected_bones = bpy.context.selected_pose_bones
    
    # Set shape
    for bone in selected_bones:
        bone.custom_shape = custom_object
        print(f"Set custom shape for bone '{bone.name}'")
    return {'FINISHED'}

class AWTools_LowercaseShapeKeys(bpy.types.Operator):
    """Change shape key names to lowercase"""
    bl_idname = "awt.lowercaseshapekeys"
    bl_label = "Lowercase shape keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for ob in context.selected_objects:
            if ob.data.shape_keys:
                for b in ob.data.shape_keys.key_blocks:
                    if b.name != "Base":
                        b.name = b.name[0].lower() + b.name[1:]

            self.report({'INFO'}, "Sucess renamed shapekeys to lowercase name.")
        return {'FINISHED'}

class AWTools_SetAllShapeKeysValuesToZero(bpy.types.Operator):
    """Sets all shapekey values to 0"""
    bl_idname = "awt.setallshapekeyvaluestozero"
    bl_label = "Set all shape keys values to 0"
    bl_description = "Sets all shapekey values to 0 WITHOUT inserting a keyframe."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for obj in bpy.context.selected_objects:

            if obj and obj.type == 'MESH' and obj.data.shape_keys:
                for key in obj.data.shape_keys.key_blocks:
                    key.value = 0
        bpy.context.view_layer.update()
        self.report({'INFO'}, "Sucess setted all shapekeys to 0.")
        return {"FINISHED"}

class AWTools_CleanDrivers(bpy.types.Operator):
    """Clear driver from shapekeys"""
    bl_idname = "awt.cleandrivers"
    bl_label = "Clear drivers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            self.report({'WARNING'}, "Must be in object mode!")
            return {'CANCELLED'}
        
        for ob in context.selected_objects:
            if ob.data.shape_keys:
                for b in ob.data.shape_keys.key_blocks:
                    b.driver_remove('value')

                self.report({'INFO'}, "Sucess cleared all drivers!")
        return {'FINISHED'}

class AWTools_CleanEmptyBlendshapes(bpy.types.Operator):
    """Clear empty shapekeys"""
    bl_idname = "awt.cleanlessblends"
    bl_label = "Clear empty shapes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tolerance = 0.001

        if bpy.context.mode != 'OBJECT':
            self.report({'WARNING'}, "Must be in object mode!")
            return {'CANCELLED'}

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

            self.report({'INFO'}, "Sucess cleared empty shapes!")
                
        return {'FINISHED'}

class AWTools_CleanMaterials(bpy.types.Operator):
    """Clear unused materials"""
    bl_idname = "awt.clearmaterials"
    bl_label = "Clear unused materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for material in bpy.data.materials:
            if not material.users:
                bpy.data.materials.remove(material)
                print(material)
        
        self.report({'INFO'}, "Try delete unused materials.")
        return {'FINISHED'}

class AWTools_CleanTextures(bpy.types.Operator):
    """Clear unused textures"""
    bl_idname = "awt.cleartextures"
    bl_label = "Clear unused textures"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for texture in bpy.data.textures:
            if not texture.users:
                bpy.data.textures.remove(texture)
                print(texture)

        self.report({'INFO'}, "Try delete unused images.")
        return {'FINISHED'}

class AWTools_TransferBlendshapes(bpy.types.Operator):
    """Transfer blendshapes 1 to 2 model"""
    bl_idname = "awt.transferblend"
    bl_label = "Transfer blendshapes 1 to 2"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        copy_all_shape_keys(self)

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

        self.report({'INFO'}, "Shapes renamed.")
        return {'FINISHED'}


class AWTools_Renamerbone(bpy.types.PropertyGroup):
    KeyBone: bpy.props.StringProperty(name="Key")
    ReplaceNameBone: bpy.props.StringProperty(name="Replace Name")

class AWTools_RenameBones(bpy.types.Operator):
    """Rename bones"""
    bl_idname = "awt.renamebones"
    bl_label = "Rename bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        key_value = context.scene.Renamerbone.KeyBone
        replace_name_value = context.scene.Renamerbone.ReplaceNameBone

        selected_armature = bpy.context.object
        bones = selected_armature.data.bones

        for bone in bones:
            bone.name = bone.name.replace(key_value, replace_name_value)

        self.report({'INFO'}, "Bones renamed.")
        return {'FINISHED'}


class AWTools_TransferLimitIK(bpy.types.Operator):
    """Transfer Limit Rotation To IK"""
    bl_idname = "awt.transferlimittoik"
    bl_label = "TransferLimitToIK"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.active_object.type == 'ARMATURE' and bpy.context.active_pose_bone:
            pose_bone = bpy.context.active_pose_bone

            limit_rot = next((con for con in pose_bone.constraints if con.type == 'LIMIT_ROTATION'), None)

            if limit_rot:
                # Copy data IK
                pose_bone.use_ik_limit_x = limit_rot.use_limit_x
                pose_bone.use_ik_limit_y = limit_rot.use_limit_y
                pose_bone.use_ik_limit_z = limit_rot.use_limit_z

                # Set limit IK from Limit Rotation
                pose_bone.ik_min_x = limit_rot.min_x if limit_rot.use_limit_x else 0.0
                pose_bone.ik_max_x = limit_rot.max_x if limit_rot.use_limit_x else 0.0
                pose_bone.ik_min_y = limit_rot.min_y if limit_rot.use_limit_y else 0.0
                pose_bone.ik_max_y = limit_rot.max_y if limit_rot.use_limit_y else 0.0
                pose_bone.ik_min_z = limit_rot.min_z if limit_rot.use_limit_z else 0.0
                pose_bone.ik_max_z = limit_rot.max_z if limit_rot.use_limit_z else 0.0
                
                self.report({'INFO'}, "Limit Rotation data has been copied to IK settings for the bone.")
            else:
                self.report({'WARNING'}, "The Limit Rotation constraint was not found on the selected bone.")
        else:
            self.report({'ERROR'}, "Please select an armature and a pose bone.")
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

class AWTools_DYNAMIC_PARENT_create(bpy.types.Operator):
    """Create a new animated Child Of constraint"""
    bl_idname = "awt.dynamic_parent_create"
    bl_label = "Create Constraint"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        frame = context.scene.frame_current

        if obj.type == 'ARMATURE':
            if obj.mode != 'POSE':
                self.report({'ERROR'}, "Armature objects must be in Pose mode.")
                return {'CANCELLED'}
            obj = bpy.context.active_pose_bone
            const = get_last_dymanic_parent_constraint(obj)
            if const:
                disable_constraint(obj, const, frame)
            dp_create_dynamic_parent_pbone(self)
        else:
            const = get_last_dymanic_parent_constraint(obj)
            if const:
                disable_constraint(obj, const, frame)
            dp_create_dynamic_parent_obj(self)

        return {'FINISHED'}


class AWTools_DYNAMIC_PARENT_disable(bpy.types.Operator):
    """Disable the current animated Child Of constraint"""
    bl_idname = "awt.dynamic_parent_disable"
    bl_label = "Disable Constraint"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode in ('OBJECT', 'POSE')

    def execute(self, context):
        frame = context.scene.frame_current
        objects = get_selected_objects(context)
        counter = 0

        if not objects:
            self.report({'ERROR'}, 'Nothing selected.')
            return {'CANCELLED'}

        for obj in objects:
            const = get_last_dymanic_parent_constraint(obj)
            if const is None:
                continue
            disable_constraint(obj, const, frame)
            counter += 1
        self.report({'INFO'}, f'{counter} constraints were disabled.')
        return {'FINISHED'}


class AWTools_DYNAMIC_PARENT_clear(bpy.types.Operator):
    """Clear Dynamic Parent constraints"""
    bl_idname = "awt.dynamic_parent_clear"
    bl_label = "Clear Dynamic Parent"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        pbone = None
        obj = bpy.context.active_object
        if obj.type == 'ARMATURE':
            pbone = bpy.context.active_pose_bone

        dp_clear(obj, pbone)

        return {'FINISHED'}

class AWTools_DYNAMIC_PARENT_bake(bpy.types.Operator):
    """Bake Dynamic Parent animation"""
    bl_idname = "awt.dynamic_parent_bake"
    bl_label = "Bake Dynamic Parent"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.active_object
        scn = bpy.context.scene

        if obj.type == 'ARMATURE':
            obj = bpy.context.active_pose_bone
            bpy.ops.nla.bake(frame_start=scn.frame_start, 
                             frame_end=scn.frame_end, step=1, 
                             only_selected=True, visual_keying=True,
                             clear_constraints=False, clear_parents=False, 
                             bake_types={'POSE'})
            for const in obj.constraints[:]:
                if const.name.startswith("DP_"):
                    obj.constraints.remove(const)
        else:
            bpy.ops.nla.bake(frame_start=scn.frame_start,
                             frame_end=scn.frame_end, step=1, 
                             only_selected=True, visual_keying=True,
                             clear_constraints=False, clear_parents=False, 
                             bake_types={'OBJECT'})
            for const in obj.constraints[:]:
                if const.name.startswith("DP_"):
                    obj.constraints.remove(const)

        return {'FINISHED'}

class AWTools_DYNAMIC_PARENT_clear_menu(bpy.types.Menu):
    """Clear or bake Dynamic Parent constraints"""
    bl_label = "Clear Dynamic Parent?"
    bl_idname = "awt.dynamic_parent_clear_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("awt.dynamic_parent_clear", text="Clear", icon="X")
        layout.operator("awt.dynamic_parent_bake", text="Bake and clear", icon="REC")


class AWTools_Transferweightname(bpy.types.PropertyGroup):
    KeyOldWeight: bpy.props.StringProperty(name="Old Weight")
    AddActiveBoneWeight: bpy.props.StringProperty(name="Active bone")
    DellOldWeight: bpy.props.BoolProperty(name="Delete old weight", default=False)

class AWTools_TransferWeightbonestobone(bpy.types.Operator):
    """Transfer weight bones (2) to bone (1)"""
    bl_idname = "awt.transferweightbonestobone"
    bl_label = "Transfer weight bones to bone"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.active_object

        getOldWeight = context.scene.Transferweightname.KeyOldWeight
        weightAdd = context.scene.Transferweightname.AddActiveBoneWeight
        Dellold = context.scene.Transferweightname.DellOldWeight

        if obj.type != 'MESH':
            self.report({'WARNING'}, "Must be in object mode!")
            return {'CANCELLED'}

        for obj in bpy.context.selected_objects:
            if obj.type != 'MESH': continue

            if getOldWeight in obj.vertex_groups and weightAdd in obj.vertex_groups:
                # Get index
                new_bone_vgroup_index = obj.vertex_groups[weightAdd].index

                # loop vertex and get weight
                for vertex in obj.data.vertices:
                    old_weight = 0
                    # Get weight old
                    for group in vertex.groups:
                        if group.group == obj.vertex_groups[getOldWeight].index:
                            old_weight = group.weight
                            break
                    # Add weight to selected weight
                    for group in vertex.groups:
                        if group.group == new_bone_vgroup_index:
                            # Add weight
                            obj.vertex_groups[new_bone_vgroup_index].add([vertex.index], old_weight, 'ADD')
                            break
                    else:
                        # If no weight found, add new
                        obj.vertex_groups[new_bone_vgroup_index].add([vertex.index], old_weight, 'REPLACE')


                if Dellold:
                    obj.vertex_groups.remove(obj.vertex_groups[getOldWeight])

            bpy.context.view_layer.update()
        
        return {'FINISHED'}

class AWTools_TransferWeightbonestobonemass(bpy.types.Operator):
    """Transfer weight bones (2) to bone (1) for all objects"""
    bl_idname = "awt.transferweightbonestobonemass"
    bl_label = "Transfer weight bones to bone for all objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.active_object

        getOldWeight = context.scene.Transferweightname.KeyOldWeight
        weightAdd = context.scene.Transferweightname.AddActiveBoneWeight
        Dellold = context.scene.Transferweightname.DellOldWeight

        if bpy.context.active_object.type != 'MESH':
            self.report({'WARNING'}, "Must be in object mode!")
            return {'CANCELLED'}

        for obj in bpy.context.scene.objects:
            if obj.type != 'MESH': continue

            if getOldWeight in obj.vertex_groups and weightAdd in obj.vertex_groups:
                new_bone_vgroup_index = obj.vertex_groups[weightAdd].index

                for vertex in obj.data.vertices:
                    old_weight = 0
                    for group in vertex.groups:
                        if group.group == obj.vertex_groups[getOldWeight].index:
                            old_weight = group.weight
                            break
                    
                    for group in vertex.groups:
                        if group.group == new_bone_vgroup_index:
                            obj.vertex_groups[new_bone_vgroup_index].add([vertex.index], old_weight, 'ADD')
                            break
                    else:
                        obj.vertex_groups[new_bone_vgroup_index].add([vertex.index], old_weight, 'REPLACE')

                if Dellold:
                    obj.vertex_groups.remove(obj.vertex_groups[getOldWeight])

                bpy.context.view_layer.update()
        
        return {'FINISHED'}

class AWTools_TransferWeightbonestobonemassrig(bpy.types.Operator):
    """Transfer weight bones (2) to bone (1) for all objects rig"""
    bl_idname = "awt.transferweightbonestobonemassrig"
    bl_label = "Transfer weight bones to bone for all objects rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_object = bpy.context.active_object

        getOldWeight = context.scene.Transferweightname.KeyOldWeight
        weightAdd = context.scene.Transferweightname.AddActiveBoneWeight
        Dellold = context.scene.Transferweightname.DellOldWeight

        if selected_object.type == 'ARMATURE':
            linked_rig = selected_object
        elif selected_object.type == 'MESH':
            linked_rig = None
            for modifier in selected_object.modifiers:
                if modifier.type == 'ARMATURE':
                    linked_rig = modifier.object
                    break
        else:
            bpy.context.window_manager.popup_menu(lambda self, context: self.layout.operator("wm.popup_operator"), title="Select a mesh or armature object!")
            return {'CANCELLED'}

        if linked_rig is None:
            bpy.context.window_manager.popup_menu(lambda self, context: self.layout.operator("wm.popup_operator"), title="No armature linked to the selected mesh!")
            return {'CANCELLED'}

        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE' and modifier.object == linked_rig:
                        if getOldWeight in obj.vertex_groups and weightAdd in obj.vertex_groups:
                            new_bone_vgroup_index = obj.vertex_groups[weightAdd].index

                            for vertex in obj.data.vertices:
                                old_weight = 0
                                for group in vertex.groups:
                                    if group.group == obj.vertex_groups[getOldWeight].index:
                                        old_weight = group.weight
                                        break
                                
                                for group in vertex.groups:
                                    if group.group == new_bone_vgroup_index:
                                        obj.vertex_groups[new_bone_vgroup_index].add([vertex.index], old_weight, 'ADD')
                                        break
                                else:
                                    obj.vertex_groups[new_bone_vgroup_index].add([vertex.index], old_weight, 'REPLACE')

                            if Dellold:
                                obj.vertex_groups.remove(obj.vertex_groups[getOldWeight])

        bpy.context.view_layer.update()

        return {'FINISHED'}

class AWTools_SetCustomShape(bpy.types.Operator):
    """Set Custom Shape to Selected Bones"""
    bl_idname = "awt.set_custom_shape"
    bl_label = "Set Custom Shape to Selected Bones"
    bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        custom_object_name = context.scene.custom_object_to_bones.name
        return set_custom_shape_to_bones(custom_object_name)


class AWTools_CopyLocationHanddef(bpy.types.Operator):
    """Transfer 1 rig to 2 rig"""
    bl_idname = "awt.copylocationhand"
    bl_label = "ransfer 1 rig to 2 rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        target_rig = None
        selected_rig = bpy.context.selected_objects[0]
        target_rig = bpy.context.selected_objects[1]

        bone_mapping = {
            "hand_l": "hand_l",
            "pinky_01_l": "pinky_01_l",
            "pinky_02_l": "pinky_02_l",
            "pinky_03_l": "pinky_03_l",
            "ring_01_l": "ring_01_l",
            "ring_02_l": "ring_02_l",
            "ring_03_l": "ring_03_l",
            "middle_01_l": "middle_01_l",
            "middle_02_l": "middle_02_l",
            "middle_03_l": "middle_03_l",
            "index_01_l": "index_01_l",
            "index_02_l": "index_02_l",
            "index_03_l": "index_03_l",
            "thumb_01_l": "thumb_01_l",
            "thumb_02_l": "thumb_02_l",
            "thumb_03_l": "thumb_03_l",
            "hand_r": "hand_r",
            "pinky_01_r": "pinky_01_r",
            "pinky_02_r": "pinky_02_r",
            "pinky_03_r": "pinky_03_r",
            "ring_01_r": "ring_01_r",
            "ring_02_r": "ring_02_r",
            "ring_03_r": "ring_03_r",
            "middle_01_r": "middle_01_r",
            "middle_02_r": "middle_02_r",
            "middle_03_r": "middle_03_r",
            "index_01_r": "index_01_r",
            "index_02_r": "index_02_r",
            "index_03_r": "index_03_r",
            "thumb_01_r": "thumb_01_r",
            "thumb_02_r": "thumb_02_r",
            "thumb_03_r": "thumb_03_r",
        }


        selected_objects = bpy.context.selected_objects

        if len(selected_objects) == 2:
            for source_bone, target_bone in bone_mapping.items():
                constraint = selected_rig.pose.bones.get(source_bone).constraints.new('COPY_LOCATION')
                constraint.target = target_rig
                constraint.subtarget = target_bone
        else:
            self.report({'WARNING'}, "Select two rigs!")
        
        return {'FINISHED'}

class AWTools_CopyLocationHandarp(bpy.types.Operator):
    """Transfer 1 rig to 2 rig ARP"""
    bl_idname = "awt.copylocationhandarp"
    bl_label = "ransfer 1 rig to 2 rig (ARP)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        target_rig = None

        selected_rig = bpy.context.selected_objects[0]
        target_rig = bpy.context.selected_objects[1]

        bone_mapping = {
            "c_hand_fk.l": "hand_l",
            "c_hand_ik.l": "hand_l",
            "c_pinky1.l": "pinky_01_l",
            "c_pinky2.l": "pinky_02_l",
            "c_pinky3.l": "pinky_03_l",
            "c_ring1.l": "ring_01_l",
            "c_ring2.l": "ring_02_l",
            "c_ring3.l": "ring_03_l",
            "c_middle1.l": "middle_01_l",
            "c_middle2.l": "middle_02_l",
            "c_middle3.l": "middle_03_l",
            "c_index1.l": "index_01_l",
            "c_index2.l": "index_02_l",
            "c_index3.l": "index_03_l",
            "c_thumb1_base.l": "thumb_01_l",
            "c_thumb2.l": "thumb_02_l",
            "c_thumb3.l": "thumb_03_l",
            "c_hand_fk.r": "hand_r",
            "c_hand_ik.r": "hand_r",
            "c_pinky1.r": "pinky_01_r",
            "c_pinky2.r": "pinky_02_r",
            "c_pinky3.r": "pinky_03_r",
            "c_ring1.r": "ring_01_r",
            "c_ring2.r": "ring_02_r",
            "c_ring3.r": "ring_03_r",
            "c_middle1.r": "middle_01_r",
            "c_middle2.r": "middle_02_r",
            "c_middle3.r": "middle_03_r",
            "c_index1.r": "index_01_r",
            "c_index2.r": "index_02_r",
            "c_index3.r": "index_03_r",
            "c_thumb1_base.r": "thumb_01_r",
            "c_thumb2.r": "thumb_02_r",
            "c_thumb3.r": "thumb_03_r",
        }

        selected_objects = bpy.context.selected_objects

        if len(selected_objects) == 2:
            for source_bone, target_bone in bone_mapping.items():
                constraint = selected_rig.pose.bones.get(source_bone).constraints.new('COPY_LOCATION')
                constraint.target = target_rig
                constraint.subtarget = target_bone
        else:
            self.report({'WARNING'}, "Select two rigs!")
        
        return {'FINISHED'}

class AWTools_SelectRingAndMerge(bpy.types.Operator):
    """Select ring loops and merge"""
    bl_idname = "awt.selectring_merge"
    bl_label = "Select ring and merge"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        edit_object = bpy.context.edit_object
        if edit_object:
            mesh = edit_object.data
            if mesh.total_edge_sel > 0:
                bpy.ops.mesh.loop_multi_select(ring=True)
                bpy.ops.mesh.merge(type='COLLAPSE')

                # Merge UVs on collapsed edges (WIP)
                #bpy.ops.uv.select_all(action='SELECT')
                #bpy.ops.uv.weld()
                #bpy.ops.mesh.remove_doubles(threshold=0.0001, use_unselected=False)
                self.report({'INFO'}, "Sucess merged ring loops!")
            else:
                self.report({'WARNING'}, "Select one or more edges!")
        else:
            self.report({'ERROR'}, "Enter to edit mode!")

        return {'FINISHED'}

class AWTools_SelectRingAndDissolve(bpy.types.Operator):
    """Select ring loops and dissolve"""
    bl_idname = "awt.selectring_dissolve"
    bl_label = "Select ring and dissolve"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        edit_object = bpy.context.edit_object
        if edit_object:
            mesh = edit_object.data
            if mesh.total_edge_sel > 0:
                bpy.ops.mesh.loop_multi_select(ring=True)
                bpy.ops.mesh.dissolve_edges()
                self.report({'INFO'}, "Sucess dissolve ring loops!")
            else:
                self.report({'WARNING'}, "Select one or more edges!")
        else:
            self.report({'ERROR'}, "Enter to edit mode!")

        return {'FINISHED'}

class AWTools_RenameEngMMD(bpy.types.Operator):
    """Select bones and auto rename to englis bones"""
    bl_idname = "awt.renamemmdtoeng"
    bl_label = "Select bone and auto rename to english"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for item in bpy.data.objects:
            if item.type == "MESH":
                for slot in item.material_slots:
                    if hasattr(slot.material, "mmd_material") and slot.material.mmd_material.name_e != "":
                        print("[AWTool] Rename material " + slot.material.name + " to " + slot.material.mmd_material.name_e)
                        slot.material.name = slot.material.mmd_material.name_e
            if item.type == "ARMATURE":
                for bone in item.pose.bones:
                    if hasattr(bone, "mmd_bone") and bone.mmd_bone.name_e != "":
                        print("[AWTool] Rename bone " + bone.name + " to " + bone.mmd_bone.name_e)
                        bone.name = bone.mmd_bone.name_e
        return {'FINISHED'}

class AWTools_OptimizDisablesubdivandmultires(bpy.types.Operator):
    """Disables all subdivision and multires modifiers for viewport and render"""
    bl_idname = "awt.disable_subdiv_and_multires_on_selected"
    bl_label = "Disable Subdiv and multires on selected"
    bl_description = "Disables all subdivision and multires modifiers for viewport and render. Applies to active and selected"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            for mod in obj.modifiers:
                if mod.type in {'SUBSURF', 'MULTIRES'}:
                    mod.show_viewport = False
                    mod.show_render = False
        self.report({'INFO'}, "All Subdivision Surface and Multiresolution modifiers disabled in viewport and render for selected objects.")
        return {"FINISHED"}

class AWTools_TriangulateNgonsOnActive(bpy.types.Operator):
    """Adds a triangulate modifier that targets N-Gons"""
    bl_idname = "awt.triangulate_ngons_on_active"
    bl_label = "Triangulate N-Gons on active"
    bl_description = "Adds a triangulate modifier that targets N-Gons. Applies to active"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        triangulate_min = 5
        triangulate_min

        if bpy.context.active_object and bpy.context.active_object.type == 'MESH':
            obj = bpy.context.active_object
            triangulate_mod = obj.modifiers.new(name="Triangulate", type='TRIANGULATE')
            triangulate_mod.quad_method = 'FIXED'
            triangulate_mod.ngon_method = 'BEAUTY'
            triangulate_mod.min_vertices = triangulate_min
            self.report({'INFO'}, "Triangulate modifier added with specified settings.")
        else:
            self.report({'INFO'}, "No suitable active object found or the active object cannot have modifiers.")
        return {"FINISHED"}

class AWTools_TriangulateActiveMesh(bpy.types.Operator):
    """Adds a triangulate modifier that targets 4-Gons"""
    bl_idname = "awt.triangulate_active_mesh"
    bl_label = "Triangulate active mesh"
    bl_description = "Adds a triangulate modifier to entire mesh. Applies to active"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        triangulate_min = 4
        triangulate_min
        if bpy.context.active_object and bpy.context.active_object.type == 'MESH':
            obj = bpy.context.active_object
            triangulate_mod = obj.modifiers.new(name="Triangulate", type='TRIANGULATE')
            triangulate_mod.quad_method = 'FIXED'
            triangulate_mod.ngon_method = 'BEAUTY'
            triangulate_mod.min_vertices = triangulate_min
            self.report({'INFO'}, "Triangulate modifier added with specified settings.")
        else:
            self.report({'INFO'}, "No suitable active object found or the active object cannot have modifiers.")
        return {"FINISHED"}

class AWTools_ui(bpy.types.Panel):
    bl_label = "Awesomium tools"
    bl_idname = "OBJECT_AWT_panel"
    bl_category = "AWTool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_order = 0
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        try: 
            row.label(text= "Active Mode: " + context.active_object.mode)
        except:
            row.label(text= "Active Mode: N/A")

class AWUI_Statistics_panel(bpy.types.Panel):
    bl_label = "Statistic mesh"
    bl_idname = "StatisticMesh"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'OBJECT_AWT_panel'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        try:
            materialCount = len(context.active_object.material_slots) \
            if context.active_object.material_slots is not None else 0
            
            try:
                nlaCount = len(context.active_object.animation_data.nla_tracks) \
                if context.active_object.animation_data.nla_tracks is not None else 0
            except:
                nlaCount = 0

            try: shapeKeyCount = len(bpy.context.active_object.data.shape_keys.key_blocks) \
                if bpy.context.active_object.data.shape_keys.key_blocks is not None else 0            
            except: shapeKeyCount =0
                
            
            if context.active_object.type == 'MESH':
                row = layout.row()

                if len(context.selected_objects) ==1:
                    row.label(text=context.active_object.name + " details.", icon='INFO')
                    row = layout.row()

                    row.label(text="Vert's: " + str(len(context.active_object.data.vertices)), icon='NORMALS_VERTEX_FACE')
                    row.label(text="Mat's: " + str(materialCount), icon='MATERIAL')
                    row = layout.row()
                    row.label(text="Key's: " + str(shapeKeyCount), icon='SHAPEKEY_DATA')
                    row.label(text="NLA's: " + str(nlaCount), icon='NLA')
                    #row = layout.row()
                    #row.label(text="Edges: " + str(len(context.active_object.data.edges)), icon='MESH_EDGE')
                    #row.label(text="Faces: " + str(len(context.active_object.data.polygons)), icon='MESH_POLY')
                    #row.label(text="Triangles: " + str(sum(len(p.vertices) == 3 for p in context.active_object.data.polygons)), icon='MESH_GRID')

                if len(context.selected_objects) >1:
                    row.label(text="Multiple Objects", icon='INFO')
                    row = layout.row()
                    total_verts = sum(len(obj.data.vertices) for obj in context.selected_objects)
                    #total_edges = sum(len(obj.data.edges) for obj in context.selected_objects)
                    #total_faces = sum(len(obj.data.polygons) for obj in context.selected_objects)
                    #total_triangles = sum(len(p.vertices) == 3 for obj in context.selected_objects for p in obj.data.polygons)

                    row.label(text="Vert's: " + str(total_verts), icon='NORMALS_VERTEX_FACE')
                    ##row.label(text="Edges: " + str(total_edges), icon='MESH_EDGE')
                    #row.label(text="Mat's: " + str(len(bpy.data.materials) if bpy.data.materials is not None else 0), icon='MATERIAL')
                    #row.label(text="Key's: " + str(len(bpy.data.shape_keys.key_blocks) if bpy.data.shape_keys.key_blocks is not None else 0), icon='SHAPEKEY_DATA')
                    #row.label(text="NLA's: " + str(len(bpy.data.animation_data) if bpy.data.animation_data is not None else 0), icon='NLA')


        except:
            print('AWTool Error panel!') 

class AWUI_Cleaner_panel(bpy.types.Panel):
    bl_label = "Cleaner"
    bl_idname = "CleanerPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'OBJECT_AWT_panel'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        try:
            layout.label(text="Cleaner (Select mesh)",icon='BRUSH_DATA')

            #if context.mode == 'OBJECT':
            row = layout.row()
            row.operator("awt.cleandrivers", text="Clear all driver shape keys", icon="PANEL_CLOSE")
            row = layout.row()
            row.operator("awt.cleanlessblends", text="Clear empty shape keys", icon="FULLSCREEN_EXIT")
            row = layout.row()

            row.operator("awt.clearmaterials", text="Clear unused materials", icon="NODE_MATERIAL")
            row.operator("awt.cleartextures", text="Clear unused textures", icon="NODE_TEXTURE")
            
        except:
            print('AWTool Error panel!') 

class AWUI_Shapekeys_panel(bpy.types.Panel):
    bl_label = "Shapekeys"
    bl_idname = "ShapekeysPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'OBJECT_AWT_panel'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        renamescene = scene.Renamer

        try:
            #if context.mode == 'OBJECT':
            row = layout.row()
            row.operator("awt.lowercaseshapekeys", text="Lowercase shape keys", icon="SMALL_CAPS")

            row = layout.row()
            row.operator("awt.setallshapekeyvaluestozero", text="All shapekeys to 0", icon="RADIOBUT_OFF")

            layout.separator()
            layout.label(text="Transfer shapekey (Select [1]-Parent and [2]-Child )", icon='RESTRICT_SELECT_OFF')
            row = layout.row()
            row.operator("awt.transferblend", text="Transfer", icon="TRACKING_FORWARDS_SINGLE")
                
            layout.separator()
            layout.label(text="Renamer shapekeys", icon='SYNTAX_OFF')

            row = layout.row()
            row.prop(renamescene, "Key", icon='OUTLINER_OB_FONT')
                
            row = layout.row()
            row.prop(renamescene, "ReplaceName", icon='BOLD')

            row = layout.row()
            row.operator("awt.renameshapes", text="Rename blendshapes", icon="OUTLINER_DATA_GP_LAYER")
            
        except:
            print('AWTool Error panel!') 

class AWUI_Bones_panel(bpy.types.Panel):
    bl_label = "Bones tools"
    bl_idname = "BonestoolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'OBJECT_AWT_panel'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        renamebone = scene.Renamerbone
        transferweight = scene.Transferweightname

        try:
            layout.label(text="Renamer bones", icon='BONE_DATA')

            row = layout.row()
            row.prop(renamebone, "KeyBone", icon='OUTLINER_OB_FONT')
            
            row = layout.row()
            row.prop(renamebone, "ReplaceNameBone", icon='BOLD')

            row = layout.row()
            row.operator("awt.renamebones", text="Rename bones", icon="OUTLINER_DATA_GP_LAYER")

            row = layout.row()
            row.operator("awt.transferlimittoik", text="Transfer limit to IK", icon="POSE_HLT")

            #if context.mode == 'MESH':
            layout.separator()
            layout.label(text="Transfer weight old bones to new bone", icon="GROUP_BONE")
            row = layout.row()
            row.prop(transferweight, "KeyOldWeight", text="Old Weight", icon="COPYDOWN")
            row = layout.row()
            row.prop(transferweight, "AddActiveBoneWeight", text="Active Bone", icon='PASTEDOWN')
            row = layout.row()
            row.prop(transferweight, "DellOldWeight", text="Delete old weight")
            row = layout.row()
            row.operator("awt.transferweightbonestobone", text="Transfer weight one object", icon="GROUP_BONE")
            row = layout.row()
            row.operator("awt.transferweightbonestobonemassrig", text="Transfer weight all objects rig", icon="GROUP_BONE")
            #row = layout.row()
            #row.operator("awt.transferweightbonestobonemass", text="Transfer weight all objects", icon="GROUP_BONE")

            layout.separator()
            layout.label(text="Set Custom Bone Shape", icon='MESH_CUBE')

            # Object picker with eyedropper
            row = layout.row()
            row.prop(context.scene, "custom_object_to_bones", text="Shape")

            # Button to apply the custom shape to selected bones
            row = layout.row()
            row.operator("awt.set_custom_shape", text="Set to Selected Bones", icon="CON_ARMATURE")

            # DEBUG
            #key_value = renamescene.Key
            #replace_name_value = renamescene.ReplaceName
            #print("Key:", key_value)
            #print("Replace Name:", replace_name_value)

            layout.separator()
            layout.label(text="Dynamic parent", icon='OUTLINER_DATA_ARMATURE')
            row = layout.row()
            row.operator("awt.dynamic_parent_create", text="Create", icon="KEY_HLT")
            row.operator("awt.dynamic_parent_disable", text="Disable", icon="KEY_DEHLT")
            row = layout.row()
            row.menu("awt.dynamic_parent_clear_menu", text="Clear")

            layout.separator()
            layout.label(text="Rigs hand Select RigTO, and selecto rig copy", icon='OUTLINER_OB_ARMATURE')
            row = layout.row()
            row.operator("awt.copylocationhand", text="Copy def mode", icon="GROUP_BONE")
            row.operator("awt.copylocationhandarp", text="Copy ARP mode", icon="GROUP_BONE")
            
        except:
            print('AWTool Error panel!') 

class AWUI_Lashesgen_panel(bpy.types.Panel):
    bl_label = "Lashes generator"
    bl_idname = "LashesgenPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'OBJECT_AWT_panel'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        try:
            layout.label(text="Lashes generator", icon='CURVES')

            row = layout.row()
            row.prop(scene, "RotateRangeStartX")
            row.prop(scene, "RotateRangeEndX")
            row = layout.row()
            row.prop(scene, "RotateRangeStartY")
            row.prop(scene, "RotateRangeEndY")
            row = layout.row()
            row.prop(scene, "RotateRangeStartZ")
            row.prop(scene, "RotateRangeEndZ")
            
            layout.label(text="Random Scale", icon='SURFACE_NCYLINDER')
            row = layout.row()
            row.prop(scene, "ScaleRangeStart")
            row.prop(scene, "ScaleEnd")
            layout.label(text="Random Position Interval", icon='FCURVE')
            row = layout.row()
            row.prop(scene, "PosRangeStart")
            row.prop(scene, "PosRangeEnd")
            
            layout.label(text="Rate", icon='PREV_KEYFRAME')
            row = layout.row()
            row.prop(scene, "RateRangeGen")
            layout.label(text="Maximum Frames",icon='NEXT_KEYFRAME')
            row = layout.row()
            row.prop(scene, "MaximumFrames")

            row = layout.row()
            row.operator("awt.eyelashesgen", text="Generate eye lashes (BezierCurve and mesh)", icon="SEQ_HISTOGRAM")

        except:
            print('AWTool Error panel!') 

class AWUI_Optimizationrep_panel(bpy.types.Panel):
    bl_label = "Optimization and repotology"
    bl_idname = "OptimizationrepPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'OBJECT_AWT_panel'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        try:
            if context.mode == 'EDIT_MESH':
                layout.label(text="Select and merge", icon='MOD_MULTIRES')
                row = layout.row()
                row.operator("awt.selectring_merge", text="Select ring and merge(UV Space need weld)", icon="UV_EDGESEL")
                #row.operator("awt.selectring_dissolve", text="Select ring and dissolve(Beta)", icon="UV_FACESEL")

        except:
            print('AWTool Error panel!') 

class AWUI_Optimizationrender_panel(bpy.types.Panel):
    bl_label = "Optimization render"
    bl_idname = "OptimizationrenderPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'OBJECT_AWT_panel'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        try:
            row = layout.row()
            row.operator("awt.disable_subdiv_and_multires_on_selected", text="Disable Subdiv and multires", icon="MOD_EXPLODE")
            row = layout.row()
            row.operator("awt.triangulate_ngons_on_active", text="Triangulate N-Gons", icon="MOD_TRIANGULATE")
            row.operator("awt.triangulate_active_mesh", text="Triangulate mesh", icon="MOD_TRIANGULATE")

            row = layout.row()
            row.prop(bpy.context.scene.render, 'use_simplify', text='Simplify', icon="META_PLANE")
            row.prop(bpy.context.scene.render, 'simplify_subdivision', text='')

        except:
            print('AWTool Error panel!') 

class AWUI_Other_panel(bpy.types.Panel):
    bl_label = "Other tools"
    bl_idname = "OtherPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'OBJECT_AWT_panel'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        try:
            row = layout.row()
            row.operator("awt.renamemmdtoeng", text="Rename bones/mats MMD JP to English", icon="FONTPREVIEW")

        except:
            print('AWTool Error panel!') 

classes = (
    AWTools_LowercaseShapeKeys,
    AWTools_SetAllShapeKeysValuesToZero,
    AWTools_CleanDrivers,
    AWTools_CleanEmptyBlendshapes,
    AWTools_TransferBlendshapes,
    AWTools_CleanMaterials,
    AWTools_CleanTextures,
    AWTools_Renamer,
    AWTools_RenameBlendshapes,
    AWTools_Renamerbone,
    AWTools_RenameBones,
    AWTools_TransferLimitIK,
    AWTools_EyelashesGenerator,
    AWTools_DYNAMIC_PARENT_create,
    AWTools_DYNAMIC_PARENT_disable,
    AWTools_DYNAMIC_PARENT_clear,
    AWTools_DYNAMIC_PARENT_bake,
    AWTools_DYNAMIC_PARENT_clear_menu,
    AWTools_Transferweightname,
    AWTools_TransferWeightbonestobone,
    AWTools_TransferWeightbonestobonemass,
    AWTools_TransferWeightbonestobonemassrig,
    AWTools_SetCustomShape,
    AWTools_CopyLocationHanddef,
    AWTools_CopyLocationHandarp,
    AWTools_SelectRingAndMerge,
    AWTools_SelectRingAndDissolve,
    AWTools_RenameEngMMD,
    AWTools_OptimizDisablesubdivandmultires,
    AWTools_TriangulateNgonsOnActive,
    AWTools_TriangulateActiveMesh,
    AWTools_ui,
    AWUI_Statistics_panel,
    AWUI_Cleaner_panel,
    AWUI_Shapekeys_panel,
    AWUI_Bones_panel,
    AWUI_Lashesgen_panel,
    AWUI_Optimizationrep_panel,
    AWUI_Optimizationrender_panel,
    AWUI_Other_panel,
)

#register, unregister = bpy.utils.register_classes_factory(classes)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.Renamer = bpy.props.PointerProperty(type=AWTools_Renamer)
    bpy.types.Scene.Renamerbone = bpy.props.PointerProperty(type=AWTools_Renamerbone)
    bpy.types.Scene.Transferweightname = bpy.props.PointerProperty(type=AWTools_Transferweightname)
    bpy.types.Scene.custom_object_to_bones = bpy.props.PointerProperty(
        name="Custom Shape Object",
        type=bpy.types.Object
    )

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.Renamer
    del bpy.types.Scene.Renamerbone
    del bpy.types.Scene.Transferweightname

if __name__ == "__main__":
    register()
