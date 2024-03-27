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
    "description": "Easy working for blendshapes and other.",
    "tracker_url": "https://mrkubu.github.io/",  
    "category": "Utility",
    "version": (2, 0, 0),
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
        return {'FINISHED'}

class AWTools_CleanDrivers(bpy.types.Operator):
    """Clear driver from shapekeys"""
    bl_idname = "awt.cleandrivers"
    bl_label = "Clear drivers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        assert context.mode == 'OBJECT', "Must be in object mode!"
        
        for ob in context.selected_objects:
            if ob.data.shape_keys:
                for b in ob.data.shape_keys.key_blocks:
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

class AWTools_CleanMaterials(bpy.types.Operator):
    """Clear unused materials"""
    bl_idname = "awt.clearmaterials"
    bl_label = "Clear unused materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for material in bpy.data.materials:
            if not material.users:
                bpy.data.materials.remove(material)
                
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
                # Get all data limit for IK
                pose_bone.use_ik_limit_x = limit_rot.use_limit_x
                pose_bone.use_ik_limit_y = limit_rot.use_limit_y
                pose_bone.use_ik_limit_z = limit_rot.use_limit_z

                # Set limit IK in Limit Rotation
                pose_bone.ik_min_x = limit_rot.min_x if limit_rot.use_limit_x else 0.0
                pose_bone.ik_max_x = limit_rot.max_x if limit_rot.use_limit_x else 0.0
                pose_bone.ik_min_y = limit_rot.min_y if limit_rot.use_limit_y else 0.0
                pose_bone.ik_max_y = limit_rot.max_y if limit_rot.use_limit_y else 0.0
                pose_bone.ik_min_z = limit_rot.min_z if limit_rot.use_limit_z else 0.0
                pose_bone.ik_max_z = limit_rot.max_z if limit_rot.use_limit_z else 0.0
                
                print("Limit Rotation data has been copied to IK settings for the bone.")
            else:
                print("The Limit Rotation constraint was not found on the selected bone.")
        else:
            print("Please select an armature and a pose bone.")
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

        assert obj.type == 'MESH', "Must be in object mode!"

        for obj in bpy.context.selected_objects:
            if obj.type != 'MESH': continue

            # Проверяем, существуют ли группы вершин
            if getOldWeight in obj.vertex_groups and weightAdd in obj.vertex_groups:
                # Получаем индекс новой группы вершин
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

            # Update view layer
            bpy.context.view_layer.update()
        
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
        row = layout.row()
        row.operator("awt.clearmaterials", text="Clear unused materials", icon="NODE_MATERIAL")
        row.operator("awt.cleartextures", text="Clear unused textures", icon="NODE_TEXTURE")



        row = layout.row()
        row.operator("awt.lowercaseshapekeys", text="Lowercase shape keys", icon="SMALL_CAPS")



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
        row.operator("awt.renameshapes", text="Rename blendshapes", icon="OUTLINER_DATA_GP_LAYER")

        renamebone = scene.Renamerbone
        layout.separator()
        layout.label(text="Renamer bones")

        row = layout.row()
        row.prop(renamebone, "KeyBone")
        
        row = layout.row()
        row.prop(renamebone, "ReplaceNameBone")

        row = layout.row()
        row.operator("awt.renamebones", text="Rename bones", icon="OUTLINER_DATA_GP_LAYER")

        row = layout.row()
        row.operator("awt.transferlimittoik", text="Transfer limit to IK", icon="POSE_HLT")

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

        layout.separator()
        layout.label(text="Dynamic parent")
        row = layout.row()
        row.operator("awt.dynamic_parent_create", text="Create", icon="KEY_HLT")
        row.operator("awt.dynamic_parent_disable", text="Disable", icon="KEY_DEHLT")
        row = layout.row()
        row.menu("awt.dynamic_parent_clear_menu", text="Clear")


        transferweight = scene.Transferweightname
        layout.separator()
        layout.label(text="Transfer weight old bones to new bone")
        row = layout.row()
        row.prop(transferweight, "KeyOldWeight", text="Old Weight")
        row = layout.row()
        row.prop(transferweight, "AddActiveBoneWeight", text="Active Bone")
        row = layout.row()
        row.prop(transferweight, "DellOldWeight", text="Delete old weight")
        row = layout.row()
        row.operator("awt.transferweightbonestobone", text="Transfer weight", icon="GROUP_BONE")
        

classes = (
    AWTools_LowercaseShapeKeys,
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
    AWTools_ui,
)

#register, unregister = bpy.utils.register_classes_factory(classes)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.Renamer = bpy.props.PointerProperty(type=AWTools_Renamer)
    bpy.types.Scene.Renamerbone = bpy.props.PointerProperty(type=AWTools_Renamerbone)
    bpy.types.Scene.Transferweightname = bpy.props.PointerProperty(type=AWTools_Transferweightname)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.Renamer
    del bpy.types.Scene.Renamerbone
    del bpy.types.Scene.Transferweightname

if __name__ == "__main__":
    register()
