bl_info = {
    "name": "Pokémon Switch V2 (.TRMDL)",
    "author": "Scarlett/SomeKitten & ElChicoEevee",
    "version": (0, 0, 2),
    "blender": (3, 3, 0),
    "location": "File > Import",
    "description": "Blender addon for import Pokémon Switch TRMDL",
    "warning": "",
    "category": "Import",
}

import os
from os import path
import os.path
import random
import struct
from pathlib import Path
from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )
from bpy_extras.io_utils import ImportHelper
from bpy.types import (
        Operator,
        OperatorFileListElement,
        )
import bpy
import mathutils
import math
import glob
import shutil
import sys


# READ THIS: change to True when running in Blender, False when running using fake-bpy-module-latest
IN_BLENDER_ENV = True

class PokeSVImport(bpy.types.Operator, ImportHelper):
    bl_idname = "custom_import_scene.pokemonscarletviolet"
    bl_label = "Import"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".trmdl"
    filter_glob: StringProperty(
            default="*.trmdl",
            options={'HIDDEN'},
            maxlen=255,
    )
    filepath = bpy.props.StringProperty(subtype='FILE_PATH',)
    files = CollectionProperty(type=bpy.types.PropertyGroup)
    rare: BoolProperty(
            name="Load Shiny",
            description="Uses rare material instead of normal one",
            default=False,
            )
    multiple: BoolProperty(
            name="Load All Folder",
            description="Uses rare material instead of normal one",
            default=False,
            )
    loadlods: BoolProperty(
            name="Load LODS",
            description="Uses rare material instead of normal one",
            default=False,
            )
    bonestructh: BoolProperty(
            name="Bone Extras (WIP)",
            description="Bone Extras (WIP)",
            default=False,
            )
    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop(self, 'rare')
        
        box = layout.box()
        box.prop(self, 'multiple')
        
        box = layout.box()
        box.prop(self, 'loadlods')

        box = layout.box()
        box.prop(self, 'bonestructh')
        
        
    def execute(self, context):
        directory = os.path.dirname(self.filepath)
        if self.multiple == False:
            filename = os.path.basename(self.filepath)        
            f = open(os.path.join(directory, filename), "rb")
            from_trmdlsv(directory, f, self.rare, self.loadlods, self.bonestructh)
            f.close()
            return {'FINISHED'}  
        else:
            file_list = sorted(os.listdir(directory))
            obj_list = [item for item in file_list if item.endswith('.trmdl')]
            for item in obj_list:
                f = open(os.path.join(directory, item), "rb")
                from_trmdlsv(directory, f, self.rare, self.loadlods, self.bonestructh)
                f.close()
            return {'FINISHED'}

def from_trmdlsv(filep, trmdl, rare, loadlods, bonestructh):
    # make collection
    if IN_BLENDER_ENV:
        new_collection = bpy.data.collections.new(os.path.basename(trmdl.name[:-6]))
        bpy.context.scene.collection.children.link(new_collection)


    textureextension = ".png"


    materials = []
    bone_structure = None
    trskl = None
    trmsh = None
    trmtr = None
    
    trmsh_lods_array = []
    bone_array = []
    bone_id_map = {}
    bone_rig_array = []
    trskl_bone_adjust = 0
    CharaCheck = "None"

    print("Parsing TRMDL...")

    trmdl_file_start = readlong(trmdl); fseek(trmdl, trmdl_file_start)
    trmdl_struct = ftell(trmdl) - readlong(trmdl); fseek(trmdl, trmdl_struct)
    trmdl_struct_len = readshort(trmdl)


    if trmdl_struct_len == 0x0012:
        trmdl_struct_section_len = readshort(trmdl)
        trmdl_struct_start = readshort(trmdl)
        trmdl_struct_trmsh = readshort(trmdl)
        trmdl_struct_trskl = readshort(trmdl)
        trmdl_struct_trmtr = readshort(trmdl)
        trmdl_struct_custom = readshort(trmdl)
        trmdl_struct_bound_box = readshort(trmdl)
        trmdl_struct_float = readshort(trmdl)
    elif trmdl_struct_len == 0x0014: #ScarletViolet Only
        trmdl_struct_section_len = readshort(trmdl)
        trmdl_struct_start = readshort(trmdl)
        trmdl_struct_trmsh = readshort(trmdl)
        trmdl_struct_trskl = readshort(trmdl)
        trmdl_struct_trmtr = readshort(trmdl)
        trmdl_struct_custom = readshort(trmdl)
        trmdl_struct_bound_box = readshort(trmdl)
        trmdl_struct_float = readshort(trmdl)
        trmdl_struct_trltt = readshort(trmdl)
    elif trmdl_struct_len == 0x0018: #ScarletViolet Only
        trmdl_struct_section_len = readshort(trmdl)
        trmdl_struct_start = readshort(trmdl)
        trmdl_struct_trmsh = readshort(trmdl)
        trmdl_struct_trskl = readshort(trmdl)
        trmdl_struct_trmtr = readshort(trmdl)
        trmdl_struct_custom = readshort(trmdl)
        trmdl_struct_bound_box = readshort(trmdl)
        trmdl_struct_float = readshort(trmdl)
        trmdl_struct_trltt = readshort(trmdl)
        trmdl_struct_unka = readshort(trmdl)
        trmdl_struct_unkb = readshort(trmdl)
    else:
        raise AssertionError("Unexpected TRMDL header struct length!")

    if trmdl_struct_trmsh != 0:
        fseek(trmdl, trmdl_file_start + trmdl_struct_trmsh)
        trmsh_start = ftell(trmdl) + readlong(trmdl); fseek(trmdl, trmsh_start)
        trmsh_count = readlong(trmdl)
        for x in range(trmsh_count):
            trmsh_offset = ftell(trmdl) + readlong(trmdl)
            trmsh_ret = ftell(trmdl)
            fseek(trmdl, trmsh_offset)
            trmsh_struct = ftell(trmdl) - readlong(trmdl); fseek(trmdl, trmsh_struct)
            trmsh_struct_len = readshort(trmdl)

            if trmsh_struct_len != 0x0006:
                raise AssertionError("Unexpected TRMSH struct length!")

            trmsh_struct_section_len = readshort(trmdl)
            trmsh_struct_ptr_name = readshort(trmdl)

            if trmsh_struct_ptr_name != 0:
                fseek(trmdl, trmsh_offset + trmsh_struct_ptr_name)
                trmsh_name_offset = ftell(trmdl) + readlong(trmdl)
                fseek(trmdl, trmsh_name_offset)
                trmsh_name_len = readlong(trmdl)
                chara_check = readfixedstring(trmdl, 3); fseek(trmdl, ftell(trmdl) - 3)

                if chara_check.startswith(('au_')): chara_check = "CommonNPC"
                elif chara_check.startswith(('bu_')): chara_check = "CommonNPC"
                elif chara_check.startswith(('cf_')): chara_check = "CommonNPC"
                elif chara_check.startswith(('cm_')): chara_check = "CommonNPC"
                elif chara_check.startswith(('df_')): chara_check = "CommonNPC"
                elif chara_check.startswith(('dm_')): chara_check = "CommonNPC"
                elif chara_check.startswith(('p1_')): chara_check = "Rei"
                elif chara_check.startswith(('p2_')): chara_check = "Akari"
                elif chara_check.startswith(('pm')): chara_check = "Pokemon"
                else: chara_check = "None"

                trmsh_name = readfixedstring(trmdl, trmsh_name_len)
                print(trmsh_name)
                print(chara_check)
                trmsh_lods_array.append(trmsh_name)
            fseek(trmdl, trmsh_ret)

    if trmdl_struct_trskl != 0:
        fseek(trmdl, trmdl_file_start + trmdl_struct_trskl)
        trskl_start = ftell(trmdl) + readlong(trmdl); fseek(trmdl, trskl_start)
        trskl_struct = ftell(trmdl) - readlong(trmdl); fseek(trmdl, trskl_struct)
        trskl_struct_len = readshort(trmdl)

        if trskl_struct_len != 0x0006:
            raise AssertionError("Unexpected TRSKL struct length!")

        trskl_struct_section_len = readshort(trmdl)
        trskl_struct_ptr_name = readshort(trmdl)

        if trskl_struct_ptr_name != 0:
            fseek(trmdl, trskl_start + trskl_struct_ptr_name)
            trskl_name_offset = ftell(trmdl) + readlong(trmdl)
            fseek(trmdl, trskl_name_offset)
            trskl_name_len = readlong(trmdl)
            trskl_name = readfixedstring(trmdl, trskl_name_len)
            print(trskl_name)

            if os.path.exists(os.path.join(filep, trskl_name)):
                trskl = open(os.path.join(filep, trskl_name), "rb")
            else:
                print(f"Can't find {trskl_name}!")

    if trmdl_struct_trmtr != 0:
        fseek(trmdl, trmdl_file_start + trmdl_struct_trmtr)
        trmtr_start = ftell(trmdl) + readlong(trmdl); fseek(trmdl, trmtr_start)
        trmtr_count = readlong(trmdl)
        for x in range(trmtr_count):
            trmtr_offset = ftell(trmdl) + readlong(trmdl)
            trmtr_ret = ftell(trmdl)
            fseek(trmdl, trmtr_offset)
            trmtr_name_len = readlong(trmdl)  #  - 6 -- dunno why the extension was excluded
            trmtr_name = readfixedstring(trmdl, trmtr_name_len)
            # TODO ArceusShiny
            # LINE 1227
            print(trmtr_name)
            if x == 0:
                if rare == True:
                    trmtr = open(os.path.join(filep, Path(trmtr_name).stem + "_rare.trmtr"), "rb")
                else:
                    trmtr = open(os.path.join(filep, trmtr_name), "rb") 
            fseek(trmdl, trmtr_ret)
    fclose(trmdl)

    # TODO create bone_rig_array
    # LINE 1247
    
    
    if trskl is not None:
        print("Parsing TRSKL...")
        trskl_file_start = readlong(trskl)
        fseek(trskl, trskl_file_start)
        trskl_struct = ftell(trskl) - readlong(trskl); fseek(trskl, trskl_struct)
        trskl_struct_len = readshort(trskl)
        if trskl_struct_len == 0x000C:
            trskl_struct_section_len = readshort(trskl)
            trskl_struct_start = readshort(trskl)
            trskl_struct_bone = readshort(trskl)
            trskl_struct_b = readshort(trskl)
            trskl_struct_c = readshort(trskl)
            trskl_struct_bone_adjust = 0
        elif trskl_struct_len == 0x000E:
            trskl_struct_section_len = readshort(trskl)
            trskl_struct_start = readshort(trskl)
            trskl_struct_bone = readshort(trskl)
            trskl_struct_b = readshort(trskl)
            trskl_struct_c = readshort(trskl)
            trskl_struct_bone_adjust = readshort(trskl)
        else:
            raise AssertionError("Unexpected TRSKL header struct length!")

        if trskl_struct_bone_adjust != 0:
            fseek(trskl, trskl_file_start + trskl_struct_bone_adjust)
            trskl_bone_adjust = readlong(trskl); print(f"Mesh node IDs start at {trskl_bone_adjust}")

        if trskl_struct_bone != 0:
            fseek(trskl, trskl_file_start + trskl_struct_bone)
            trskl_bone_start = ftell(trskl) + readlong(trskl); fseek(trskl, trskl_bone_start)
            bone_count = readlong(trskl)

            if IN_BLENDER_ENV:
                new_armature = bpy.data.armatures.new(os.path.basename(trmdl.name))
                bone_structure = bpy.data.objects.new(os.path.basename(trmdl.name), new_armature)
                new_collection.objects.link(bone_structure)
                bpy.context.view_layer.objects.active = bone_structure
                bpy.ops.object.editmode_toggle()
            
            for x in range(bone_count):
                bone_offset = ftell(trskl) + readlong(trskl)
                bone_ret = ftell(trskl)
                fseek(trskl, bone_offset)
                print(f"Bone {x} start: {hex(bone_offset)}")
                trskl_bone_struct = ftell(trskl) - readlong(trskl); fseek(trskl, trskl_bone_struct)
                trskl_bone_struct_len = readshort(trskl)

                if trskl_bone_struct_len == 0x0012:
                    trskl_bone_struct_ptr_section_len = readshort(trskl)
                    trskl_bone_struct_ptr_string = readshort(trskl)
                    trskl_bone_struct_ptr_bone = readshort(trskl)
                    trskl_bone_struct_ptr_c = readshort(trskl)
                    trskl_bone_struct_ptr_d = readshort(trskl)
                    trskl_bone_struct_ptr_parent = readshort(trskl)
                    trskl_bone_struct_ptr_rig_id = readshort(trskl)
                    trskl_bone_struct_ptr_bone_merge = readshort(trskl)
                    trskl_bone_struct_ptr_h = 0
                elif trskl_bone_struct_len == 0x0014:
                    trskl_bone_struct_ptr_section_len = readshort(trskl)
                    trskl_bone_struct_ptr_string = readshort(trskl)
                    trskl_bone_struct_ptr_bone = readshort(trskl)
                    trskl_bone_struct_ptr_c = readshort(trskl)
                    trskl_bone_struct_ptr_d = readshort(trskl)
                    trskl_bone_struct_ptr_parent = readshort(trskl)
                    trskl_bone_struct_ptr_rig_id = readshort(trskl)
                    trskl_bone_struct_ptr_bone_merge = readshort(trskl)
                    trskl_bone_struct_ptr_h = readshort(trskl)
                else:
                    trskl_bone_struct_ptr_section_len = readshort(trskl)
                    trskl_bone_struct_ptr_string = readshort(trskl)
                    trskl_bone_struct_ptr_bone = readshort(trskl)
                    trskl_bone_struct_ptr_c = readshort(trskl)
                    trskl_bone_struct_ptr_d = readshort(trskl)
                    trskl_bone_struct_ptr_parent = readshort(trskl)
                    trskl_bone_struct_ptr_rig_id = readshort(trskl)
                    trskl_bone_struct_ptr_bone_merge = readshort(trskl)
                    trskl_bone_struct_ptr_h = readshort(trskl)



                if trskl_bone_struct_ptr_bone_merge != 0:
                    fseek(trskl, bone_offset + trskl_bone_struct_ptr_bone_merge)
                    bone_merge_start = ftell(trskl) + readlong(trskl); fseek(trskl, bone_merge_start)
                    bone_merge_string_len = readlong(trskl)
                    if bone_merge_string_len != 0:
                        bone_merge_string = readfixedstring(trskl, bone_merge_string_len)
                        print(f"BoneMerge to {bone_merge_string}")
                    else: bone_merge_string = ""

                if chara_check == "Rei" or chara_check == "Akari":
                    bone_array.append("foot_base")
                    bone_array.append("waist")
                    bone_array.append("spine_01")
                    bone_array.append("spine_02")
                    bone_array.append("spine_03")
                    bone_array.append("neck")
                    bone_array.append("look")
                    bone_array.append("head")
                    bone_array.append("left_shoulder")
                    bone_array.append("left_arm_width")
                    bone_array.append("left_arm_01")
                    bone_array.append("left_arm_02")
                    bone_array.append("left_hand")
                    bone_array.append("left_thumb_01")
                    bone_array.append("left_thumb_02")
                    bone_array.append("left_thumb_03")
                    bone_array.append("left_index_01")
                    bone_array.append("left_index_02")
                    bone_array.append("left_index_03")
                    bone_array.append("left_middle_01")
                    bone_array.append("left_middle_02")
                    bone_array.append("left_middle_03")
                    bone_array.append("left_ring_01")
                    bone_array.append("left_ring_02")
                    bone_array.append("left_ring_03")
                    bone_array.append("left_pinky_01")
                    bone_array.append("left_pinky_02")
                    bone_array.append("left_pinky_03")
                    bone_array.append("left_attach_off")
                    bone_array.append("left_attach_on")
                    bone_array.append("left_hand_roll")
                    bone_array.append("left_arm_02_sub")
                    bone_array.append("left_arm_02_roll")
                    bone_array.append("left_arm_01_roll")
                    bone_array.append("right_shoulder")
                    bone_array.append("right_arm_width")
                    bone_array.append("right_arm_01")
                    bone_array.append("right_arm_02")
                    bone_array.append("right_hand")
                    bone_array.append("right_thumb_01")
                    bone_array.append("right_thumb_02")
                    bone_array.append("right_thumb_03")
                    bone_array.append("right_index_01")
                    bone_array.append("right_index_02")
                    bone_array.append("right_index_03")
                    bone_array.append("right_middle_01")
                    bone_array.append("right_middle_02")
                    bone_array.append("right_middle_03")
                    bone_array.append("right_ring_01")
                    bone_array.append("right_ring_02")
                    bone_array.append("right_ring_03")
                    bone_array.append("right_pinky_01")
                    bone_array.append("right_pinky_02")
                    bone_array.append("right_pinky_03")
                    bone_array.append("right_attach_off")
                    bone_array.append("right_attach_on")
                    bone_array.append("right_hand_roll")
                    bone_array.append("right_arm_02_sub")
                    bone_array.append("right_arm_02_roll")
                    bone_array.append("right_arm_01_roll")
                    bone_array.append("hips")
                    bone_array.append("leg_width")
                    bone_array.append("left_leg_01")
                    bone_array.append("left_leg_02")
                    bone_array.append("left_foot")
                    bone_array.append("left_toe")
                    bone_array.append("left_leg_02_sub")
                    bone_array.append("right_leg_01")
                    bone_array.append("right_leg_02")
                    bone_array.append("right_foot")
                    bone_array.append("right_toe")
                    bone_array.append("right_leg_02_sub")

                if trskl_bone_struct_ptr_bone != 0:
                    fseek(trskl, bone_offset + trskl_bone_struct_ptr_bone)
                    bone_pos_start = ftell(trskl) + readlong(trskl); fseek(trskl, bone_pos_start)
                    bone_pos_struct = ftell(trskl) - readlong(trskl); fseek(trskl, bone_pos_struct)
                    bone_pos_struct_len = readshort(trskl)

                    if bone_pos_struct_len != 0x000A:
                        raise AssertionError("Unexpected bone position struct length!")

                    bone_pos_struct_section_len = readshort(trskl)
                    bone_pos_struct_ptr_scl = readshort(trskl)
                    bone_pos_struct_ptr_rot = readshort(trskl)
                    bone_pos_struct_ptr_trs = readshort(trskl)

                    fseek(trskl, bone_pos_start + bone_pos_struct_ptr_trs)
                    bone_tx = readfloat(trskl); bone_ty = readfloat(trskl); bone_tz = readfloat(trskl)
                    # TODO ArceusScale
                    # LINE 1797
                    fseek(trskl, bone_pos_start + bone_pos_struct_ptr_rot)
                    bone_rx = readfloat(trskl); bone_ry = readfloat(trskl); bone_rz = readfloat(trskl)
                    fseek(trskl, bone_pos_start + bone_pos_struct_ptr_scl)
                    bone_sx = readfloat(trskl); bone_sy = readfloat(trskl); bone_sz = readfloat(trskl)

                    if trskl_bone_struct_ptr_string != 0:
                        fseek(trskl, bone_offset + trskl_bone_struct_ptr_string)
                        bone_string_start = ftell(trskl) + readlong(trskl); fseek(trskl, bone_string_start)
                        bone_str_len = readlong(trskl); bone_name = readfixedstring(trskl, bone_str_len)
                    if trskl_bone_struct_ptr_parent != 0x00:
                        fseek(trskl, bone_offset + trskl_bone_struct_ptr_parent)
                        bone_parent = readlong(trskl) + 1
                    else:
                        bone_parent = 0
                    print(bone_parent)
                    if trskl_bone_struct_ptr_rig_id != 0:
                        fseek(trskl, bone_offset + trskl_bone_struct_ptr_rig_id)
                        bone_rig_id = readlong(trskl) + trskl_bone_adjust

                        while len(bone_rig_array) <= bone_rig_id:
                            bone_rig_array.append("")
                        bone_rig_array[bone_rig_id] = bone_name

                    bone_matrix = mathutils.Matrix.LocRotScale(
                        (bone_tx, bone_ty, bone_tz),
                        mathutils.Euler((bone_rx, bone_ry, bone_rz)),
                        (bone_sx, bone_sy, bone_sz))

                    if IN_BLENDER_ENV:
                        new_bone = new_armature.edit_bones.new(bone_name)

                        new_bone.use_connect = False
                        new_bone.use_inherit_rotation = True
                        new_bone.use_inherit_scale = True
                        
                        if bonestructh == True:
                            if trskl_bone_struct_ptr_h == 0:
                                new_bone.use_inherit_scale = True
                            else:
                                new_bone.use_inherit_scale = False
                        
                        new_bone.use_local_location = True

                        new_bone.head = (0, 0, 0)
                        new_bone.tail = (0, 0, 0.1)
                        new_bone.matrix = bone_matrix

                        if bone_parent != 0:
                            new_bone.parent = bone_array[bone_parent - 1]
                            new_bone.matrix = bone_array[bone_parent - 1].matrix @ bone_matrix

                        if bone_name in bone_rig_array:
                            bone_id_map[bone_rig_array.index(bone_name)] = bone_name
                        else:
                            bone_rig_array.append(bone_name)
                            bone_id_map[len(bone_rig_array) - 1] = bone_name
                        
                        bone_array.append(new_bone)
                fseek(trskl, bone_ret)
        fclose(trskl)
        if IN_BLENDER_ENV:
            bpy.ops.object.editmode_toggle()
    
    if trmtr is not None:
        print("Parsing TRMTR...")
        trmtr_file_start = readlong(trmtr)
        mat_data_array = []
        fseek(trmtr, trmtr_file_start)
        trmtr_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, trmtr_struct)
        trmtr_struct_len = readshort(trmtr)

        if trmtr_struct_len != 0x0008:
            raise AssertionError("Unexpected TRMTR header struct length!")
        trmtr_struct_section_len = readshort(trmtr)
        trmtr_struct_start = readshort(trmtr)
        trmtr_struct_material = readshort(trmtr)

        if trmtr_struct_material != 0:
            fseek(trmtr, trmtr_file_start + trmtr_struct_material)
            mat_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_start)
            mat_count = readlong(trmtr)
            for x in range(mat_count):
                mat_shader = "Standard"; mat_col0 = ""; mat_lym0 = ""; mat_nrm0 = ""; mat_ao0 = ""; mat_emi0 = ""; mat_rgh0 = ""; mat_mtl0 = ""; mat_msk0 = ""; mat_highmsk0 = ""
                mat_uv_scale_u = 1.0; mat_uv_scale_v = 1.0; mat_uv_trs_u = 0; mat_uv_trs_v = 0
                mat_uv_scale2_u = 1.0; mat_uv_scale2_v = 1.0; mat_uv_trs2_u = 0; mat_uv_trs2_v = 0
                mat_color_r = 1.0; mat_color_g = 1.0; mat_color_b = 1.0
                mat_color1_r = 1.0; mat_color1_g = 1.0; mat_color1_b = 1.0
                mat_color2_r = 1.0; mat_color2_g = 1.0; mat_color2_b = 1.0
                mat_color3_r = 1.0; mat_color3_g = 1.0; mat_color3_b = 1.0
                mat_color4_r = 1.0; mat_color4_g = 1.0; mat_color4_b = 1.0

                mat_emcolor1_r = 1.0; mat_emcolor1_g = 1.0; mat_emcolor1_b = 1.0
                mat_emcolor2_r = 1.0; mat_emcolor2_g = 1.0; mat_emcolor2_b = 1.0
                mat_emcolor3_r = 1.0; mat_emcolor3_g = 1.0; mat_emcolor3_b = 1.0
                mat_emcolor4_r = 1.0; mat_emcolor4_g = 1.0; mat_emcolor4_b = 1.0
                mat_emcolor5_r = 1.0; mat_emcolor5_g = 1.0; mat_emcolor5_b = 1.0                
                mat_rgh_layer0 = 1.0; mat_rgh_layer1 = 1.0; mat_rgh_layer2 = 1.0; mat_rgh_layer3 = 1.0; mat_rgh_layer4 = 1.0
                mat_mtl_layer0 = 0.0; mat_mtl_layer1 = 0.0; mat_mtl_layer2 = 0.0; mat_mtl_layer3 = 0.0; mat_mtl_layer4 = 0.0
                mat_reflectance = 0.0
                mat_emm_intensity = 1.0
                mat_offset = ftell(trmtr) + readlong(trmtr)
                mat_ret = ftell(trmtr)

                mat_enable_base_color_map = False
                mat_enable_normal_map = False
                mat_enable_ao_map = False
                mat_enable_emission_color_map = False
                mat_enable_roughness_map = False
                mat_enable_metallic_map = False
                mat_enable_displacement_map = False
                mat_enable_highlight_map = False

                fseek(trmtr, mat_offset)
                print("--------------------")
                mat_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_struct)
                mat_struct_len = readshort(trmtr)

                if mat_struct_len != 0x0024:
                    raise AssertionError("Unexpected material struct length!")
                mat_struct_section_len = readshort(trmtr)
                mat_struct_ptr_param_a = readshort(trmtr)
                mat_struct_ptr_param_b = readshort(trmtr)
                mat_struct_ptr_param_c = readshort(trmtr)
                mat_struct_ptr_param_d = readshort(trmtr)
                mat_struct_ptr_param_e = readshort(trmtr)
                mat_struct_ptr_param_f = readshort(trmtr)
                mat_struct_ptr_param_g = readshort(trmtr)
                mat_struct_ptr_param_h = readshort(trmtr)
                mat_struct_ptr_param_i = readshort(trmtr)
                mat_struct_ptr_param_j = readshort(trmtr)
                mat_struct_ptr_param_k = readshort(trmtr)
                mat_struct_ptr_param_l = readshort(trmtr)
                mat_struct_ptr_param_m = readshort(trmtr)
                mat_struct_ptr_param_n = readshort(trmtr)
                mat_struct_ptr_param_o = readshort(trmtr)
                mat_struct_ptr_param_p = readshort(trmtr)

                if mat_struct_ptr_param_a != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_a)
                    mat_param_a_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_a_start)
                    mat_name_len = readlong(trmtr)
                    mat_name = readfixedstring(trmtr, mat_name_len)
                    print(f"Material properties for {mat_name}:")
                if mat_struct_ptr_param_b != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_b)
                    mat_param_b_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_b_start)
                    mat_param_b_section_count = readlong(trmtr)
                    for z in range(mat_param_b_section_count):
                        mat_param_b_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_b_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_b_offset)
                        mat_param_b_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_b_struct)
                        mat_param_b_struct_len = readshort(trmtr)

                        if mat_param_b_struct_len != 0x0008:
                            raise AssertionError("Unexpected material param b struct length!")
                        mat_param_b_struct_section_len = readshort(trmtr)
                        mat_param_b_struct_ptr_string = readshort(trmtr)
                        mat_param_b_struct_ptr_params = readshort(trmtr)

                        if mat_param_b_struct_ptr_string != 0:
                            fseek(trmtr, mat_param_b_offset + mat_param_b_struct_ptr_string)
                            mat_param_b_shader_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_b_shader_start)
                            mat_param_b_shader_len = readlong(trmtr)
                            mat_param_b_shader_string = readfixedstring(trmtr, mat_param_b_shader_len)
                            print(f"Shader: {mat_param_b_shader_string}")
                            mat_shader = mat_param_b_shader_string
                        if mat_param_b_struct_ptr_params != 0:
                            fseek(trmtr, mat_param_b_offset + mat_param_b_struct_ptr_params)
                            mat_param_b_sub_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_b_sub_start)
                            mat_param_b_sub_count = readlong(trmtr)
                            for y in range(mat_param_b_sub_count):
                                mat_param_b_sub_offset = ftell(trmtr) + readlong(trmtr)
                                mat_param_b_sub_ret = ftell(trmtr)
                                fseek(trmtr, mat_param_b_sub_offset)
                                mat_param_b_sub_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_b_sub_struct)
                                mat_param_b_sub_struct_len = readshort(trmtr)

                                if mat_param_b_sub_struct_len != 0x0008:
                                    raise AssertionError("Unexpected material param b sub struct length!")
                                mat_param_b_sub_struct_section_len = readshort(trmtr)
                                mat_param_b_sub_struct_ptr_string = readshort(trmtr)
                                mat_param_b_sub_struct_ptr_value = readshort(trmtr)

                                if mat_param_b_sub_struct_ptr_string != 0:
                                    fseek(trmtr, mat_param_b_sub_offset + mat_param_b_sub_struct_ptr_string)
                                    mat_param_b_sub_string_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_b_sub_string_start)
                                    mat_param_b_sub_string_len = readlong(trmtr)
                                    mat_param_b_sub_string = readfixedstring(trmtr, mat_param_b_sub_string_len)
                                if mat_param_b_sub_struct_ptr_value != 0:
                                    fseek(trmtr, mat_param_b_sub_offset + mat_param_b_sub_struct_ptr_value)
                                    mat_param_b_sub_value_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_b_sub_value_start)
                                    mat_param_b_sub_value_len = readlong(trmtr)
                                    mat_param_b_sub_value = readfixedstring(trmtr, mat_param_b_sub_value_len)
                                    print(f"(param_b) {mat_param_b_sub_string}: {mat_param_b_sub_value}")

                                if mat_param_b_sub_string == "EnableBaseColorMap": mat_enable_base_color_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableNormalMap": mat_enable_normal_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableAOMap": mat_enable_ao_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableEmissionColorMap": mat_enable_emission_color_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableRoughnessMap": mat_enable_roughness_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableMetallicMap": mat_enable_metallic_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableDisplacementMap": mat_enable_displacement_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableHighlight": mat_enable_highlight_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableOverrideColor": mat_enable_override_color = mat_param_b_sub_value == "True"
                                fseek(trmtr, mat_param_b_sub_ret)
                        fseek(trmtr, mat_param_b_ret)

                if mat_struct_ptr_param_c != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_c)
                    mat_param_c_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_c_start)
                    mat_param_c_count = readlong(trmtr)

                    for z in range(mat_param_c_count):
                        mat_param_c_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_c_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_c_offset)
                        mat_param_c_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_c_struct)
                        mat_param_c_struct_len = readshort(trmtr)

                        if mat_param_c_struct_len == 0x0008:
                            mat_param_c_struct_section_len = readshort(trmtr)
                            mat_param_c_struct_ptr_string = readshort(trmtr)
                            mat_param_c_struct_ptr_value = readshort(trmtr)
                            mat_param_c_struct_ptr_id = 0
                        elif mat_param_c_struct_len == 0x000A:
                            mat_param_c_struct_section_len = readshort(trmtr)
                            mat_param_c_struct_ptr_string = readshort(trmtr)
                            mat_param_c_struct_ptr_value = readshort(trmtr)
                            mat_param_c_struct_ptr_id = readshort(trmtr)
                        else:
                            raise AssertionError("Unexpected material param c struct length!")

                        if mat_param_c_struct_ptr_string != 0:
                            fseek(trmtr, mat_param_c_offset + mat_param_c_struct_ptr_string)
                            mat_param_c_string_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_c_string_start)
                            mat_param_c_string_len = readlong(trmtr)
                            mat_param_c_string = readfixedstring(trmtr, mat_param_c_string_len)
                        if mat_param_c_struct_ptr_value != 0:
                            fseek(trmtr, mat_param_c_offset + mat_param_c_struct_ptr_value)
                            mat_param_c_value_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_c_value_start)
                            mat_param_c_value_len = readlong(trmtr)  # - 5 # Trimming the ".bntx" from the end.
                            mat_param_c_value = readfixedstring(trmtr, mat_param_c_value_len)
                        if mat_param_c_struct_ptr_id != 0:
                            fseek(trmtr, mat_param_c_offset + mat_param_c_struct_ptr_id)
                            mat_param_c_id = readlong(trmtr)
                        else:
                            mat_param_c_id = 0

                        if mat_param_c_string == "BaseColorMap": mat_col0 = mat_param_c_value
                        elif mat_param_c_string == "LayerMaskMap": mat_lym0 = mat_param_c_value
                        elif mat_param_c_string == "NormalMap": mat_nrm0 = mat_param_c_value
                        elif mat_param_c_string == "AOMap": mat_ao0 = mat_param_c_value
                        elif mat_param_c_string == "EmissionColorMap": mat_emi0 = mat_param_c_value
                        elif mat_param_c_string == "RoughnessMap": mat_rgh0 = mat_param_c_value
                        elif mat_param_c_string == "MetallicMap": mat_mtl0 = mat_param_c_value
                        elif mat_param_c_string == "DisplacementMap": mat_msk0 = mat_param_c_value
                        elif mat_param_c_string == "HighlightMaskMap": mat_highmsk0 = mat_param_c_value

                        # -- There's also all of the following, which aren't automatically assigned to keep things simple.
                        # -- "AOMap"
                        # -- "AOMap1"
                        # -- "AOMap2"
                        # -- "BaseColorMap1"
                        # -- "DisplacementMap"
                        # -- "EyelidShadowMaskMap"
                        # -- "FlowMap"
                        # -- "FoamMaskMap"
                        # -- "GrassCollisionMap"
                        # -- "HighlightMaskMap"
                        # -- "LowerEyelidColorMap"
                        # -- "NormalMap1"
                        # -- "NormalMap2"
                        # -- "PackedMap"
                        # -- "UpperEyelidColorMap"
                        # -- "WeatherLayerMaskMap"
                        # -- "WindMaskMap"

                        print(f"(param_c) {mat_param_c_string}: {mat_param_c_value} [{mat_param_c_id}]")
                        fseek(trmtr, mat_param_c_ret)

                if mat_struct_ptr_param_d != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_d)
                    mat_param_d_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_d_start)
                    mat_param_d_count = readlong(trmtr)

                    for z in range(mat_param_d_count):
                        mat_param_d_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_d_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_d_offset)
                        mat_param_d_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_d_struct)
                        mat_param_d_struct_len = readshort(trmtr)

                        if mat_param_d_struct_len != 0x001E:
                            raise AssertionError("Unexpected material param d struct length!")
                        mat_param_d_struct_section_len = readshort(trmtr)
                        mat_param_d_struct_ptr_a = readshort(trmtr)
                        mat_param_d_struct_ptr_b = readshort(trmtr)
                        mat_param_d_struct_ptr_c = readshort(trmtr)
                        mat_param_d_struct_ptr_d = readshort(trmtr)
                        mat_param_d_struct_ptr_e = readshort(trmtr)
                        mat_param_d_struct_ptr_f = readshort(trmtr)
                        mat_param_d_struct_ptr_g = readshort(trmtr)
                        mat_param_d_struct_ptr_h = readshort(trmtr)
                        mat_param_d_struct_ptr_i = readshort(trmtr)
                        mat_param_d_struct_ptr_j = readshort(trmtr)
                        mat_param_d_struct_ptr_k = readshort(trmtr)
                        mat_param_d_struct_ptr_l = readshort(trmtr)
                        mat_param_d_struct_ptr_m = readshort(trmtr)

                        if mat_param_d_struct_ptr_a != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_a)
                            mat_param_d_value_a = readlong(trmtr)
                        else: mat_param_d_value_a = 0
                        if mat_param_d_struct_ptr_b != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_b)
                            mat_param_d_value_b = readlong(trmtr)
                        else: mat_param_d_value_b = 0
                        if mat_param_d_struct_ptr_c != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_c)
                            mat_param_d_value_c = readlong(trmtr)
                        else: mat_param_d_value_c = 0
                        if mat_param_d_struct_ptr_d != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_d)
                            mat_param_d_value_d = readlong(trmtr)
                        else: mat_param_d_value_d = 0
                        if mat_param_d_struct_ptr_e != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_e)
                            mat_param_d_value_e = readlong(trmtr)
                        else: mat_param_d_value_e = 0
                        if mat_param_d_struct_ptr_f != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_f)
                            mat_param_d_value_f = readlong(trmtr)
                        else: mat_param_d_value_f = 0
                        if mat_param_d_struct_ptr_g != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_g)
                            mat_param_d_value_g = readlong(trmtr)
                        else: mat_param_d_value_g = 0
                        if mat_param_d_struct_ptr_h != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_h)
                            mat_param_d_value_h = readlong(trmtr)
                        else: mat_param_d_value_h = 0
                        if mat_param_d_struct_ptr_i != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_i)
                            mat_param_d_value_i = readlong(trmtr)
                        else: mat_param_d_value_i = 0
                        if mat_param_d_struct_ptr_j != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_j)
                            mat_param_d_value_j = readlong(trmtr)
                        else: mat_param_d_value_j = 0
                        if mat_param_d_struct_ptr_k != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_k)
                            mat_param_d_value_k = readlong(trmtr)
                        else: mat_param_d_value_k = 0
                        if mat_param_d_struct_ptr_l != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_l)
                            mat_param_d_value_l = readlong(trmtr)
                        else: mat_param_d_value_l = 0
                        if mat_param_d_struct_ptr_m != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_m)
                            mat_param_d_value_m1 = readfloat(trmtr); mat_param_d_value_m2 = readfloat(trmtr); mat_param_d_value_m3 = readfloat(trmtr)
                        else: mat_param_d_value_m1 = 0; mat_param_d_value_m2 = 0; mat_param_d_value_m3 = 0

                        print(f"Flags #{z}: {mat_param_d_value_a} | {mat_param_d_value_b} | {mat_param_d_value_c} | {mat_param_d_value_d} | {mat_param_d_value_e} | {mat_param_d_value_f} | {mat_param_d_value_g} | {mat_param_d_value_h} | {mat_param_d_value_i} | {mat_param_d_value_j} | {mat_param_d_value_k} | {mat_param_d_value_l} | {mat_param_d_value_m1} | {mat_param_d_value_m2} | {mat_param_d_value_m3}")
                        fseek(trmtr, mat_param_d_ret)

                if mat_struct_ptr_param_e != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_e)
                    mat_param_e_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_e_start)
                    mat_param_e_count = readlong(trmtr)

                    for z in range(mat_param_e_count):
                        mat_param_e_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_e_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_e_offset)
                        mat_param_e_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_e_struct)
                        mat_param_e_struct_len = readshort(trmtr)

                        if mat_param_e_struct_len == 0x0006:
                            mat_param_e_struct_section_len = readshort(trmtr)
                            mat_param_e_struct_ptr_string = readshort(trmtr)
                            mat_param_e_struct_ptr_value = 0
                        elif mat_param_e_struct_len == 0x0008:
                            mat_param_e_struct_section_len = readshort(trmtr)
                            mat_param_e_struct_ptr_string = readshort(trmtr)
                            mat_param_e_struct_ptr_value = readshort(trmtr)
                        else:
                            raise Exception(f"Unknown mat_param_e struct length!")

                        if mat_param_e_struct_ptr_string != 0:
                            fseek(trmtr, mat_param_e_offset + mat_param_e_struct_ptr_string)
                            mat_param_e_string_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_e_string_start)
                            mat_param_e_string_len = readlong(trmtr)
                            mat_param_e_string = readfixedstring(trmtr, mat_param_e_string_len)

                        if mat_param_e_struct_ptr_value != 0:
                            fseek(trmtr, mat_param_e_offset + mat_param_e_struct_ptr_value)
                            mat_param_e_value = readfloat(trmtr)
                        else: mat_param_e_value = 0

                        if mat_param_e_string == "Roughness": mat_rgh_layer0 = mat_param_e_value
                        elif mat_param_e_string == "RoughnessLayer1": mat_rgh_layer1 = mat_param_e_value
                        elif mat_param_e_string == "RoughnessLayer2": mat_rgh_layer2 = mat_param_e_value
                        elif mat_param_e_string == "RoughnessLayer3": mat_rgh_layer3 = mat_param_e_value
                        elif mat_param_e_string == "RoughnessLayer4": mat_rgh_layer4 = mat_param_e_value
                        elif mat_param_e_string == "Metallic": mat_mtl_layer0 = mat_param_e_value
                        elif mat_param_e_string == "MetallicLayer1": mat_mtl_layer1 = mat_param_e_value
                        elif mat_param_e_string == "MetallicLayer2": mat_mtl_layer2 = mat_param_e_value
                        elif mat_param_e_string == "MetallicLayer3": mat_mtl_layer3 = mat_param_e_value
                        elif mat_param_e_string == "MetallicLayer4": mat_mtl_layer4 = mat_param_e_value
                        elif mat_param_e_string == "Reflectance": mat_reflectance = mat_param_e_value
                        elif mat_param_e_string == "EmissionIntensity": mat_emm_intensity = mat_param_e_value
                        
                        print(f"(param_e) {mat_param_e_string}: {mat_param_e_value}")
                        fseek(trmtr, mat_param_e_ret)

                if mat_struct_ptr_param_f != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_f)
                    mat_param_f_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_f_start)
                    mat_param_f_count = readlong(trmtr)

                    for z in range(mat_param_f_count):
                        mat_param_f_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_f_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_f_offset)
                        mat_param_f_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_f_struct)
                        mat_param_f_struct_len = readlong(trmtr)

                        if mat_param_f_struct_len != 0x0008:
                            raise Exception(f"Unknown mat_param_f struct length!")
                        mat_param_f_struct_section_len = readshort(trmtr)
                        mat_param_f_struct_ptr_string = readshort(trmtr)
                        mat_param_f_struct_ptr_values = readshort(trmtr)

                        if mat_param_f_struct_ptr_string != 0:
                            fseek(trmtr, mat_param_f_offset + mat_param_f_struct_ptr_string)
                            mat_param_f_string_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_f_string_start)
                            mat_param_f_string_len = readlong(trmtr)
                            mat_param_f_string = readfixedstring(trmtr, mat_param_f_string_len)

                        if mat_param_f_struct_ptr_values != 0:
                            fseek(trmtr, mat_param_f_offset + mat_param_f_struct_ptr_values)
                            mat_param_f_value1 = readfloat(trmtr)
                            mat_param_f_value2 = readfloat(trmtr)
                        else: mat_param_f_value1 = mat_param_f_value2 = 0

                        print(f"(param_f) {mat_param_f_string}: {mat_param_f_value1}, {mat_param_f_value2}")
                        fseek(trmtr, mat_param_f_ret)

                if mat_struct_ptr_param_g != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_g)
                    mat_param_g_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_g_start)
                    mat_param_g_count = readlong(trmtr)

                    for z in range(mat_param_g_count):
                        mat_param_g_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_g_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_g_offset)
                        mat_param_g_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_g_struct)
                        mat_param_g_struct_len = readlong(trmtr)

                        if mat_param_g_struct_len != 0x0008:
                            raise Exception(f"Unknown mat_param_g struct length!")
                        mat_param_g_struct_section_len = readshort(trmtr)
                        mat_param_g_struct_ptr_string = readshort(trmtr)
                        mat_param_g_struct_ptr_values = readshort(trmtr)

                        if mat_param_g_struct_ptr_string != 0:
                            fseek(trmtr, mat_param_g_offset + mat_param_g_struct_ptr_string)
                            mat_param_g_string_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_g_string_start)
                            mat_param_g_string_len = readlong(trmtr)
                            mat_param_g_string = readfixedstring(trmtr, mat_param_g_string_len)

                        if mat_param_g_struct_ptr_values != 0:
                            fseek(trmtr, mat_param_g_offset + mat_param_g_struct_ptr_values)
                            mat_param_g_value1 = readfloat(trmtr)
                            mat_param_g_value2 = readfloat(trmtr)
                            mat_param_g_value3 = readfloat(trmtr)
                        else: mat_param_g_value1 = mat_param_g_value2 = mat_param_g_value3 = 0

                        print(f"(param_g) {mat_param_g_string}: {mat_param_g_value1}, {mat_param_g_value2}, {mat_param_g_value3}")
                        fseek(trmtr, mat_param_g_ret)

                if mat_struct_ptr_param_h != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_h)
                    mat_param_h_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_h_start)
                    mat_param_h_count = readlong(trmtr)

                    for z in range(mat_param_h_count):
                        mat_param_h_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_h_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_h_offset)
                        mat_param_h_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_h_struct)
                        mat_param_h_struct_len = readshort(trmtr)

                        if mat_param_h_struct_len != 0x0008:
                            raise Exception(f"Unknown mat_param_h struct length!")
                        mat_param_h_struct_section_len = readshort(trmtr)
                        mat_param_h_struct_ptr_string = readshort(trmtr)
                        mat_param_h_struct_ptr_values = readshort(trmtr)

                        if mat_param_h_struct_ptr_string != 0:
                            fseek(trmtr, mat_param_h_offset + mat_param_h_struct_ptr_string)
                            mat_param_h_string_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_h_string_start)
                            mat_param_h_string_len = readlong(trmtr)
                            mat_param_h_string = readfixedstring(trmtr, mat_param_h_string_len)

                        if mat_param_h_struct_ptr_values != 0:
                            fseek(trmtr, mat_param_h_offset + mat_param_h_struct_ptr_values)
                            mat_param_h_value1 = readfloat(trmtr)
                            mat_param_h_value2 = readfloat(trmtr)
                            mat_param_h_value3 = readfloat(trmtr)
                            mat_param_h_value4 = readfloat(trmtr)
                        else: mat_param_h_value1 = mat_param_h_value2 = mat_param_h_value3 = mat_param_h_value4 = 0

                        if mat_param_h_string == "UVScaleOffset": mat_uv_scale_u = mat_param_h_value1; mat_uv_scale_v = mat_param_h_value2; mat_uv_trs_u = mat_param_h_value3; mat_uv_trs_v = mat_param_h_value4
                        elif mat_param_h_string == "UVScaleOffset1": mat_uv_scale2_u = mat_param_h_value1; mat_uv_scale2_v = mat_param_h_value2; mat_uv_trs2_u = mat_param_h_value3; mat_uv_trs2_v = mat_param_h_value4
                        elif mat_param_h_string == "BaseColor": mat_color_r = mat_param_h_value1; mat_color_g = mat_param_h_value2; mat_color_b = mat_param_h_value3
                        elif mat_param_h_string == "BaseColorLayer1": mat_color1_r = mat_param_h_value1; mat_color1_g = mat_param_h_value2; mat_color1_b = mat_param_h_value3
                        elif mat_param_h_string == "BaseColorLayer2": mat_color2_r = mat_param_h_value1; mat_color2_g = mat_param_h_value2; mat_color2_b = mat_param_h_value3
                        elif mat_param_h_string == "BaseColorLayer3": mat_color3_r = mat_param_h_value1; mat_color3_g = mat_param_h_value2; mat_color3_b = mat_param_h_value3
                        elif mat_param_h_string == "BaseColorLayer4": mat_color4_r = mat_param_h_value1; mat_color4_g = mat_param_h_value2; mat_color4_b = mat_param_h_value3
                        elif mat_param_h_string == "EmissionColorLayer1": mat_emcolor1_r = mat_param_h_value1; mat_emcolor1_g = mat_param_h_value2; mat_emcolor1_b = mat_param_h_value3
                        elif mat_param_h_string == "EmissionColorLayer2": mat_emcolor2_r = mat_param_h_value1; mat_emcolor2_g = mat_param_h_value2; mat_emcolor2_b = mat_param_h_value3
                        elif mat_param_h_string == "EmissionColorLayer3": mat_emcolor3_r = mat_param_h_value1; mat_emcolor3_g = mat_param_h_value2; mat_emcolor3_b = mat_param_h_value3
                        elif mat_param_h_string == "EmissionColorLayer4": mat_emcolor4_r = mat_param_h_value1; mat_emcolor4_g = mat_param_h_value2; mat_emcolor4_b = mat_param_h_value3
                        elif mat_param_h_string == "EmissionColorLayer5": mat_emcolor5_r = mat_param_h_value1; mat_emcolor5_g = mat_param_h_value2; mat_emcolor5_b = mat_param_h_value3
                        else: print(f"Unknown mat_param_h: {mat_param_h_string}")

                        print(f"(param_h) {mat_param_h_string}: {mat_param_h_value1}, {mat_param_h_value2}, {mat_param_h_value3}, {mat_param_h_value4}")
                        fseek(trmtr, mat_param_h_ret)

                if mat_struct_ptr_param_i != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_i)
                    mat_param_i_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_i_start)
                    mat_param_i_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_i_struct)
                    mat_param_i_struct_len = readlong(trmtr)

                    if mat_param_i_struct_len != 0x0000:
                        raise Exception(f"Unknown mat_param_i struct length!")

                if mat_struct_ptr_param_j != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_j)
                    mat_param_j_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_j_start)
                    mat_param_j_count = readlong(trmtr)

                    for y in range(mat_param_j_count):
                        mat_param_j_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_j_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_j_offset)
                        mat_param_j_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_j_struct)
                        mat_param_j_struct_len = readshort(trmtr)

                        if mat_param_j_struct_len == 0x0006:
                            mat_param_j_struct_section_len = readshort(trmtr)
                            mat_param_j_struct_ptr_string = readshort(trmtr)
                            mat_param_j_struct_ptr_value = 0
                        elif mat_param_j_struct_len == 0x0008:
                            mat_param_j_struct_section_len = readshort(trmtr)
                            mat_param_j_struct_ptr_string = readshort(trmtr)
                            mat_param_j_struct_ptr_value = readshort(trmtr)
                        else:
                            raise Exception(f"Unknown mat_param_j struct length!")

                        if mat_param_j_struct_ptr_string != 0:
                            fseek(trmtr, mat_param_j_offset + mat_param_j_struct_ptr_string)
                            mat_param_j_string_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_j_string_start)
                            mat_param_j_string_len = readlong(trmtr)
                            mat_param_j_string = readfixedstring(trmtr, mat_param_j_string_len)

                        if mat_param_j_struct_ptr_value != 0:
                            fseek(trmtr, mat_param_j_offset + mat_param_j_struct_ptr_value)
                            mat_param_j_value = readlong(trmtr)
                        else: mat_param_j_value = "0" # why is this a string?

                        print(f"(param_j) {mat_param_j_string}: {mat_param_j_value}")
                        fseek(trmtr, mat_param_j_ret)

                if mat_struct_ptr_param_k != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_k)
                    mat_param_k_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_k_start)
                    mat_param_k_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_k_struct)
                    mat_param_k_struct_len = readlong(trmtr)

                    if mat_param_k_struct_len != 0x0000:
                        raise Exception(f"Unexpected mat_param_k struct length!")

                if mat_struct_ptr_param_l != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_l)
                    mat_param_l_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_l_start)
                    mat_param_l_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_l_struct)
                    mat_param_l_struct_len = readlong(trmtr)

                    if mat_param_l_struct_len != 0x0000:
                        raise Exception(f"Unexpected mat_param_l struct length!")

                if mat_struct_ptr_param_m != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_m)
                    mat_param_m_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_m_start)
                    mat_param_m_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_m_struct)
                    mat_param_m_struct_len = readlong(trmtr)

                    if mat_param_m_struct_len != 0x0000:
                        raise Exception(f"Unexpected mat_param_m struct length!")

                if mat_struct_ptr_param_n != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_n)
                    mat_param_n_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_n_start)
                    mat_param_n_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_n_struct)
                    mat_param_n_struct_len = readshort(trmtr)

                    if mat_param_n_struct_len == 0x0004:
                        mat_param_n_struct_section_len = readshort(trmtr)
                        mat_param_n_struct_unk = 0
                    elif mat_param_n_struct_len == 0x0006:
                        mat_param_n_struct_section_len = readshort(trmtr)
                        mat_param_n_struct_unk = readshort(trmtr)
                    else:
                        raise Exception(f"Unexpected mat_param_n struct length!")

                    if mat_param_n_struct_unk != 0:
                        fseek(trmtr, mat_param_n_start + mat_param_n_struct_unk)
                        mat_param_n_value =  readbyte(trmtr)
                        print(f"Unknown value A = {mat_param_n_value}")

                if mat_struct_ptr_param_o != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_o)
                    mat_param_o_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_o_start)
                    mat_param_o_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_o_struct)
                    mat_param_o_struct_len = readshort(trmtr)

                    if mat_param_o_struct_len == 0x0004:
                        mat_param_o_struct_section_len = readshort(trmtr)
                        mat_param_o_struct_unk = 0
                        mat_param_o_struct_value = 0
                    elif mat_param_o_struct_len == 0x0008:
                        mat_param_o_struct_section_len = readshort(trmtr)
                        mat_param_o_struct_unk = readshort(trmtr)
                        mat_param_o_struct_value = readshort(trmtr)
                    else:
                        raise Exception(f"Unexpected mat_param_o struct length!")

                    if mat_param_o_struct_unk != 0:
                        fseek(trmtr, mat_param_o_start + mat_param_o_struct_unk)
                        mat_param_o_value =  readbyte(trmtr)
                        print(f"Unknown value B = {mat_param_o_value}")

                if mat_struct_ptr_param_p != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_p)
                    mat_param_p_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_p_start)
                    mat_param_p_string_len = readlong(trmtr)
                    mat_param_p_string = readfixedstring(trmtr, mat_param_p_string_len)
                    print(mat_param_p_string)

                mat_data_array.append({
                    "mat_name": mat_name,
                    "mat_shader": mat_shader,
                    "mat_col0": mat_col0,
                    "mat_lym0": mat_lym0,
                    "mat_nrm0": mat_nrm0,
                    "mat_ao0": mat_ao0,
                    "mat_emi0": mat_emi0,
                    "mat_rgh0": mat_rgh0,
                    "mat_mtl0": mat_mtl0,
                    "mat_msk0": mat_msk0,
                    "mat_highmsk0": mat_highmsk0,
                    "mat_color_r": mat_color_r, "mat_color_g": mat_color_g, "mat_color_b": mat_color_b,
                    "mat_color1_r": mat_color1_r, "mat_color1_g": mat_color1_g, "mat_color1_b": mat_color1_b,
                    "mat_color2_r": mat_color2_r, "mat_color2_g": mat_color2_g, "mat_color2_b": mat_color2_b,
                    "mat_color3_r": mat_color3_r, "mat_color3_g": mat_color3_g, "mat_color3_b": mat_color3_b,
                    "mat_color4_r": mat_color4_r, "mat_color4_g": mat_color4_g, "mat_color4_b": mat_color4_b,
                    "mat_emcolor1_r": mat_emcolor1_r, "mat_emcolor1_g": mat_emcolor1_g, "mat_emcolor1_b": mat_emcolor1_b,
                    "mat_emcolor2_r": mat_emcolor2_r, "mat_emcolor2_g": mat_emcolor2_g, "mat_emcolor2_b": mat_emcolor2_b,
                    "mat_emcolor3_r": mat_emcolor3_r, "mat_emcolor3_g": mat_emcolor3_g, "mat_emcolor3_b": mat_emcolor3_b,
                    "mat_emcolor4_r": mat_emcolor4_r, "mat_emcolor4_g": mat_emcolor4_g, "mat_emcolor4_b": mat_emcolor4_b,
                    "mat_emcolor5_r": mat_emcolor5_r, "mat_emcolor5_g": mat_emcolor5_g, "mat_emcolor5_b": mat_emcolor5_b,
                    "mat_rgh_layer0": mat_rgh_layer0, "mat_rgh_layer1": mat_rgh_layer1, "mat_rgh_layer2": mat_rgh_layer2, "mat_rgh_layer3": mat_rgh_layer3, "mat_rgh_layer4": mat_rgh_layer4,
                    "mat_mtl_layer0": mat_mtl_layer0, "mat_mtl_layer1": mat_mtl_layer1, "mat_mtl_layer2": mat_mtl_layer2, "mat_mtl_layer3": mat_mtl_layer3, "mat_mtl_layer4": mat_mtl_layer4,
                    "mat_reflectance": mat_reflectance,
                    "mat_emm_intensity": mat_emm_intensity,
                    "mat_uv_scale_u": mat_uv_scale_u, "mat_uv_scale_v": mat_uv_scale_v,
                    "mat_uv_scale2_u": mat_uv_scale2_u, "mat_uv_scale2_v": mat_uv_scale2_v,
                    "mat_enable_base_color_map": mat_enable_base_color_map,
                    "mat_enable_normal_map": mat_enable_normal_map,
                    "mat_enable_ao_map": mat_enable_ao_map,
                    "mat_enable_emission_color_map": mat_enable_emission_color_map,
                    "mat_enable_roughness_map": mat_enable_roughness_map,
                    "mat_enable_metallic_map": mat_enable_metallic_map,
                    "mat_enable_displacement_map": mat_enable_displacement_map,
                    "mat_enable_highlight_map": mat_enable_highlight_map
                })
                fseek(trmtr, mat_ret)
            print("--------------------")

        fclose(trmtr)

        if IN_BLENDER_ENV:
            # process materials
            for m, mat in enumerate(mat_data_array):
                material = bpy.data.materials.new(name=mat["mat_name"])
                material.use_nodes = True
                materials.append(material)
                
                if 'skin' in mat["mat_name"]:
                    blend_type = "MULTIPLY"
                else:
                    blend_type = "MIX"

                material_output = material.node_tree.nodes.get("Material Output")
                principled_bsdf = material.node_tree.nodes.get("Principled BSDF")
                material.node_tree.links.new(principled_bsdf.outputs[0], material_output.inputs[0])

                print(f"mat_shader = {mat['mat_shader']}")
                
                material.blend_method = ("HASHED")
                material.shadow_method = ("OPAQUE")
                
                color_output = principled_bsdf.inputs[0]
                if mat["mat_shader"] == "Unlit":
                    color_output = material_output.inputs[0]
                if mat["mat_shader"] == "Transparent":
                    material.blend_method = ("BLEND")
                    reflectionpart1 = material.node_tree.nodes.new("ShaderNodeMath")
                    reflectionpart1.operation = "SQRT"
                    reflectionpart1.inputs[0].default_value = mat["mat_reflectance"]

                    reflectionpart2 = material.node_tree.nodes.new("ShaderNodeMath")
                    reflectionpart2.inputs[0].default_value = 1.0
                    reflectionpart2.operation = "ADD"
                    
                    reflectionpart3 = material.node_tree.nodes.new("ShaderNodeMath")
                    reflectionpart3.inputs[0].default_value = 1.0
                    reflectionpart3.operation = "SUBTRACT"

                    reflectionpart4 = material.node_tree.nodes.new("ShaderNodeMath")
                    reflectionpart4.operation = "DIVIDE"

                    reflectionpart5 = material.node_tree.nodes.new("ShaderNodeFresnel")
 
                    reflectionpart6 = material.node_tree.nodes.new("ShaderNodeMath")
                    reflectionpart6.inputs[0].default_value = 0.25
                    reflectionpart6.operation = "SUBTRACT"
 
                    material.node_tree.links.new(reflectionpart1.outputs[0], reflectionpart2.inputs[1])
                    material.node_tree.links.new(reflectionpart1.outputs[0], reflectionpart3.inputs[1])
                    material.node_tree.links.new(reflectionpart2.outputs[0], reflectionpart4.inputs[0])
                    material.node_tree.links.new(reflectionpart3.outputs[0], reflectionpart4.inputs[1])
                    material.node_tree.links.new(reflectionpart4.outputs[0], reflectionpart5.inputs[0])
                    
                material.use_backface_culling = True
                

                
                basecolor = (mat["mat_color_r"], mat["mat_color_g"], mat["mat_color_b"], 1.0)
                # LAYER MASK MAP
                
                lym_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                if os.path.exists(os.path.join(filep, mat["mat_lym0"][:-5] + textureextension)) == True:
                    lym_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_lym0"][:-5] + textureextension))
                    lym_image_texture.image.colorspace_settings.name = "Non-Color"
                huesaturationvalue = material.node_tree.nodes.new("ShaderNodeHueSaturation")
                huesaturationvalue.inputs[2].default_value = 2.0
                huesaturationvalue2 = material.node_tree.nodes.new("ShaderNodeHueSaturation")
                huesaturationvalue2.inputs[2].default_value = 2.0
                
                color1 = (mat["mat_color1_r"], mat["mat_color1_g"], mat["mat_color1_b"], 1.0)
                color2 = (mat["mat_color2_r"], mat["mat_color2_g"], mat["mat_color2_b"], 1.0)
                color3 = (mat["mat_color3_r"], mat["mat_color3_g"], mat["mat_color3_b"], 1.0)
                color4 = (mat["mat_color4_r"], mat["mat_color4_g"], mat["mat_color4_b"], 1.0)
                
                
                emcolor1 = (mat["mat_emcolor1_r"], mat["mat_emcolor1_g"], mat["mat_emcolor1_b"], 1.0)
                emcolor2 = (mat["mat_emcolor2_r"], mat["mat_emcolor2_g"], mat["mat_emcolor2_b"], 1.0)
                emcolor3 = (mat["mat_emcolor3_r"], mat["mat_emcolor3_g"], mat["mat_emcolor3_b"], 1.0)                   
                emcolor4 = (mat["mat_emcolor4_r"], mat["mat_emcolor4_g"], mat["mat_emcolor4_b"], 1.0)
                if emcolor1 == (1.0, 1.0, 1.0, 1.0):
                    emcolor1 = (0.0, 0.0, 0.0, 0.0)
                if emcolor2 == (1.0, 1.0, 1.0, 1.0):
                    emcolor2 = (0.0, 0.0, 0.0, 0.0)
                if emcolor3 == (1.0, 1.0, 1.0, 1.0):
                    emcolor3 = (0.0, 0.0, 0.0, 0.0)
                if emcolor4 == (1.0, 1.0, 1.0, 1.0):
                    emcolor4 = (0.0, 0.0, 0.0, 0.0)
                print(f'Material {mat["mat_name"]}:')
                print(f"Color 1: {color1}")
                print(f"Color 2: {color2}")
                print(f"Color 3: {color3}")
                print(f"Color 4: {color4}")
                print(f"Emission Color 1: {emcolor1}")
                print(f"Emission Color 2: {emcolor2}")
                print(f"Emission Color 3: {emcolor3}")
                print(f"Emission Color 4: {emcolor4}")
                print("---")
     
                mix_color1 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_color1.blend_type = blend_type
                mix_color1.inputs[0].default_value = 0.0
                mix_color1.inputs[1].default_value = (1, 1, 1, 1)
                mix_color1.inputs[2].default_value = color1
                mix_color2 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_color2.blend_type = blend_type
                mix_color2.inputs[0].default_value = 0.0
                mix_color2.inputs[1].default_value = (0, 0, 0, 0)
                mix_color2.inputs[2].default_value = color2
                mix_color3 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_color3.blend_type = blend_type
                mix_color3.inputs[0].default_value = 0.0
                mix_color3.inputs[1].default_value = (0, 0, 0, 0)
                mix_color3.inputs[2].default_value = color3
                mix_color4 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_color4.blend_type = blend_type
                mix_color4.inputs[0].default_value = 0.0
                mix_color4.inputs[1].default_value = (0, 0, 0, 0)
                mix_color4.inputs[2].default_value = color4
                mix_color5 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_color5.blend_type = blend_type
                mix_color5.inputs[0].default_value = 0.0
                mix_color5.inputs[1].default_value = (0, 0, 0, 0)
                mix_color5.inputs[2].default_value = (1, 1, 1, 1)
                
                
                
                mix_emcolor1 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_emcolor1.blend_type = blend_type
                mix_emcolor1.inputs[1].default_value = (0, 0, 0, 0)
                mix_emcolor1.inputs[2].default_value = emcolor1
                mix_emcolor2 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_emcolor2.blend_type = blend_type
                mix_emcolor2.inputs[1].default_value = (0, 0, 0, 0)
                mix_emcolor2.inputs[2].default_value = emcolor2
                mix_emcolor3 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_emcolor3.blend_type = blend_type
                mix_emcolor3.inputs[1].default_value = (0, 0, 0, 0)
                mix_emcolor3.inputs[2].default_value = emcolor3
                mix_emcolor4 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_emcolor4.blend_type = blend_type
                mix_emcolor4.inputs[1].default_value = (0, 0, 0, 0)
                mix_emcolor4.inputs[2].default_value = emcolor4
                
                material.node_tree.links.new(mix_color1.outputs[0], mix_color2.inputs[1])
                material.node_tree.links.new(mix_color2.outputs[0], mix_color3.inputs[1])
                material.node_tree.links.new(mix_color3.outputs[0], mix_color4.inputs[1])
                material.node_tree.links.new(mix_color3.outputs[0], mix_color4.inputs[1])
                material.node_tree.links.new(mix_color4.outputs[0], color_output)

                material.node_tree.links.new(mix_emcolor1.outputs[0], mix_emcolor2.inputs[1])
                material.node_tree.links.new(mix_emcolor2.outputs[0], mix_emcolor3.inputs[1])
                material.node_tree.links.new(mix_emcolor3.outputs[0], mix_emcolor4.inputs[1])
                material.node_tree.links.new(mix_emcolor3.outputs[0], mix_emcolor4.inputs[1])
                material.node_tree.links.new(mix_emcolor4.outputs[0], principled_bsdf.inputs[19])
              
                
                separate_color = material.node_tree.nodes.new("ShaderNodeSeparateRGB")
                material.node_tree.links.new(lym_image_texture.outputs[0], huesaturationvalue.inputs[4])
                material.node_tree.links.new(huesaturationvalue.outputs[0], separate_color.inputs[0])
                material.node_tree.links.new(separate_color.outputs[0], mix_color1.inputs[0])
                material.node_tree.links.new(separate_color.outputs[1], mix_color2.inputs[0])
                material.node_tree.links.new(separate_color.outputs[2], mix_color3.inputs[0])
                material.node_tree.links.new(lym_image_texture.outputs[1],  huesaturationvalue2.inputs[4])
                material.node_tree.links.new(huesaturationvalue2.outputs[0],  mix_color4.inputs[0])

                material.node_tree.links.new(separate_color.outputs[0], mix_emcolor1.inputs[0])
                material.node_tree.links.new(separate_color.outputs[1], mix_emcolor2.inputs[0])
                material.node_tree.links.new(separate_color.outputs[2], mix_emcolor3.inputs[0])
                material.node_tree.links.new(huesaturationvalue2.outputs[0],  mix_emcolor4.inputs[0])
    
                
                
                if os.path.exists(os.path.join(filep, mat["mat_col0"][:-5] + textureextension)) == True:
                    alb_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                    alb_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_col0"][:-5] + textureextension))
                    material.node_tree.links.new(alb_image_texture.outputs[0], mix_color1.inputs[1])
                    material.node_tree.links.new(alb_image_texture.outputs[1],  principled_bsdf.inputs[21])
                    if 'hair' in mat["mat_name"] in mat["mat_name"] and basecolor != (1, 1, 1, 1):
                        haircolor = material.node_tree.nodes.new("ShaderNodeMixRGB")
                        haircolor.blend_type = "MULTIPLY"
                        haircolor.inputs[0].default_value = 1.0
                        material.node_tree.links.new(alb_image_texture.outputs[0], haircolor.inputs[1])
                        haircolor.inputs[2].default_value = basecolor
                        material.node_tree.links.new(haircolor.outputs[0], color_output)
                        
                if mat["mat_enable_highlight_map"]:
                    highlight_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")                        
                    if os.path.exists(os.path.join(filep, mat["mat_highmsk0"][:-5] + ".png")) == True:
                        highlight_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_highmsk0"][:-5] + ".png"))
                        highlight_image_texture.image.colorspace_settings.name = "Non-Color"
                    elif os.path.exists(os.path.join(filep, mat["mat_col0"][:-8] + "msk.png")) == True:
                        highlight_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_col0"][:-8] + "msk.png"))
                        highlight_image_texture.image.colorspace_settings.name = "Non-Color"
                    elif os.path.exists(os.path.join(filep, mat["mat_col0"][:-8] + "msk.png")) == True:
                        highlight_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_col0"][:-8] + "msk.png"))
                        highlight_image_texture.image.colorspace_settings.name = "Non-Color"
                    elif os.path.exists(os.path.join(filep, mat["mat_col0"][:-12] + "r_eye_msk.png")) == True and mat["mat_name"] == "eye_r":
                        highlight_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_col0"][:-12] + "r_eye_msk.png"))
                        highlight_image_texture.image.colorspace_settings.name = "Non-Color"
                    elif os.path.exists(os.path.join(filep, mat["mat_col0"][:-12] + "l_eye_msk.png")) == True and mat["mat_name"] == "eye_l":
                        highlight_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_col0"][:-12] + "l_eye_msk.png"))
                        highlight_image_texture.image.colorspace_settings.name = "Non-Color"
                    else:
                        print("No Highlight")
                    material.node_tree.links.new(highlight_image_texture.outputs[0],  mix_color5.inputs[0])
                    material.node_tree.links.new(mix_color4.outputs[0], mix_color5.inputs[1])
                    material.node_tree.links.new(mix_color5.outputs[0], color_output)

                if mat["mat_enable_normal_map"]:
                    normal_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                    if os.path.exists(os.path.join(filep, mat["mat_nrm0"][:-5] + textureextension)) == True:
                        normal_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_nrm0"][:-5] + textureextension))
                        normal_image_texture.image.colorspace_settings.name = "Non-Color"
                    separate_color2 = material.node_tree.nodes.new("ShaderNodeSeparateRGB")
                    combine_color2 = material.node_tree.nodes.new("ShaderNodeCombineColor")
                    normal_map2 = material.node_tree.nodes.new("ShaderNodeNormalMap")
                    material.node_tree.links.new(normal_image_texture.outputs[0], separate_color2.inputs[0])
                    material.node_tree.links.new(separate_color2.outputs[0], combine_color2.inputs[0])
                    material.node_tree.links.new(separate_color2.outputs[1], combine_color2.inputs[1])
                    material.node_tree.links.new(normal_image_texture.outputs[1], combine_color2.inputs[2])
                    material.node_tree.links.new(combine_color2.outputs[0], normal_map2.inputs[1])
                    material.node_tree.links.new(normal_map2.outputs[0], principled_bsdf.inputs[22])

                    
                if mat["mat_enable_metallic_map"]:
                    metalness_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                    if os.path.exists(os.path.join(filep, mat["mat_mtl0"][:-5] + textureextension)) == True:
                        metalness_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_mtl0"][:-5] + textureextension))
                        metalness_image_texture.image.colorspace_settings.name = "Non-Color"
                    material.node_tree.links.new(metalness_image_texture.outputs[0], principled_bsdf.inputs[6])

                if mat["mat_enable_emission_color_map"]:
                    emission_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                    if os.path.exists(os.path.join(filep, mat["mat_emi0"][:-5] + textureextension)) == True:
                        emission_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_emi0"][:-5] + textureextension))
                    material.node_tree.links.new(emission_image_texture.outputs[0], principled_bsdf.inputs[19])                        
                    
                if mat["mat_enable_roughness_map"]:
                    roughness_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                    if os.path.exists(os.path.join(filep, mat["mat_rgh0"][:-5] + textureextension)) == True:
                        roughness_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_rgh0"][:-5] + textureextension))
                        roughness_image_texture.image.colorspace_settings.name = "Non-Color"
                    material.node_tree.links.new(roughness_image_texture.outputs[0], principled_bsdf.inputs[9])
                    
                if mat["mat_enable_ao_map"]:
                    ambientocclusion_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                    if os.path.exists(os.path.join(filep, mat["mat_ao0"][:-5] + textureextension)) == True:            
                        ambientocclusion_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_ao0"][:-5] + textureextension))
                    mix_color6 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                    mix_color6.blend_type = "MULTIPLY"
                    if mat["mat_ao0"][:-5] == "../../glb_share_tex/texture_white_ao/texture_white_ao":
                        mix_color6.inputs[0].default_value = 0
                    else:
                        mix_color6.inputs[0].default_value = 1.0
                    if mix_color5 == True:
                        material.node_tree.links.new(mix_color5.outputs[0], mix_color6.inputs[0])
                        material.node_tree.links.new(ambientocclusion_image_texture.outputs[0], mix_color6.inputs[1])
                        material.node_tree.links.new(mix_color6.outputs[0], color_output)
                    else:
                        material.node_tree.links.new(mix_color4.outputs[0], mix_color6.inputs[1])
                        material.node_tree.links.new(ambientocclusion_image_texture.outputs[0], mix_color6.inputs[2])
                        material.node_tree.links.new(mix_color6.outputs[0], color_output)
                    if 'hair' in mat["mat_name"] in mat["mat_name"] and basecolor != (1, 1, 1, 1):
                        material.node_tree.links.new(mix_color6.outputs[0], haircolor.inputs[1])
                        material.node_tree.links.new(haircolor.outputs[0], color_output)
                if os.path.exists(os.path.join(filep, mat["mat_col0"][:-5] + textureextension)) == True:
                    if color1 == (1.0, 1.0, 1.0, 1.0) and color2 == (1.0, 1.0, 1.0, 1.0) and color3 == (1.0, 1.0, 1.0, 1.0) and color4 == (1.0, 1.0, 1.0, 1.0):
                        if mat["mat_enable_ao_map"]:
                            material.node_tree.links.new(alb_image_texture.outputs[0],  mix_color6.inputs[1])
                        else:
                            material.node_tree.links.new(alb_image_texture.outputs[0],  mix_color5.inputs[1])                   

                if mat["mat_color1_r"] == (1.0) and mat["mat_color1_g"] == (1.0) and mat["mat_color1_b"] == (1.0):
                    color1 = mix_color1.inputs[0].links[0]
                    material.node_tree.links.remove(color1)
    
                if mat["mat_color2_r"] == (1.0) and mat["mat_color2_g"] == (1.0) and mat["mat_color2_b"] == (1.0):
                    color2 = mix_color2.inputs[0].links[0]
                    material.node_tree.links.remove(color2)                    
    
                if mat["mat_color3_r"] == (1.0) and mat["mat_color3_g"] == (1.0) and mat["mat_color3_b"] == (1.0):
                    color3 = mix_color3.inputs[0].links[0]
                    material.node_tree.links.remove(color3)                    
    
                if mat["mat_color4_r"] == (1.0) and mat["mat_color4_g"] == (1.0) and mat["mat_color4_b"] == (1.0):
                    color4 = mix_color4.inputs[0].links[0]
                    material.node_tree.links.remove(color4)
                if 'eyelash' in mat["mat_name"] and os.path.exists(os.path.join(filep, mat["mat_col0"][:-5] + textureextension)) == False:
                    material.node_tree.links.remove(principled_bsdf.inputs[0].links[0])
                    color_output.default_value = basecolor

    if loadlods == False:
        trmsh_count = 1
                        
    for w in range(trmsh_count):
        if os.path.exists(os.path.join(filep, trmsh_lods_array[w])):
            poly_group_array = []
            trmsh = open(os.path.join(filep, trmsh_lods_array[w]), "rb")
            trmsh_file_start = readlong(trmsh)
            print("Parsing TRMSH...")
            fseek(trmsh, trmsh_file_start)
            trmsh_struct = ftell(trmsh) - readlong(trmsh); fseek(trmsh, trmsh_struct)
            trmsh_struct_len = readshort(trmsh)

            if trmsh_struct_len != 0x000A:
                raise AssertionError("Unexpected TRMSH header struct length!")
            trmsh_struct_section_len = readshort(trmsh)
            trmsh_struct_start = readshort(trmsh)
            trmsh_struct_poly_group = readshort(trmsh)
            trmsh_struct_trmbf = readshort(trmsh)

            if trmsh_struct_trmbf != 0:
                fseek(trmsh, trmsh_file_start + trmsh_struct_trmbf)
                trmbf_filename_start = ftell(trmsh) + readlong(trmsh)
                fseek(trmsh, trmbf_filename_start)
                trmbf_filename_len = readlong(trmsh)
                trmbf_filename = readfixedstring(trmsh, trmbf_filename_len)
                print(trmbf_filename)

                trmbf = None
                if os.path.exists(os.path.join(filep, trmbf_filename)):
                    trmbf = open(os.path.join(filep, trmbf_filename), "rb")
                else:
                    raise AssertionError(f"Can't find {trmbf_filename}!")

                if trmbf != None:
                    print("Parsing TRMBF...")
                    trmbf_file_start = readlong(trmbf); fseek(trmbf, trmbf_file_start)
                    trmbf_struct = ftell(trmbf) - readlong(trmbf); fseek(trmbf, trmbf_struct)
                    trmbf_struct_len = readshort(trmbf)

                    if trmbf_struct_len != 0x0008:
                        raise AssertionError("Unexpected TRMBF header struct length!")
                    trmbf_struct_section_len = readshort(trmbf)
                    trmbf_struct_start = readshort(trmbf)
                    trmbf_struct_buffer = readshort(trmbf)

                    if trmsh_struct_poly_group != 0:
                        fseek(trmsh, trmsh_file_start + trmsh_struct_poly_group)
                        poly_group_start = ftell(trmsh) + readlong(trmsh)
                        fseek(trmsh, poly_group_start)
                        poly_group_count = readlong(trmsh)

                        fseek(trmbf, trmbf_file_start + trmbf_struct_buffer)
                        vert_buffer_start = ftell(trmbf) + readlong(trmbf)
                        vert_buffer_count = readlong(trmbf)

                        for x in range(poly_group_count):
                            vert_array = []
                            normal_array = []
                            color_array = []
                            alpha_array = []
                            uv_array = []
                            uv2_array = []
                            uv3_array = []
                            uv4_array = []
                            face_array = []
                            face_mat_id_array = []
                            b1_array = []
                            w1_array = []
                            weight_array = []
                            Morphs_array = []
                            MorphName_array = []
                            groupoffset_array = []
                            poly_group_name = ""; vis_group_name = ""; vert_buffer_stride = 0; mat_id = 0
                            positions_fmt = "None"; normals_fmt = "None"; tangents_fmt = "None"; bitangents_fmt = "None"; tritangents_fmt = "None"
                            uvs_fmt = "None"; uvs2_fmt = "None"; uvs3_fmt = "None"; uvs4_fmt = "None"
                            colors_fmt = "None"; colors2_fmt = "None"; bones_fmt = "None"; weights_fmt = "None"; svunk_fmt = "None"

                            poly_group_offset = ftell(trmsh) + readlong(trmsh)
                            poly_group_ret = ftell(trmsh)
                            fseek(trmsh, poly_group_offset)
                            print(f"PolyGroup offset #{x}: {hex(poly_group_offset)}")
                            poly_group_struct = ftell(trmsh) - readlong(trmsh)
                            fseek(trmsh, poly_group_struct)
                            poly_group_struct_len = readshort(trmsh)


                            if poly_group_struct_len == 0x001E:
                                poly_group_struct_section_len = readshort(trmsh)
                                poly_group_struct_ptr_poly_group_name = readshort(trmsh)
                                poly_group_struct_ptr_bbbox = readshort(trmsh)
                                poly_group_struct_ptp_unc_a = readshort(trmsh)
                                poly_group_struct_ptr_vert_buff = readshort(trmsh)
                                poly_group_struct_ptr_mat_list = readshort(trmsh)
                                poly_group_struct_ptr_unk_b = readshort(trmsh)
                                poly_group_struct_ptr_unk_c = readshort(trmsh)
                                poly_group_struct_ptr_unk_d = readshort(trmsh)
                                poly_group_struct_ptr_unk_e = readshort(trmsh)
                                poly_group_struct_ptr_unk_float = readshort(trmsh)
                                poly_group_struct_ptr_unk_g = readshort(trmsh)
                                poly_group_struct_ptr_morphname = readshort(trmsh)
                                poly_group_struct_ptr_vis_group_name = readshort(trmsh)
                                poly_group_struct_ptr_unk_i = 0
                                poly_group_struct_ptr_group_name = 0
                            elif poly_group_struct_len == 0x0022:
                                poly_group_struct_section_len = readshort(trmsh)
                                poly_group_struct_ptr_poly_group_name = readshort(trmsh)
                                poly_group_struct_ptr_bbbox = readshort(trmsh)
                                poly_group_struct_ptp_unc_a = readshort(trmsh)
                                poly_group_struct_ptr_vert_buff = readshort(trmsh)
                                poly_group_struct_ptr_mat_list = readshort(trmsh)
                                poly_group_struct_ptr_unk_b = readshort(trmsh)
                                poly_group_struct_ptr_unk_c = readshort(trmsh)
                                poly_group_struct_ptr_unk_d = readshort(trmsh)
                                poly_group_struct_ptr_unk_e = readshort(trmsh)
                                poly_group_struct_ptr_unk_float = readshort(trmsh)
                                poly_group_struct_ptr_unk_g = readshort(trmsh)
                                poly_group_struct_ptr_morphname = readshort (trmsh)
                                poly_group_struct_ptr_vis_group_name = readshort (trmsh)
                                poly_group_struct_ptr_unk_i = readshort(trmsh)
                                poly_group_struct_ptr_group_name = readshort(trmsh)

                            if poly_group_struct_ptr_mat_list != 0:
                                fseek(trmsh, poly_group_offset + poly_group_struct_ptr_mat_list)
                                mat_offset = ftell(trmsh) + readlong(trmsh)
                                fseek(trmsh, mat_offset)
                                mat_count = readlong(trmsh)
                                for y in range(mat_count):
                                    mat_entry_offset = ftell(trmsh) + readlong(trmsh)
                                    mat_ret = ftell(trmsh)
                                    fseek(trmsh, mat_entry_offset)
                                    mat_struct = ftell(trmsh) - readlong(trmsh)
                                    fseek(trmsh, mat_struct)
                                    mat_struct_len = readshort(trmsh)

                                    if mat_struct_len != 0x000E:
                                        raise AssertionError("Unexpected material struct length!")
                                    mat_struct_section_len = readshort(trmsh)
                                    mat_struct_ptr_facepoint_count = readshort(trmsh)
                                    mat_struct_ptr_facepoint_start = readshort(trmsh)
                                    mat_struct_ptr_unk_c = readshort(trmsh)
                                    mat_struct_ptr_string = readshort(trmsh)
                                    mat_struct_ptr_unk_d = readshort(trmsh)

                                    if mat_struct_ptr_facepoint_count != 0:
                                        fseek(trmsh, mat_entry_offset + mat_struct_ptr_facepoint_count)
                                        mat_facepoint_count = int(readlong(trmsh) / 3)

                                    if mat_struct_ptr_facepoint_start != 0:
                                        fseek(trmsh, mat_entry_offset + mat_struct_ptr_facepoint_start)
                                        mat_facepoint_start = int(readlong(trmsh) / 3)
                                    else: mat_facepoint_start = 0

                                    if mat_struct_ptr_unk_c != 0:
                                        fseek(trmsh, mat_entry_offset + mat_struct_ptr_unk_c)
                                        mat_unk_c = readlong(trmsh)

                                    if mat_struct_ptr_string != 0:
                                        fseek(trmsh, mat_entry_offset + mat_struct_ptr_string)
                                        mat_name_offset = ftell(trmsh) + readlong(trmsh)
                                        fseek(trmsh, mat_name_offset)
                                        mat_name_len = readlong(trmsh)
                                        mat_name = readfixedstring(trmsh, mat_name_len)

                                    if mat_struct_ptr_unk_d != 0:
                                        fseek(trmsh, mat_entry_offset + mat_struct_ptr_unk_d)
                                        mat_unk_d = readlong(trmsh)

                                    mat_id = 0
                                    for z in range(len(mat_data_array)):
                                        if mat_data_array[z]["mat_name"] == mat_name:
                                            mat_id = z
                                            break

                                    for z in range(mat_facepoint_count):
                                        face_mat_id_array.append(mat_id)

                                    print(f"Material {mat_name}: FaceCount = {mat_facepoint_count}, FaceStart = {mat_facepoint_start}")
                                    fseek(trmsh, mat_ret)

                            if poly_group_struct_ptr_poly_group_name != 0:
                                fseek(trmsh, poly_group_offset + poly_group_struct_ptr_poly_group_name)
                                poly_group_name_offset = ftell(trmsh) + readlong(trmsh); fseek(trmsh, poly_group_name_offset)
                                poly_group_name_len = readlong(trmsh)
                                poly_group_name = readfixedstring(trmsh, poly_group_name_len)
                                print(f"Building {poly_group_name}...")
                                
                            if poly_group_struct_ptr_group_name != 0:
                                fseek(trmsh, poly_group_offset + poly_group_struct_ptr_group_name)
                                group_name_header_offset = ftell(trmsh) + readlong(trmsh); fseek(trmsh, group_name_header_offset)
                                group_name_count = readlong(trmsh)
                                for g in range(group_name_count):
                                    group_name_offset = ftell(trmsh) + readlong(trmsh)
                                    groupoffset_array.append(group_name_offset)
                                    
                            if poly_group_struct_ptr_vis_group_name != 0:
                                fseek(trmsh, poly_group_offset + poly_group_struct_ptr_vis_group_name)
                                vis_group_name_offset = ftell(trmsh) + readlong(trmsh); fseek(trmsh, vis_group_name_offset)
                                vis_group_name_len = readlong(trmsh)
                                vis_group_name = readfixedstring(trmsh, vis_group_name_len)
                                # changed the output variable because the original seems to be a typo
                                print(f"VisGroup: {vis_group_name}")
                            if poly_group_struct_ptr_morphname !=0:
                                fseek(trmsh, poly_group_offset + poly_group_struct_ptr_morphname)
                                morph_name_header_offset = ftell(trmsh) + readlong(trmsh); fseek(trmsh, morph_name_header_offset)
                                morph_name_count = readlong(trmsh)
                                for m in range(morph_name_count):
                                    morph_name_header_offset = ftell (trmsh) + readlong (trmsh)
                                    morph_ret = ftell (trmsh)
                                    fseek (trmsh, morph_name_header_offset)
                                    morph_name_struct = ftell (trmsh) - readlong (trmsh)
                                    fseek (trmsh, morph_name_struct)
                                    morph_name_struct_len = readshort (trmsh)
                                    if morph_name_struct_len == 0x0008:
                                        morph_name_struct_section_len = readshort (trmsh)
                                        morph_name_struct_ptr_ID = readshort (trmsh)
                                        morph_name_struct_ptr_name = readshort (trmsh)
                                    else:
                                        raise AssertionError("Unexpected morph name struct length!")
                                    fseek (trmsh, morph_name_header_offset + morph_name_struct_ptr_ID)
                                    morph_name_ID = readlong (trmsh)
                                    fseek (trmsh, morph_name_header_offset + morph_name_struct_ptr_name)
                                    morph_name_start = ftell (trmsh) + readlong (trmsh)
                                    fseek (trmsh, morph_name_start)
                                    morph_name_len = readlong (trmsh)
                                    morph_name = readfixedstring (trmsh, morph_name_len)
                                    MorphName_array.append(morph_name)
                                    fseek (trmsh, morph_ret)
                            if poly_group_struct_ptr_vert_buff != 0:
                                fseek(trmsh, poly_group_offset + poly_group_struct_ptr_vert_buff)
                                poly_group_vert_buff_offset = ftell(trmsh) + readlong(trmsh)
                                fseek(trmsh, poly_group_vert_buff_offset)
                                vert_buff_count = readlong(trmsh)
                                vert_buff_offset = ftell(trmsh) + readlong(trmsh)
                                fseek(trmsh, vert_buff_offset)
                                vert_buff_struct = ftell(trmsh) - readlong(trmsh)
                                fseek(trmsh, vert_buff_struct)
                                vert_buff_struct_len = readshort(trmsh)

                                if vert_buff_struct_len != 0x0008:
                                    raise AssertionError("Unexpected VertexBuffer struct length!")
                                vert_buff_struct_section_len = readshort(trmsh)
                                vert_buff_struct_ptr_param = readshort(trmsh)
                                vert_buff_struct_ptr_b = readshort(trmsh)

                                if vert_buff_struct_ptr_param != 0:
                                    fseek(trmsh, vert_buff_offset + vert_buff_struct_ptr_param)
                                    vert_buff_param_offset = ftell(trmsh) + readlong(trmsh)
                                    fseek(trmsh, vert_buff_param_offset)
                                    vert_buff_param_count = readlong(trmsh)
                                    for y in range(vert_buff_param_count):
                                        vert_buff_param_offset = ftell(trmsh) + readlong(trmsh)
                                        vert_buff_param_ret = ftell(trmsh)
                                        fseek(trmsh, vert_buff_param_offset)
                                        vert_buff_param_struct = ftell(trmsh) - readlong(trmsh)
                                        fseek(trmsh, vert_buff_param_struct)
                                        vert_buff_param_struct_len = readshort(trmsh)

                                        if vert_buff_param_struct_len == 0x000C:
                                            vert_buff_param_struct_section_len = readshort(trmsh)
                                            vert_buff_param_ptr_unk_a = readshort(trmsh)
                                            vert_buff_param_ptr_type = readshort(trmsh)
                                            vert_buff_param_ptr_layer = readshort(trmsh)
                                            vert_buff_param_ptr_fmt = readshort(trmsh)
                                            vert_buff_param_ptr_position = 0
                                        elif vert_buff_param_struct_len == 0x000E:
                                            vert_buff_param_struct_section_len = readshort(trmsh)
                                            vert_buff_param_ptr_unk_a = readshort(trmsh)
                                            vert_buff_param_ptr_type = readshort(trmsh)
                                            vert_buff_param_ptr_layer = readshort(trmsh)
                                            vert_buff_param_ptr_fmt = readshort(trmsh)
                                            vert_buff_param_ptr_position = readshort(trmsh)
                                        else:
                                            raise AssertionError("Unknown vertex buffer parameter struct length!")

                                        vert_buff_param_layer = 0

                                        if vert_buff_param_ptr_type != 0:
                                            fseek(trmsh, vert_buff_param_offset + vert_buff_param_ptr_type)
                                            vert_buff_param_type = readlong(trmsh)
                                        if vert_buff_param_ptr_layer != 0:
                                            fseek(trmsh, vert_buff_param_offset + vert_buff_param_ptr_layer)
                                            vert_buff_param_layer = readlong(trmsh)
                                        if vert_buff_param_ptr_fmt != 0:
                                            fseek(trmsh, vert_buff_param_offset + vert_buff_param_ptr_fmt)
                                            vert_buff_param_format = readlong(trmsh)
                                        if vert_buff_param_ptr_position != 0:
                                            fseek(trmsh, vert_buff_param_offset + vert_buff_param_ptr_position)
                                            vert_buff_param_position = readlong(trmsh)
                                        else:
                                            vert_buff_param_position = 0

                                        # -- Types:
                                        # -- 0x01: = Positions
                                        # -- 0x02 = Normals
                                        # -- 0x03 = Tangents
                                        # -- 0x05 = Colors
                                        # -- 0x06 = UVs
                                        # -- 0x07 = NodeIDs
                                        # -- 0x08 = Weights
                                        #
                                        # -- Formats:
                                        # -- 0x14 = 4 bytes as float
                                        # -- 0x16 = 4 bytes
                                        # -- 0x27 = 4 shorts as float
                                        # -- 0x2B = 4 half-floats
                                        # -- 0x30 = 2 floats
                                        # -- 0x33 = 3 floats
                                        # -- 0x36 = 4 floats
                                        print(f'vert_buff_param_type = {vert_buff_param_type}')
                                        if vert_buff_param_type == 0x01:
                                            if vert_buff_param_layer != 0:
                                                raise AssertionError("Unexpected positions layer!")

                                            if vert_buff_param_format != 0x33:
                                                raise AssertionError("Unexpected positions format!")

                                            positions_fmt = "3Floats"; vert_buffer_stride = vert_buffer_stride + 0x0C
                                        elif vert_buff_param_type == 0x02:
                                            if vert_buff_param_layer != 0:
                                                raise AssertionError("Unexpected normals layer!")

                                            if vert_buff_param_format != 0x2B:
                                                raise AssertionError("Unexpected normals format!")

                                            normals_fmt = "4HalfFloats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                        elif vert_buff_param_type == 0x03:
                                            if vert_buff_param_layer == 0:
                                                if vert_buff_param_format != 0x2B:
                                                    raise AssertionError("Unexpected tangents format!")

                                                tangents_fmt = "4HalfFloats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                            elif vert_buff_param_layer == 1:
                                                if vert_buff_param_format != 0x2B:
                                                    raise AssertionError("Unexpected bitangents format!")

                                                bitangents_fmt = "4HalfFloats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                            elif vert_buff_param_layer == 2:
                                                if vert_buff_param_format != 0x2B:
                                                    raise AssertionError("Unexpected tritangents format!")

                                                tritangents_fmt = "4HalfFloats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                            else:
                                                raise AssertionError("Unexpected tangents layer!")
                                                
                                                
                                                
                                        
                                        elif vert_buff_param_type == 0x05:
                                            print(f'vert_buff_param_layer = {vert_buff_param_layer}')
                                            if vert_buff_param_layer == 0:
                                                print("bufflayer0 confirmed")
                                                if vert_buff_param_format == 0x14:
                                                    print("vert_buff_param_format0x14 confirmed")
                                                    colors_fmt = "4BytesAsFloat"; vert_buffer_stride = vert_buffer_stride + 0x04
                                                elif vert_buff_param_format == 0x16:
                                                    colors_fmt = "4Bytes"; vert_buffer_stride = vert_buffer_stride + 0x04
                                                elif vert_buff_param_format == 0x36:
                                                    print("vert_buff_param_format0x36 confirmed")
                                                    colors_fmt = "4Floats"; vert_buffer_stride = vert_buffer_stride + 0x10
                                                else:
                                                    raise AssertionError(hex(vert_buff_param_format))
                                            elif vert_buff_param_layer == 1:
                                                if vert_buff_param_format == 0x14:
                                                    colors2_fmt = "4BytesAsFloat"; vert_buffer_stride = vert_buffer_stride + 0x04
                                                elif vert_buff_param_format == 0x16:
                                                    colors_fmt = "4Bytes"; vert_buffer_stride = vert_buffer_stride + 0x04
                                                elif vert_buff_param_format == 0x36:
                                                    colors2_fmt = "4Floats"; vert_buffer_stride = vert_buffer_stride + 0x10
                                                else:
                                                    raise AssertionError("Unexpected colors2 format!")
                                                    
                                                    

                                        elif vert_buff_param_type == 0x06:
                                            if vert_buff_param_layer == 0:
                                                if vert_buff_param_format != 0x30:
                                                    raise AssertionError("Unexpected UVs format!")

                                                uvs_fmt = "2Floats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                            elif vert_buff_param_layer == 1:
                                                if vert_buff_param_format != 0x30:
                                                    raise AssertionError("Unexpected UVs2 format!")

                                                uvs2_fmt = "2Floats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                            elif vert_buff_param_layer == 2:
                                                if vert_buff_param_format != 0x30:
                                                    raise AssertionError("Unexpected UVs3 format!")

                                                uvs3_fmt = "2Floats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                            elif vert_buff_param_layer == 3:
                                                if vert_buff_param_format != 0x30:
                                                    raise AssertionError("Unexpected UVs4 format!")

                                                uvs4_fmt = "2Floats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                            else:
                                                raise AssertionError("Unexpected UVs layer!")
                                        elif vert_buff_param_type == 0x07:
                                            if vert_buff_param_layer != 0:
                                                raise AssertionError("Unexpected node IDs layer!")

                                            if vert_buff_param_format != 0x16:
                                                raise AssertionError("Unexpected node IDs format!")

                                            bones_fmt = "4Bytes"; vert_buffer_stride = vert_buffer_stride + 0x04
                                        elif vert_buff_param_type == 0x08:
                                            if vert_buff_param_layer != 0:
                                                raise AssertionError("Unexpected weights layer!")

                                            ##if vert_buff_param_format != 0x27:
                                            ##    raise AssertionError("Unexpected weights format!")
                                            if vert_buff_param_format == 0x16:
                                                weights_fmt = "4Bytes"; vert_buffer_stride = vert_buffer_stride + 0x04
                                            else:
                                                weights_fmt = "4ShortsAsFloat"; vert_buffer_stride = vert_buffer_stride + 0x08
                                        elif vert_buff_param_type == 0x09:
                                            if vert_buff_param_layer != 0:
                                                raise AssertionError("Unexpected ?????? layer!")

                                            if vert_buff_param_format != 0x24:
                                                raise AssertionError("Unexpected ?????? layer!")

                                            svunk_fmt = "1Long?"; vert_buffer_stride = vert_buffer_stride + 0x04
                                        else:
                                            raise AssertionError("Unknown vertex type!")


                                        fseek(trmsh, vert_buff_param_ret)

                            poly_group_array.append(
                                {
                                    "poly_group_name": poly_group_name,
                                    "vis_group_name": vis_group_name,
                                    "vert_buffer_stride": vert_buffer_stride,
                                    "positions_fmt": positions_fmt,
                                    "normals_fmt": normals_fmt,
                                    "tangents_fmt": tangents_fmt,
                                    "bitangents_fmt": bitangents_fmt,
                                    "tritangents_fmt":tritangents_fmt,
                                    "uvs_fmt": uvs_fmt,
                                    "uvs2_fmt": uvs2_fmt,
                                    "uvs3_fmt": uvs3_fmt,
                                    "uvs4_fmt": uvs4_fmt,
                                    "colors_fmt": colors_fmt,
                                    "colors2_fmt": colors2_fmt,
                                    "bones_fmt": bones_fmt,
                                    "weights_fmt": weights_fmt,
                                    "svunk_fmt":svunk_fmt
                                }
                            )
                            fseek(trmsh, poly_group_ret)

                            vert_buffer_offset = ftell(trmbf) + readlong(trmbf)
                            vert_buffer_ret = ftell(trmbf)
                            fseek(trmbf, vert_buffer_offset)
                            vert_buffer_struct = ftell(trmbf) - readlong(trmbf); fseek(trmbf, vert_buffer_struct)
                            vert_buffer_struct_len = readshort(trmbf)
                            print(hex(vert_buffer_struct_len))
                            if vert_buffer_struct_len == 0x0008:
                                vert_buffer_struct_section_length = readshort(trmbf)
                                vert_buffer_struct_ptr_faces = readshort(trmbf)
                                vert_buffer_struct_ptr_verts = readshort(trmbf)
                                vert_buffer_struct_ptr_groups = 0
                            elif vert_buffer_struct_len == 0x000A:
                                vert_buffer_struct_section_length = readshort(trmbf)
                                vert_buffer_struct_ptr_faces = readshort(trmbf)
                                vert_buffer_struct_ptr_verts = readshort(trmbf)
                                vert_buffer_struct_ptr_groups = readshort(trmbf)
                            else:
                                raise AssertionError("Unexpected vertex buffer struct length!")

                            if vert_buffer_struct_ptr_verts != 0:
                                fseek(trmbf, vert_buffer_offset + vert_buffer_struct_ptr_verts)
                                vert_buffer_sub_start = ftell(trmbf) + readlong(trmbf); fseek(trmbf, vert_buffer_sub_start)
                                vert_buffer_sub_count = readlong(trmbf)

                                for y in range(vert_buffer_sub_count):
                                    vert_buffer_sub_offset = ftell(trmbf) + readlong(trmbf)
                                    vert_buffer_sub_ret = ftell(trmbf)
                                    fseek(trmbf, vert_buffer_sub_offset)
                                    if y == 0:
                                        print(f"Vertex buffer {x} header: {hex(ftell(trmbf))}")
                                    else:
                                        print(f"Vertex buffer {x} morph {y} header: {hex(ftell(trmbf))}")
                                    vert_buffer_sub_struct = ftell(trmbf) - readlong(trmbf); fseek(trmbf, vert_buffer_sub_struct)
                                    vert_buffer_sub_struct_len = readshort(trmbf)

                                    if vert_buffer_sub_struct_len != 0x0006:
                                        raise AssertionError("Unexpected vertex buffer struct length!")
                                    vert_buffer_sub_struct_section_length = readshort(trmbf)
                                    vert_buffer_sub_struct_ptr = readshort(trmbf)

                                    if vert_buffer_sub_struct_ptr != 0:
                                        fseek(trmbf, vert_buffer_sub_offset + vert_buffer_sub_struct_ptr)
                                        vert_buffer_start = ftell(trmbf) + readlong(trmbf); fseek(trmbf, vert_buffer_start)
                                        vert_buffer_byte_count = readlong(trmbf)
                                        if y == 0:
                                            print(f"Vertex buffer {x} start: {hex(ftell(trmbf))}")

                                            for v in range(vert_buffer_byte_count // poly_group_array[x]["vert_buffer_stride"]):
                                                if poly_group_array[x]["positions_fmt"] == "4HalfFloats":
                                                    vx = readhalffloat(trmbf)
                                                    vy = readhalffloat(trmbf)
                                                    vz = readhalffloat(trmbf)
                                                    vq = readhalffloat(trmbf)
                                                elif poly_group_array[x]["positions_fmt"] == "3Floats":
                                                    vx = readfloat(trmbf)
                                                    vy = readfloat(trmbf)
                                                    vz = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown positions type!")

                                                if poly_group_array[x]["normals_fmt"] == "4HalfFloats":
                                                    nx = readhalffloat(trmbf)
                                                    ny = readhalffloat(trmbf)
                                                    nz = readhalffloat(trmbf)
                                                    nq = readhalffloat(trmbf)
                                                elif poly_group_array[x]["normals_fmt"] == "3Floats":
                                                    nx = readfloat(trmbf)
                                                    ny = readfloat(trmbf)
                                                    nz = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown normals type!")

                                                if poly_group_array[x]["tangents_fmt"] == "None":
                                                    pass
                                                elif poly_group_array[x]["tangents_fmt"] == "4HalfFloats":
                                                    tanx = readhalffloat(trmbf)
                                                    tany = readhalffloat(trmbf)
                                                    tanz = readhalffloat(trmbf)
                                                    tanq = readhalffloat(trmbf)
                                                elif poly_group_array[x]["tangents_fmt"] == "3Floats":
                                                    tanx = readfloat(trmbf)
                                                    tany = readfloat(trmbf)
                                                    tanz = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown tangents type!")

                                                if poly_group_array[x]["bitangents_fmt"] == "None":
                                                    pass
                                                elif poly_group_array[x]["bitangents_fmt"] == "4HalfFloats":
                                                    bitanx = readhalffloat(trmbf)
                                                    bitany = readhalffloat(trmbf)
                                                    bitanz = readhalffloat(trmbf)
                                                    bitanq = readhalffloat(trmbf)
                                                elif poly_group_array[x]["bitangents_fmt"] == "3Floats":
                                                    bitanx = readfloat(trmbf)
                                                    bitany = readfloat(trmbf)
                                                    bitanz = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown bitangents type!")

                                                if poly_group_array[x]["tritangents_fmt"] == "None":
                                                    pass
                                                elif poly_group_array[x]["tritangents_fmt"] == "4HalfFloats":
                                                    tritanx = readhalffloat(trmbf)
                                                    tritany = readhalffloat(trmbf)
                                                    tritanz = readhalffloat(trmbf)
                                                    tritanq = readhalffloat(trmbf)
                                                elif poly_group_array[x]["tritangents_fmt"] == "3Floats":
                                                    tritanx = readfloat(trmbf)
                                                    tritany = readfloat(trmbf)
                                                    tritanz = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown bitangents type!")

                                                if poly_group_array[x]["uvs_fmt"] == "None":
                                                    tu = 0
                                                    tv = 0
                                                elif poly_group_array[x]["uvs_fmt"] == "2Floats":
                                                    tu = readfloat(trmbf)
                                                    tv = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown uvs type!")

                                                if poly_group_array[x]["uvs2_fmt"] == "None":
                                                    pass
                                                elif poly_group_array[x]["uvs2_fmt"] == "2Floats":
                                                    tu2 = readfloat(trmbf)
                                                    tv2 = readfloat(trmbf)
                                                    uv2_array.append((tu2, tv2))
                                                else:
                                                    raise AssertionError("Unknown uvs2 type!")

                                                if poly_group_array[x]["uvs3_fmt"] == "None":
                                                    pass
                                                elif poly_group_array[x]["uvs3_fmt"] == "2Floats":
                                                    tu3 = readfloat(trmbf)
                                                    tv3 = readfloat(trmbf)
                                                    uv3_array.append((tu3, tv3))
                                                else:
                                                    raise AssertionError("Unknown uvs3 type!")

                                                if poly_group_array[x]["uvs4_fmt"] == "None":
                                                    pass
                                                elif poly_group_array[x]["uvs4_fmt"] == "2Floats":
                                                    tu4 = readfloat(trmbf)
                                                    tv4 = readfloat(trmbf)
                                                    uv4_array.append((tu4, tv4))
                                                else:
                                                    raise AssertionError("Unknown uvs4 type!")

                                                if poly_group_array[x]["colors_fmt"] == "None":
                                                    colorr = 255
                                                    colorg = 255
                                                    colorb = 255
                                                    colora = 1
                                                elif poly_group_array[x]["colors_fmt"] == "4BytesAsFloat":
                                                    colorr = readbyte(trmbf)
                                                    colorg = readbyte(trmbf)
                                                    colorb = readbyte(trmbf)
                                                    colora = readbyte(trmbf)
                                                elif poly_group_array[x]["colors_fmt"] == "4Floats":
                                                    colorr = readfloat(trmbf) * 255
                                                    colorg = readfloat(trmbf) * 255
                                                    colorb = readfloat(trmbf) * 255
                                                    colora = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown colors type!")

                                                if poly_group_array[x]["colors2_fmt"] == "None":
                                                    colorr2 = 255
                                                    colorg2 = 255
                                                    colorb2 = 255
                                                    colora2 = 1
                                                elif poly_group_array[x]["colors2_fmt"] == "4BytesAsFloat":
                                                    colorr2 = readbyte(trmbf)
                                                    colorg2 = readbyte(trmbf)
                                                    colorb2 = readbyte(trmbf)
                                                    colora2 = readbyte(trmbf)
                                                elif poly_group_array[x]["colors2_fmt"] == "4Floats":
                                                    colorr2 = readfloat(trmbf) * 255
                                                    colorg2 = readfloat(trmbf) * 255
                                                    colorb2 = readfloat(trmbf) * 255
                                                    colora2 = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown colors 2 type!")

                                                if poly_group_array[x]["bones_fmt"] == "None":
                                                    bone1 = 0
                                                    bone2 = 0
                                                    bone3 = 0
                                                    bone4 = 0
                                                elif poly_group_array[x]["bones_fmt"] == "4Bytes":
                                                    bone1 = readbyte(trmbf)
                                                    bone2 = readbyte(trmbf)
                                                    bone3 = readbyte(trmbf)
                                                    bone4 = readbyte(trmbf)
                                                else:
                                                    raise AssertionError("Unknown bones type!")

                                                if poly_group_array[x]["weights_fmt"] == "None":
                                                    weight1 = 0
                                                    weight2 = 0
                                                    weight3 = 0
                                                    weight4 = 0
                                                elif poly_group_array[x]["weights_fmt"] == "4ShortsAsFloat":
                                                    weight1 = readshort(trmbf) / 65535
                                                    weight2 = readshort(trmbf) / 65535
                                                    weight3 = readshort(trmbf) / 65535
                                                    weight4 = readshort(trmbf) / 65535
                                                else:
                                                    raise AssertionError("Unknown weights type!")
                                                
                                                if poly_group_array[x]["svunk_fmt"] == "None":
                                                    SVUnk = 0
                                                elif poly_group_array[x]["svunk_fmt"] == "1Long?":
                                                    SVUnk = readlong(trmbf)
                                                else:
                                                    raise AssertionError("Unknown ?????? type!")
                                                
                                                vert_array.append((vx, vy, vz))
                                                normal_array.append((nx, ny, nz))
                                                
                                                
                                                uv_array.append((tu, tv))
                                                
                                                color_array.append((colorr, colorg, colorb))
                                                alpha_array.append(colora)
                                                if trskl is not None:
                                                    w1_array.append({"weight1": weight1, "weight2": weight2, "weight3": weight3, "weight4": weight4})
                                                    b1_array.append({"bone1": bone1, "bone2": bone2, "bone3": bone3, "bone4": bone4})

                                            print(f"Vertex buffer {x} end: {hex(ftell(trmbf))}")
                                        else:
                                            print(f"Vertex buffer {x} morph {y} start: {hex(ftell(trmbf))}")
                                            MorphVert_array = []
                                            MorphNormal_array = []
                                            for v in range(int(vert_buffer_byte_count / 0x1C)):
                                                #Morphs always seem to use this setup.
                                                vx = readfloat(trmbf)
                                                vy = readfloat(trmbf)
                                                vz = readfloat(trmbf)
                                                nx = readhalffloat(trmbf)
                                                ny = readhalffloat(trmbf)
                                                nz = readhalffloat(trmbf)
                                                nq = readhalffloat(trmbf)
                                                tanx = readhalffloat(trmbf)
                                                tany = readhalffloat(trmbf)
                                                tanz = readhalffloat(trmbf)
                                                tanq = readhalffloat(trmbf)
                                                MorphVert_array.append((vx, vy, vz))
                                                MorphNormal_array.append((nx, ny, nz))
                                            print(f"Vertex buffer {x} morph {y} end: {hex(ftell(trmbf))}")
                                            Morphs_array.append(MorphVert_array)
                                            #TODO: Continue implementing after line 3814
                                    fseek(trmbf,vert_buffer_sub_ret)

                            if vert_buffer_struct_ptr_faces != 0:
                                fseek(trmbf, vert_buffer_offset + vert_buffer_struct_ptr_faces)
                                face_buffer_start = ftell(trmbf) + readlong(trmbf); fseek(trmbf, face_buffer_start)
                                face_buffer_count = readlong(trmbf)

                                for y in range(face_buffer_count):
                                    face_buff_offset = ftell(trmbf) + readlong(trmbf)
                                    face_buff_ret = ftell(trmbf)
                                    fseek(trmbf, face_buff_offset)
                                    print(f"Facepoint {x} header: {hex(ftell(trmbf))}")
                                    face_buff_struct = ftell(trmbf) - readlong(trmbf); fseek(trmbf, face_buff_struct)
                                    face_buff_struct_len = readshort(trmbf)

                                    if face_buff_struct_len != 0x0006:
                                        raise AssertionError("Unexpected face buffer struct length!")
                                    face_buffer_struct_section_length = readshort(trmbf)
                                    face_buffer_struct_ptr = readshort(trmbf)

                                    if face_buffer_struct_ptr != 0:
                                        fseek(trmbf, face_buff_offset + face_buffer_struct_ptr)
                                        facepoint_start = ftell(trmbf) + readlong(trmbf); fseek(trmbf, facepoint_start)
                                        facepoint_byte_count = readlong(trmbf)
                                        print(f"Facepoint {x} start: {hex(ftell(trmbf))}")
                                        
                                        if len(vert_array) > 65536: # is this a typo? I would imagine it to be 65535
                                            for v in range(facepoint_byte_count // 12):
                                                fa = readlong(trmbf)
                                                fb = readlong(trmbf)
                                                fc = readlong(trmbf)
                                                face_array.append([fa, fb, fc])
                                        else:
                                            for v in range(facepoint_byte_count // 6):
                                                fa = readshort(trmbf)
                                                fb = readshort(trmbf)
                                                fc = readshort(trmbf)
                                                face_array.append([fa, fb, fc])
                                        print(f"Facepoint {x} end: {hex(ftell(trmbf))}")
                                    fseek(trmbf, face_buff_ret)

                            if vert_buffer_struct_ptr_groups != 0:
                                fseek(trmbf, vert_buffer_offset + vert_buffer_struct_ptr_groups)
                                group_start = ftell(trmbf) + readlong(trmbf); fseek(trmbf, group_start)
                                group_count = readlong(trmbf)
                                if group_count > 0:
                                    MorphNameNext = 1
                                    for g in range(group_count):
                                        fseek(trmsh, groupoffset_array[g])
                                        group_namestruct = ftell(trmsh) - readlong(trmsh)
                                        fseek(trmsh, group_namestruct)
                                        groupnamestructlen = readshort(trmsh)
                                        if groupnamestructlen == 0x000A:
                                            group_structsectionlen = readshort(trmsh)
                                            group_structptrparama = readshort(trmsh)
                                            group_structptrparammorph = readshort(trmsh)
                                            group_structprtparamname = readshort(trmsh)
                                        else:
                                            raise AssertionError("Unexpected morph group buffer struct length!")
                                        
                                        fseek(trmsh, groupoffset_array[g] + group_structprtparamname)
                                        group_nameoffset = ftell(trmsh) + readlong(trmsh)
                                        fseek(trmsh, group_nameoffset)
                                        group_namelen = readlong(trmsh)
                                        group_name = readfixedstring(trmsh, group_namelen)
                                        
                                        
                                        fseek(trmsh, groupoffset_array[g] + group_structptrparammorph)
                                        group_morphoffset = ftell(trmsh) + readlong(trmsh)
                                        fseek(trmsh, group_morphoffset)
                                        group_morphnamecount = readlong(trmsh)
                                        for y in range(group_morphnamecount):
                                            group_morphnameoffset = ftell(trmsh) + readlong(trmsh)
                                            group_morhpnameret = ftell(trmsh)
                                            fseek(trmsh, group_morphnameoffset)
                                            
                                            group_namemorphstruct = ftell(trmsh) - readlong(trmsh)
                                            fseek(trmsh, group_namemorphstruct)
                                            group_namemorphstructlen = readshort(trmsh)
                                            if group_namemorphstructlen == 0x000A:
                                                group_namemorphstructsectionlen = readshort(trmsh)
                                                group_namemorphstructptrparamid = readshort(trmsh)
                                                group_namemorphstructptrparamname = readshort(trmsh)
                                                group_namemorphstructptrparamflag = readshort(trmsh)
                                            else:
                                                raise AssertionError("Unexpected morph group buffer struct length!")
                                            fseek(trmsh, group_morphnameoffset + group_namemorphstructptrparamname)
                                            group_morphnameoffset = ftell(trmsh) + readlong(trmsh)
                                            fseek(trmsh, group_morphnameoffset)
                                            group_morphnamelen = readlong(trmsh)
                                            group_morphname = readfixedstring(trmsh, group_morphnamelen)
                                            MorphName_array.append(group_morphname)
                                            fseek(trmsh, group_morhpnameret)
                                        
                                        MorphVertIDs_array = []
                                        group_offset = ftell(trmbf) + readlong(trmbf)
                                        group_ret = ftell(trmbf)
                                        fseek(trmbf, group_offset)
                                        group_struct = ftell(trmbf) - readlong(trmbf)
                                        fseek(trmbf, group_struct)
                                        group_structlen = readshort(trmbf)
                                        if group_structlen == 0x0006:
                                            group_structsectionlen = readshort(trmbf)
                                            group_structptrparam = readshort(trmbf)
                                        else:
                                            raise AssertionError("Unexpected morph group buffer struct lenght!")
                                        
                                        fseek(trmbf, group_offset + group_structptrparam)
                                        group_morphsoffset = ftell(trmbf) + readlong(trmbf)
                                        fseek(trmbf, group_morphsoffset)
                                        group_morphscount = readlong(trmbf)
                                        print(f"Group {x} header start: {group_morphsoffset}")
                                        
                                        for y in range(group_morphscount):
                                            morphgroupoffset = ftell(trmbf) + readlong(trmbf)
                                            groupret = ftell(trmbf)
                                            fseek(trmbf, morphgroupoffset)
                                            print(f"Group morph {y} start: {ftell(trmbf)}")
                                            bufferstruct = ftell(trmbf) - readlong(trmbf)
                                            fseek(trmbf, bufferstruct)
                                            morphbufferstructlen = readshort(trmbf)
                                            if morphbufferstructlen == 0x0006:
                                                morphbuffersectionlen = readshort(trmbf)
                                                morphbufferstructptrparam = readshort(trmbf)
                                            else:
                                                raise AssertionError("Unexpected group sub buffer struct lenght!")
                                            
                                            fseek(trmbf, morphgroupoffset + morphbufferstructptrparam)
                                            morphbuffergroupsuboffset = ftell(trmbf) + readlong(trmbf)
                                            morphbuffergroupsbytecount = readlong(trmbf)
                                            if y == 0:
                                                for v in range(morphbuffergroupsbytecount // 0x04):
                                                    MorphVertID = readlong(trmbf)
                                                    MorphVertIDs_array.append(MorphVertID)
                                            else:
                                                MorphVert_array = []
                                                MorphNormal_array = []
                                                for v in range(len(vert_array)):
                                                    MorphVert_array.append(vert_array[v])
                                                    MorphNormal_array.append(normal_array[v])
                                                for v in range(morphbuffergroupsbytecount // 0x1C):
                                                    #Morphs always seem to use this setup.
                                                    vx = readfloat(trmbf)
                                                    vy = readfloat(trmbf)
                                                    vz = readfloat(trmbf)
                                                    nx = readhalffloat(trmbf)
                                                    ny = readhalffloat(trmbf)
                                                    nz = readhalffloat(trmbf)
                                                    nq = readhalffloat(trmbf)
                                                    tanx = readhalffloat(trmbf)
                                                    tany = readhalffloat(trmbf)
                                                    tanz = readhalffloat(trmbf)
                                                    tanq = readhalffloat(trmbf)
                                                    if MorphVertIDs_array[v] != 0:
                                                        MorphVert_array[MorphVertIDs_array[v]] = [vert_array[MorphVertIDs_array[v]][0] + vx, vert_array[MorphVertIDs_array[v]][1] + vy, vert_array[MorphVertIDs_array[v]][2] + vz]
                                                        MorphNormal_array[MorphVertIDs_array[v]] = [vert_array[MorphVertIDs_array[v]][0] + nx, vert_array[MorphVertIDs_array[v]][1] + ny, vert_array[MorphVertIDs_array[v]][2] + nz]
                                                print(f"Group {x} morph {y} end: {hex(ftell(trmbf))}")
                                                Morphs_array.append(MorphVert_array)
                                            fseek(trmbf, groupret)
                                        fseek(trmbf, group_ret)
                            fseek(trmbf, vert_buffer_ret)                                                          

                            print("Making object...")

                            for b in range(len(w1_array)):
                                w = {"boneids": [], "weights": []}
                                maxweight = w1_array[b]["weight1"] +\
                                            w1_array[b]["weight2"] +\
                                            w1_array[b]["weight3"] +\
                                            w1_array[b]["weight4"]

                                if maxweight > 0:
                                    if (w1_array[b]["weight1"] > 0):
                                        w["boneids"].append(b1_array[b]["bone1"])
                                        w["weights"].append(w1_array[b]["weight1"])
                                    if (w1_array[b]["weight2"] > 0):
                                        w["boneids"].append(b1_array[b]["bone2"])
                                        w["weights"].append(w1_array[b]["weight2"])
                                    if (w1_array[b]["weight3"] > 0):
                                        w["boneids"].append(b1_array[b]["bone3"])
                                        w["weights"].append(w1_array[b]["weight3"])
                                    if (w1_array[b]["weight4"] > 0):
                                        w["boneids"].append(b1_array[b]["bone4"])
                                        w["weights"].append(w1_array[b]["weight4"])

                                weight_array.append(w)

                            if IN_BLENDER_ENV:
                                # LINE 3257

                                new_mesh = bpy.data.meshes.new(f"{poly_group_name}_mesh")
                                new_mesh.from_pydata(vert_array, [], face_array)
                                new_mesh.update()
                                for p in new_mesh.polygons:
                                    p.use_smooth = True
                                new_object = bpy.data.objects.new(poly_group_name, new_mesh)
                                if len(MorphName_array) > 0:
                                    sk_basis = new_object.shape_key_add(name='Basis')
                                    sk_basis.interpolation = 'KEY_LINEAR'
                                    new_object.data.shape_keys.use_relative = True
                                    print(MorphName_array)
                                    for m in range(len(MorphName_array)):
                                        sk = new_object.shape_key_add(name=MorphName_array[m])
                                        for i in range(len(Morphs_array[m])):
                                            sk.data[i].co = Morphs_array[m][i]

                                if bone_structure != None:
                                    new_object.parent = bone_structure
                                    new_object.modifiers.new(name='Skeleton', type='ARMATURE')
                                    new_object.modifiers['Skeleton'].object = bone_structure

                                    for face in new_object.data.polygons:
                                        for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                                            w = weight_array[vert_idx]
                                            for i in range(len(w["boneids"])):
                                                try:
                                                    bone_id = bone_id_map[w['boneids'][i]]
                                                except:
                                                    bone_id = None
                                                if bone_id:
                                                    weight = w['weights'][i]

                                                    group = None
                                                    if new_object.vertex_groups.get(bone_id) == None:
                                                        group = new_object.vertex_groups.new(name=bone_id)
                                                    else:
                                                        group = new_object.vertex_groups[bone_id]

                                                    group.add([vert_idx], weight, 'REPLACE')

                                # # vertex colours
                                color_layer = new_object.data.vertex_colors.new(name="Color")
                                new_object.data.vertex_colors.active = color_layer
                                #print(f"color_array: {len(color_array)}")
                                #print(f"polygons: {len(new_object.data.polygons)}")
                                for i, poly in enumerate(new_object.data.polygons):
                                    #print(f"poly: {i}")
                                    for v, vert in enumerate(poly.vertices):
                                        loop_index = poly.loop_indices[v]
                                
                                        #print(f"loop_index: {loop_index}")
                                        #print(color_array[vert][0], color_array[vert][1], color_array[vert][2], alpha_array[vert])
                                        
                                        if alpha_array[vert] == 0:
                                            alpha_array[vert] = 1
                                        color_layer.data[loop_index].color = (color_array[vert][0] / alpha_array[vert], color_array[vert][1] / alpha_array[vert], color_array[vert][2] / alpha_array[vert], alpha_array[vert])

                                for mat in materials:
                                    new_object.data.materials.append(mat)

                                # materials

                                # uvs
                                uv_layers = new_object.data.uv_layers
                                uv_layer = uv_layers.new(name="UVMap")
                                if len(uv2_array) > 0:
                                    uv2_layer = uv_layers.new(name="UV2Map")
                                if len(uv3_array) > 0:
                                    uv3_layer = uv_layers.new(name="UV3Map")
                                if len(uv4_array) > 0:
                                    uv4_layer = uv_layers.new(name="UV4Map")
                                uv_layers.active = uv_layer




                                for i, poly in enumerate(new_object.data.polygons):
                                    poly.material_index = face_mat_id_array[i]


                                for face in new_object.data.polygons:
                                    for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                                        uv_layer.data[loop_idx].uv = uv_array[vert_idx]
                                        if len(uv2_array) > 0:
                                            uv2_layer.data[loop_idx].uv = uv2_array[vert_idx]
                                        if len(uv3_array) > 0:
                                            uv3_layer.data[loop_idx].uv = uv3_array[vert_idx]
                                        if len(uv4_array) > 0:
                                            uv4_layer.data[loop_idx].uv = uv4_array[vert_idx]

                                #normals
                                new_object.data.use_auto_smooth = True
                                new_object.data.normals_split_custom_set_from_vertices(normal_array)
                                # add object to scene collection
                                new_collection.objects.link(new_object)


class PokeArcImport(bpy.types.Operator, ImportHelper):
    bl_idname = "custom_import_scene.pokemonlegendsarceus"
    bl_label = "Import"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".trmdl"
    filter_glob: StringProperty(
            default="*.trmdl",
            options={'HIDDEN'},
            maxlen=255,
    )
    filepath = bpy.props.StringProperty(subtype='FILE_PATH',)
    files = CollectionProperty(type=bpy.types.PropertyGroup)
    rare: BoolProperty(
            name="Load Shiny",
            description="Uses rare material instead of normal one",
            default=False,
            )
    multiple: BoolProperty(
            name="Load All Folder",
            description="Uses rare material instead of normal one",
            default=False,
            )
    loadlods: BoolProperty(
            name="Load LODS",
            description="Uses rare material instead of normal one",
            default=False,
            )
    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop(self, 'rare')
        
        box = layout.box()
        box.prop(self, 'multiple')
        
        box = layout.box()
        box.prop(self, 'loadlods')
        
    def execute(self, context):
        directory = os.path.dirname(self.filepath)
        if self.multiple == False:
            filename = os.path.basename(self.filepath)        
            f = open(os.path.join(directory, filename), "rb")
            from_trmdl(directory, f, self.rare, self.loadlods)
            f.close()
            return {'FINISHED'}  
        else:
            file_list = sorted(os.listdir(directory))
            obj_list = [item for item in file_list if item.endswith('.trmdl')]
            for item in obj_list:
                f = open(os.path.join(directory, item), "rb")
                from_trmdl(directory, f, self.rare, self.loadlods)
                f.close()
            return {'FINISHED'}

def from_trmdl(filep, trmdl, rare, loadlods):
    # make collection
    if IN_BLENDER_ENV:
        new_collection = bpy.data.collections.new(os.path.basename(trmdl.name))
        bpy.context.scene.collection.children.link(new_collection)

    textureextension = ".png"


    materials = []
    bone_structure = None

    trskl = None
    trmsh = None
    trmtr = None
    
    trmsh_lods_array = []
    bone_array = []
    bone_id_map = {}
    bone_rig_array = []
    trskl_bone_adjust = 0
    CharaCheck = "None"

    print("Parsing TRMDL...")

    trmdl_file_start = readlong(trmdl); fseek(trmdl, trmdl_file_start)
    trmdl_struct = ftell(trmdl) - readlong(trmdl); fseek(trmdl, trmdl_struct)
    trmdl_struct_len = readshort(trmdl)


    if trmdl_struct_len == 0x0012:
        trmdl_struct_section_len = readshort(trmdl)
        trmdl_struct_start = readshort(trmdl)
        trmdl_struct_trmsh = readshort(trmdl)
        trmdl_struct_trskl = readshort(trmdl)
        trmdl_struct_trmtr = readshort(trmdl)
        trmdl_struct_custom = readshort(trmdl)
        trmdl_struct_bound_box = readshort(trmdl)
        trmdl_struct_float = readshort(trmdl)
    elif trmdl_struct_len == 0x0014: #ScarletViolet Only
        trmdl_struct_section_len = readshort(trmdl)
        trmdl_struct_start = readshort(trmdl)
        trmdl_struct_trmsh = readshort(trmdl)
        trmdl_struct_trskl = readshort(trmdl)
        trmdl_struct_trmtr = readshort(trmdl)
        trmdl_struct_custom = readshort(trmdl)
        trmdl_struct_bound_box = readshort(trmdl)
        trmdl_struct_float = readshort(trmdl)
        trmdl_struct_trltt = readshort(trmdl)
    elif trmdl_struct_len == 0x0018: #ScarletViolet Only
        trmdl_struct_section_len = readshort(trmdl)
        trmdl_struct_start = readshort(trmdl)
        trmdl_struct_trmsh = readshort(trmdl)
        trmdl_struct_trskl = readshort(trmdl)
        trmdl_struct_trmtr = readshort(trmdl)
        trmdl_struct_custom = readshort(trmdl)
        trmdl_struct_bound_box = readshort(trmdl)
        trmdl_struct_float = readshort(trmdl)
        trmdl_struct_trltt = readshort(trmdl)
        trmdl_struct_unka = readshort(trmdl)
        trmdl_struct_unkb = readshort(trmdl)
    else:
        raise AssertionError("Unexpected TRMDL header struct length!")

    if trmdl_struct_trmsh != 0:
        fseek(trmdl, trmdl_file_start + trmdl_struct_trmsh)
        trmsh_start = ftell(trmdl) + readlong(trmdl); fseek(trmdl, trmsh_start)
        trmsh_count = readlong(trmdl)
        for x in range(trmsh_count):
            trmsh_offset = ftell(trmdl) + readlong(trmdl)
            trmsh_ret = ftell(trmdl)
            fseek(trmdl, trmsh_offset)
            trmsh_struct = ftell(trmdl) - readlong(trmdl); fseek(trmdl, trmsh_struct)
            trmsh_struct_len = readshort(trmdl)

            if trmsh_struct_len != 0x0006:
                raise AssertionError("Unexpected TRMSH struct length!")

            trmsh_struct_section_len = readshort(trmdl)
            trmsh_struct_ptr_name = readshort(trmdl)

            if trmsh_struct_ptr_name != 0:
                fseek(trmdl, trmsh_offset + trmsh_struct_ptr_name)
                trmsh_name_offset = ftell(trmdl) + readlong(trmdl)
                fseek(trmdl, trmsh_name_offset)
                trmsh_name_len = readlong(trmdl)
                chara_check = readfixedstring(trmdl, 3); fseek(trmdl, ftell(trmdl) - 3)

                if chara_check.startswith(('au_')): chara_check = "CommonNPC"
                elif chara_check.startswith(('bu_')): chara_check = "CommonNPC"
                elif chara_check.startswith(('cf_')): chara_check = "CommonNPC"
                elif chara_check.startswith(('cm_')): chara_check = "CommonNPC"
                elif chara_check.startswith(('df_')): chara_check = "CommonNPC"
                elif chara_check.startswith(('dm_')): chara_check = "CommonNPC"
                elif chara_check.startswith(('p1_')): chara_check = "Rei"
                elif chara_check.startswith(('p2_')): chara_check = "Akari"
                elif chara_check.startswith(('pm')): chara_check = "Pokemon"
                else: chara_check = "None"

                trmsh_name = readfixedstring(trmdl, trmsh_name_len)
                print(trmsh_name)
                print(chara_check)
                trmsh_lods_array.append(trmsh_name)
            fseek(trmdl, trmsh_ret)

    if trmdl_struct_trskl != 0:
        fseek(trmdl, trmdl_file_start + trmdl_struct_trskl)
        trskl_start = ftell(trmdl) + readlong(trmdl); fseek(trmdl, trskl_start)
        trskl_struct = ftell(trmdl) - readlong(trmdl); fseek(trmdl, trskl_struct)
        trskl_struct_len = readshort(trmdl)

        if trskl_struct_len != 0x0006:
            raise AssertionError("Unexpected TRSKL struct length!")

        trskl_struct_section_len = readshort(trmdl)
        trskl_struct_ptr_name = readshort(trmdl)

        if trskl_struct_ptr_name != 0:
            fseek(trmdl, trskl_start + trskl_struct_ptr_name)
            trskl_name_offset = ftell(trmdl) + readlong(trmdl)
            fseek(trmdl, trskl_name_offset)
            trskl_name_len = readlong(trmdl)
            trskl_name = readfixedstring(trmdl, trskl_name_len)
            print(trskl_name)

            if os.path.exists(os.path.join(filep, trskl_name)):
                trskl = open(os.path.join(filep, trskl_name), "rb")
            else:
                print(f"Can't find {trskl_name}!")

    if trmdl_struct_trmtr != 0:
        fseek(trmdl, trmdl_file_start + trmdl_struct_trmtr)
        trmtr_start = ftell(trmdl) + readlong(trmdl); fseek(trmdl, trmtr_start)
        trmtr_count = readlong(trmdl)
        for x in range(trmtr_count):
            trmtr_offset = ftell(trmdl) + readlong(trmdl)
            trmtr_ret = ftell(trmdl)
            fseek(trmdl, trmtr_offset)
            trmtr_name_len = readlong(trmdl)  #  - 6 -- dunno why the extension was excluded
            trmtr_name = readfixedstring(trmdl, trmtr_name_len)
            # TODO ArceusShiny
            # LINE 1227
            print(trmtr_name)
            if x == 0:
                if rare == True:
                    trmtr = open(os.path.join(filep, Path(trmtr_name).stem + "_rare.trmtr"), "rb")
                else:
                    trmtr = open(os.path.join(filep, trmtr_name), "rb") 
            fseek(trmdl, trmtr_ret)
    fclose(trmdl)

    # TODO create bone_rig_array
    # LINE 1247
    if chara_check == "Rei" or chara_check == "Akari":
        trskl = trskl = open(os.path.join(filep, "p0_base.trskl"), "rb")
    
    if trskl is not None:
        print("Parsing TRSKL...")
        trskl_file_start = readlong(trskl)
        fseek(trskl, trskl_file_start)
        trskl_struct = ftell(trskl) - readlong(trskl); fseek(trskl, trskl_struct)
        trskl_struct_len = readshort(trskl)
        if trskl_struct_len == 0x000C:
            trskl_struct_section_len = readshort(trskl)
            trskl_struct_start = readshort(trskl)
            trskl_struct_bone = readshort(trskl)
            trskl_struct_b = readshort(trskl)
            trskl_struct_c = readshort(trskl)
            trskl_struct_bone_adjust = 0
        elif trskl_struct_len == 0x000E:
            trskl_struct_section_len = readshort(trskl)
            trskl_struct_start = readshort(trskl)
            trskl_struct_bone = readshort(trskl)
            trskl_struct_b = readshort(trskl)
            trskl_struct_c = readshort(trskl)
            trskl_struct_bone_adjust = readshort(trskl)
        else:
            raise AssertionError("Unexpected TRSKL header struct length!")

        if trskl_struct_bone_adjust != 0:
            fseek(trskl, trskl_file_start + trskl_struct_bone_adjust)
            trskl_bone_adjust = readlong(trskl); print(f"Mesh node IDs start at {trskl_bone_adjust}")

        if trskl_struct_bone != 0:
            fseek(trskl, trskl_file_start + trskl_struct_bone)
            trskl_bone_start = ftell(trskl) + readlong(trskl); fseek(trskl, trskl_bone_start)
            bone_count = readlong(trskl)

            if IN_BLENDER_ENV:
                new_armature = bpy.data.armatures.new(os.path.basename(trmdl.name))
                bone_structure = bpy.data.objects.new(os.path.basename(trmdl.name), new_armature)
                new_collection.objects.link(bone_structure)
                bpy.context.view_layer.objects.active = bone_structure
                bpy.ops.object.editmode_toggle()
            
            for x in range(bone_count):
                bone_offset = ftell(trskl) + readlong(trskl)
                bone_ret = ftell(trskl)
                fseek(trskl, bone_offset)
                print(f"Bone {x} start: {hex(bone_offset)}")
                trskl_bone_struct = ftell(trskl) - readlong(trskl); fseek(trskl, trskl_bone_struct)
                trskl_bone_struct_len = readshort(trskl)

                if trskl_bone_struct_len == 0x0012:
                    trskl_bone_struct_ptr_section_len = readshort(trskl)
                    trskl_bone_struct_ptr_string = readshort(trskl)
                    trskl_bone_struct_ptr_bone = readshort(trskl)
                    trskl_bone_struct_ptr_c = readshort(trskl)
                    trskl_bone_struct_ptr_d = readshort(trskl)
                    trskl_bone_struct_ptr_parent = readshort(trskl)
                    trskl_bone_struct_ptr_rig_id = readshort(trskl)
                    trskl_bone_struct_ptr_bone_merge = readshort(trskl)
                    trskl_bone_struct_ptr_h = 0
                elif trskl_bone_struct_len == 0x0014:
                    trskl_bone_struct_ptr_section_len = readshort(trskl)
                    trskl_bone_struct_ptr_string = readshort(trskl)
                    trskl_bone_struct_ptr_bone = readshort(trskl)
                    trskl_bone_struct_ptr_c = readshort(trskl)
                    trskl_bone_struct_ptr_d = readshort(trskl)
                    trskl_bone_struct_ptr_parent = readshort(trskl)
                    trskl_bone_struct_ptr_rig_id = readshort(trskl)
                    trskl_bone_struct_ptr_bone_merge = readshort(trskl)
                    trskl_bone_struct_ptr_h = readshort(trskl)
                else:
                    trskl_bone_struct_ptr_section_len = readshort(trskl)
                    trskl_bone_struct_ptr_string = readshort(trskl)
                    trskl_bone_struct_ptr_bone = readshort(trskl)
                    trskl_bone_struct_ptr_c = readshort(trskl)
                    trskl_bone_struct_ptr_d = readshort(trskl)
                    trskl_bone_struct_ptr_parent = readshort(trskl)
                    trskl_bone_struct_ptr_rig_id = readshort(trskl)
                    trskl_bone_struct_ptr_bone_merge = readshort(trskl)
                    trskl_bone_struct_ptr_h = readshort(trskl)

                if trskl_bone_struct_ptr_bone_merge != 0:
                    fseek(trskl, bone_offset + trskl_bone_struct_ptr_bone_merge)
                    bone_merge_start = ftell(trskl) + readlong(trskl); fseek(trskl, bone_merge_start)
                    bone_merge_string_len = readlong(trskl)
                    if bone_merge_string_len != 0:
                        bone_merge_string = readfixedstring(trskl, bone_merge_string_len)
                        print(f"BoneMerge to {bone_merge_string}")
                    else: bone_merge_string = ""

                if trskl_bone_struct_ptr_bone != 0:
                    fseek(trskl, bone_offset + trskl_bone_struct_ptr_bone)
                    bone_pos_start = ftell(trskl) + readlong(trskl); fseek(trskl, bone_pos_start)
                    bone_pos_struct = ftell(trskl) - readlong(trskl); fseek(trskl, bone_pos_struct)
                    bone_pos_struct_len = readshort(trskl)

                    if bone_pos_struct_len != 0x000A:
                        raise AssertionError("Unexpected bone position struct length!")

                    bone_pos_struct_section_len = readshort(trskl)
                    bone_pos_struct_ptr_scl = readshort(trskl)
                    bone_pos_struct_ptr_rot = readshort(trskl)
                    bone_pos_struct_ptr_trs = readshort(trskl)

                    fseek(trskl, bone_pos_start + bone_pos_struct_ptr_trs)
                    bone_tx = readfloat(trskl); bone_ty = readfloat(trskl); bone_tz = readfloat(trskl)
                    # TODO ArceusScale
                    # LINE 1797
                    fseek(trskl, bone_pos_start + bone_pos_struct_ptr_rot)
                    bone_rx = readfloat(trskl); bone_ry = readfloat(trskl); bone_rz = readfloat(trskl)
                    fseek(trskl, bone_pos_start + bone_pos_struct_ptr_scl)
                    bone_sx = readfloat(trskl); bone_sy = readfloat(trskl); bone_sz = readfloat(trskl)

                    if trskl_bone_struct_ptr_string != 0:
                        fseek(trskl, bone_offset + trskl_bone_struct_ptr_string)
                        bone_string_start = ftell(trskl) + readlong(trskl); fseek(trskl, bone_string_start)
                        bone_str_len = readlong(trskl); bone_name = readfixedstring(trskl, bone_str_len)
                    if trskl_bone_struct_ptr_parent != 0x00:
                        fseek(trskl, bone_offset + trskl_bone_struct_ptr_parent)
                        bone_parent = readlong(trskl) + 1
                    else:
                        bone_parent = 0
                    if trskl_bone_struct_ptr_rig_id != 0:
                        fseek(trskl, bone_offset + trskl_bone_struct_ptr_rig_id)
                        bone_rig_id = readlong(trskl) + trskl_bone_adjust

                        while len(bone_rig_array) <= bone_rig_id:
                            bone_rig_array.append("")
                        bone_rig_array[bone_rig_id] = bone_name

                    bone_matrix = mathutils.Matrix.LocRotScale(
                        (bone_tx, bone_ty, bone_tz),
                        mathutils.Euler((bone_rx, bone_ry, bone_rz)),
                        (bone_sx, bone_sy, bone_sz))

                    if IN_BLENDER_ENV:
                        new_bone = new_armature.edit_bones.new(bone_name)

                        new_bone.use_connect = False
                        new_bone.use_inherit_rotation = True
                        new_bone.use_inherit_scale = True
                        new_bone.use_local_location = True

                        new_bone.head = (0, 0, 0)
                        new_bone.tail = (0, 0, 0.1)
                        new_bone.matrix = bone_matrix

                        if bone_parent != 0:
                            new_bone.parent = bone_array[bone_parent - 1]
                            new_bone.matrix = bone_array[bone_parent - 1].matrix @ bone_matrix

                        if bone_name in bone_rig_array:
                            bone_id_map[bone_rig_array.index(bone_name)] = bone_name
                        else:
                            print(f"Bone {bone_name} not found in bone rig array!")
                        bone_array.append(new_bone)
                fseek(trskl, bone_ret)
        fclose(trskl)
        if IN_BLENDER_ENV:
            bpy.ops.object.editmode_toggle()
    
    if trmtr is not None:
        print("Parsing TRMTR...")
        trmtr_file_start = readlong(trmtr)
        mat_data_array = []
        fseek(trmtr, trmtr_file_start)
        trmtr_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, trmtr_struct)
        trmtr_struct_len = readshort(trmtr)

        if trmtr_struct_len != 0x0008:
            raise AssertionError("Unexpected TRMTR header struct length!")
        trmtr_struct_section_len = readshort(trmtr)
        trmtr_struct_start = readshort(trmtr)
        trmtr_struct_material = readshort(trmtr)

        if trmtr_struct_material != 0:
            fseek(trmtr, trmtr_file_start + trmtr_struct_material)
            mat_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_start)
            mat_count = readlong(trmtr)
            for x in range(mat_count):
                mat_shader = "Standard"; mat_col0 = ""; mat_lym0 = ""; mat_nrm0 = ""; mat_ao0 = ""; mat_emi0 = ""; mat_rgh0 = ""; mat_mtl0 = ""; mat_msk0 = ""; mat_highmsk0 = ""
                mat_uv_scale_u = 1.0; mat_uv_scale_v = 1.0; mat_uv_trs_u = 0; mat_uv_trs_v = 0
                mat_uv_scale2_u = 1.0; mat_uv_scale2_v = 1.0; mat_uv_trs2_u = 0; mat_uv_trs2_v = 0
                mat_color1_r = 1.0; mat_color1_g = 1.0; mat_color1_b = 1.0
                mat_color2_r = 1.0; mat_color2_g = 1.0; mat_color2_b = 1.0
                mat_color3_r = 1.0; mat_color3_g = 1.0; mat_color3_b = 1.0
                mat_color4_r = 1.0; mat_color4_g = 1.0; mat_color4_b = 1.0

                mat_emcolor1_r = 1.0; mat_emcolor1_g = 1.0; mat_emcolor1_b = 1.0
                mat_emcolor2_r = 1.0; mat_emcolor2_g = 1.0; mat_emcolor2_b = 1.0
                mat_emcolor3_r = 1.0; mat_emcolor3_g = 1.0; mat_emcolor3_b = 1.0
                mat_emcolor4_r = 1.0; mat_emcolor4_g = 1.0; mat_emcolor4_b = 1.0
                mat_emcolor5_r = 1.0; mat_emcolor5_g = 1.0; mat_emcolor5_b = 1.0                
                mat_rgh_layer0 = 1.0; mat_rgh_layer1 = 1.0; mat_rgh_layer2 = 1.0; mat_rgh_layer3 = 1.0; mat_rgh_layer4 = 1.0
                mat_mtl_layer0 = 0.0; mat_mtl_layer1 = 0.0; mat_mtl_layer2 = 0.0; mat_mtl_layer3 = 0.0; mat_mtl_layer4 = 0.0
                mat_reflectance = 0.0
                mat_emm_intensity = 1.0
                mat_offset = ftell(trmtr) + readlong(trmtr)
                mat_ret = ftell(trmtr)

                mat_enable_base_color_map = False
                mat_enable_normal_map = False
                mat_enable_ao_map = False
                mat_enable_emission_color_map = False
                mat_enable_roughness_map = False
                mat_enable_metallic_map = False
                mat_enable_displacement_map = False
                mat_enable_highlight_map = False

                fseek(trmtr, mat_offset)
                print("--------------------")
                mat_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_struct)
                mat_struct_len = readshort(trmtr)

                if mat_struct_len != 0x0024:
                    raise AssertionError("Unexpected material struct length!")
                mat_struct_section_len = readshort(trmtr)
                mat_struct_ptr_param_a = readshort(trmtr)
                mat_struct_ptr_param_b = readshort(trmtr)
                mat_struct_ptr_param_c = readshort(trmtr)
                mat_struct_ptr_param_d = readshort(trmtr)
                mat_struct_ptr_param_e = readshort(trmtr)
                mat_struct_ptr_param_f = readshort(trmtr)
                mat_struct_ptr_param_g = readshort(trmtr)
                mat_struct_ptr_param_h = readshort(trmtr)
                mat_struct_ptr_param_i = readshort(trmtr)
                mat_struct_ptr_param_j = readshort(trmtr)
                mat_struct_ptr_param_k = readshort(trmtr)
                mat_struct_ptr_param_l = readshort(trmtr)
                mat_struct_ptr_param_m = readshort(trmtr)
                mat_struct_ptr_param_n = readshort(trmtr)
                mat_struct_ptr_param_o = readshort(trmtr)
                mat_struct_ptr_param_p = readshort(trmtr)

                if mat_struct_ptr_param_a != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_a)
                    mat_param_a_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_a_start)
                    mat_name_len = readlong(trmtr)
                    mat_name = readfixedstring(trmtr, mat_name_len)
                    print(f"Material properties for {mat_name}:")
                if mat_struct_ptr_param_b != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_b)
                    mat_param_b_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_b_start)
                    mat_param_b_section_count = readlong(trmtr)
                    for z in range(mat_param_b_section_count):
                        mat_param_b_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_b_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_b_offset)
                        mat_param_b_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_b_struct)
                        mat_param_b_struct_len = readshort(trmtr)

                        if mat_param_b_struct_len != 0x0008:
                            raise AssertionError("Unexpected material param b struct length!")
                        mat_param_b_struct_section_len = readshort(trmtr)
                        mat_param_b_struct_ptr_string = readshort(trmtr)
                        mat_param_b_struct_ptr_params = readshort(trmtr)

                        if mat_param_b_struct_ptr_string != 0:
                            fseek(trmtr, mat_param_b_offset + mat_param_b_struct_ptr_string)
                            mat_param_b_shader_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_b_shader_start)
                            mat_param_b_shader_len = readlong(trmtr)
                            mat_param_b_shader_string = readfixedstring(trmtr, mat_param_b_shader_len)
                            print(f"Shader: {mat_param_b_shader_string}")
                            mat_shader = mat_param_b_shader_string
                        if mat_param_b_struct_ptr_params != 0:
                            fseek(trmtr, mat_param_b_offset + mat_param_b_struct_ptr_params)
                            mat_param_b_sub_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_b_sub_start)
                            mat_param_b_sub_count = readlong(trmtr)
                            for y in range(mat_param_b_sub_count):
                                mat_param_b_sub_offset = ftell(trmtr) + readlong(trmtr)
                                mat_param_b_sub_ret = ftell(trmtr)
                                fseek(trmtr, mat_param_b_sub_offset)
                                mat_param_b_sub_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_b_sub_struct)
                                mat_param_b_sub_struct_len = readshort(trmtr)

                                if mat_param_b_sub_struct_len != 0x0008:
                                    raise AssertionError("Unexpected material param b sub struct length!")
                                mat_param_b_sub_struct_section_len = readshort(trmtr)
                                mat_param_b_sub_struct_ptr_string = readshort(trmtr)
                                mat_param_b_sub_struct_ptr_value = readshort(trmtr)

                                if mat_param_b_sub_struct_ptr_string != 0:
                                    fseek(trmtr, mat_param_b_sub_offset + mat_param_b_sub_struct_ptr_string)
                                    mat_param_b_sub_string_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_b_sub_string_start)
                                    mat_param_b_sub_string_len = readlong(trmtr)
                                    mat_param_b_sub_string = readfixedstring(trmtr, mat_param_b_sub_string_len)
                                if mat_param_b_sub_struct_ptr_value != 0:
                                    fseek(trmtr, mat_param_b_sub_offset + mat_param_b_sub_struct_ptr_value)
                                    mat_param_b_sub_value_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_b_sub_value_start)
                                    mat_param_b_sub_value_len = readlong(trmtr)
                                    mat_param_b_sub_value = readfixedstring(trmtr, mat_param_b_sub_value_len)
                                    print(f"(param_b) {mat_param_b_sub_string}: {mat_param_b_sub_value}")

                                if mat_param_b_sub_string == "EnableBaseColorMap": mat_enable_base_color_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableNormalMap": mat_enable_normal_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableAOMap": mat_enable_ao_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableEmissionColorMap": mat_enable_emission_color_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableRoughnessMap": mat_enable_roughness_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableMetallicMap": mat_enable_metallic_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableDisplacementMap": mat_enable_displacement_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableHighlight": mat_enable_highlight_map = mat_param_b_sub_value == "True"
                                if mat_param_b_sub_string == "EnableOverrideColor": mat_enable_override_color = mat_param_b_sub_value == "True"
                                fseek(trmtr, mat_param_b_sub_ret)
                        fseek(trmtr, mat_param_b_ret)

                if mat_struct_ptr_param_c != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_c)
                    mat_param_c_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_c_start)
                    mat_param_c_count = readlong(trmtr)

                    for z in range(mat_param_c_count):
                        mat_param_c_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_c_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_c_offset)
                        mat_param_c_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_c_struct)
                        mat_param_c_struct_len = readshort(trmtr)

                        if mat_param_c_struct_len == 0x0008:
                            mat_param_c_struct_section_len = readshort(trmtr)
                            mat_param_c_struct_ptr_string = readshort(trmtr)
                            mat_param_c_struct_ptr_value = readshort(trmtr)
                            mat_param_c_struct_ptr_id = 0
                        elif mat_param_c_struct_len == 0x000A:
                            mat_param_c_struct_section_len = readshort(trmtr)
                            mat_param_c_struct_ptr_string = readshort(trmtr)
                            mat_param_c_struct_ptr_value = readshort(trmtr)
                            mat_param_c_struct_ptr_id = readshort(trmtr)
                        else:
                            raise AssertionError("Unexpected material param c struct length!")

                        if mat_param_c_struct_ptr_string != 0:
                            fseek(trmtr, mat_param_c_offset + mat_param_c_struct_ptr_string)
                            mat_param_c_string_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_c_string_start)
                            mat_param_c_string_len = readlong(trmtr)
                            mat_param_c_string = readfixedstring(trmtr, mat_param_c_string_len)
                        if mat_param_c_struct_ptr_value != 0:
                            fseek(trmtr, mat_param_c_offset + mat_param_c_struct_ptr_value)
                            mat_param_c_value_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_c_value_start)
                            mat_param_c_value_len = readlong(trmtr)  # - 5 # Trimming the ".bntx" from the end.
                            mat_param_c_value = readfixedstring(trmtr, mat_param_c_value_len)
                        if mat_param_c_struct_ptr_id != 0:
                            fseek(trmtr, mat_param_c_offset + mat_param_c_struct_ptr_id)
                            mat_param_c_id = readlong(trmtr)
                        else:
                            mat_param_c_id = 0

                        if mat_param_c_string == "BaseColorMap": mat_col0 = mat_param_c_value
                        elif mat_param_c_string == "LayerMaskMap": mat_lym0 = mat_param_c_value
                        elif mat_param_c_string == "NormalMap": mat_nrm0 = mat_param_c_value
                        elif mat_param_c_string == "AOMap": mat_ao0 = mat_param_c_value
                        elif mat_param_c_string == "EmissionColorMap": mat_emi0 = mat_param_c_value
                        elif mat_param_c_string == "RoughnessMap": mat_rgh0 = mat_param_c_value
                        elif mat_param_c_string == "MetallicMap": mat_mtl0 = mat_param_c_value
                        elif mat_param_c_string == "DisplacementMap": mat_msk0 = mat_param_c_value
                        elif mat_param_c_string == "HighlightMaskMap": mat_highmsk0 = mat_param_c_value

                        # -- There's also all of the following, which aren't automatically assigned to keep things simple.
                        # -- "AOMap"
                        # -- "AOMap1"
                        # -- "AOMap2"
                        # -- "BaseColorMap1"
                        # -- "DisplacementMap"
                        # -- "EyelidShadowMaskMap"
                        # -- "FlowMap"
                        # -- "FoamMaskMap"
                        # -- "GrassCollisionMap"
                        # -- "HighlightMaskMap"
                        # -- "LowerEyelidColorMap"
                        # -- "NormalMap1"
                        # -- "NormalMap2"
                        # -- "PackedMap"
                        # -- "UpperEyelidColorMap"
                        # -- "WeatherLayerMaskMap"
                        # -- "WindMaskMap"

                        print(f"(param_c) {mat_param_c_string}: {mat_param_c_value} [{mat_param_c_id}]")
                        fseek(trmtr, mat_param_c_ret)

                if mat_struct_ptr_param_d != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_d)
                    mat_param_d_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_d_start)
                    mat_param_d_count = readlong(trmtr)

                    for z in range(mat_param_d_count):
                        mat_param_d_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_d_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_d_offset)
                        mat_param_d_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_d_struct)
                        mat_param_d_struct_len = readshort(trmtr)

                        if mat_param_d_struct_len != 0x001E:
                            raise AssertionError("Unexpected material param d struct length!")
                        mat_param_d_struct_section_len = readshort(trmtr)
                        mat_param_d_struct_ptr_a = readshort(trmtr)
                        mat_param_d_struct_ptr_b = readshort(trmtr)
                        mat_param_d_struct_ptr_c = readshort(trmtr)
                        mat_param_d_struct_ptr_d = readshort(trmtr)
                        mat_param_d_struct_ptr_e = readshort(trmtr)
                        mat_param_d_struct_ptr_f = readshort(trmtr)
                        mat_param_d_struct_ptr_g = readshort(trmtr)
                        mat_param_d_struct_ptr_h = readshort(trmtr)
                        mat_param_d_struct_ptr_i = readshort(trmtr)
                        mat_param_d_struct_ptr_j = readshort(trmtr)
                        mat_param_d_struct_ptr_k = readshort(trmtr)
                        mat_param_d_struct_ptr_l = readshort(trmtr)
                        mat_param_d_struct_ptr_m = readshort(trmtr)

                        if mat_param_d_struct_ptr_a != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_a)
                            mat_param_d_value_a = readlong(trmtr)
                        else: mat_param_d_value_a = 0
                        if mat_param_d_struct_ptr_b != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_b)
                            mat_param_d_value_b = readlong(trmtr)
                        else: mat_param_d_value_b = 0
                        if mat_param_d_struct_ptr_c != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_c)
                            mat_param_d_value_c = readlong(trmtr)
                        else: mat_param_d_value_c = 0
                        if mat_param_d_struct_ptr_d != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_d)
                            mat_param_d_value_d = readlong(trmtr)
                        else: mat_param_d_value_d = 0
                        if mat_param_d_struct_ptr_e != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_e)
                            mat_param_d_value_e = readlong(trmtr)
                        else: mat_param_d_value_e = 0
                        if mat_param_d_struct_ptr_f != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_f)
                            mat_param_d_value_f = readlong(trmtr)
                        else: mat_param_d_value_f = 0
                        if mat_param_d_struct_ptr_g != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_g)
                            mat_param_d_value_g = readlong(trmtr)
                        else: mat_param_d_value_g = 0
                        if mat_param_d_struct_ptr_h != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_h)
                            mat_param_d_value_h = readlong(trmtr)
                        else: mat_param_d_value_h = 0
                        if mat_param_d_struct_ptr_i != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_i)
                            mat_param_d_value_i = readlong(trmtr)
                        else: mat_param_d_value_i = 0
                        if mat_param_d_struct_ptr_j != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_j)
                            mat_param_d_value_j = readlong(trmtr)
                        else: mat_param_d_value_j = 0
                        if mat_param_d_struct_ptr_k != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_k)
                            mat_param_d_value_k = readlong(trmtr)
                        else: mat_param_d_value_k = 0
                        if mat_param_d_struct_ptr_l != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_l)
                            mat_param_d_value_l = readlong(trmtr)
                        else: mat_param_d_value_l = 0
                        if mat_param_d_struct_ptr_m != 0:
                            fseek(trmtr, mat_param_d_offset + mat_param_d_struct_ptr_m)
                            mat_param_d_value_m1 = readfloat(trmtr); mat_param_d_value_m2 = readfloat(trmtr); mat_param_d_value_m3 = readfloat(trmtr)
                        else: mat_param_d_value_m1 = 0; mat_param_d_value_m2 = 0; mat_param_d_value_m3 = 0

                        print(f"Flags #{z}: {mat_param_d_value_a} | {mat_param_d_value_b} | {mat_param_d_value_c} | {mat_param_d_value_d} | {mat_param_d_value_e} | {mat_param_d_value_f} | {mat_param_d_value_g} | {mat_param_d_value_h} | {mat_param_d_value_i} | {mat_param_d_value_j} | {mat_param_d_value_k} | {mat_param_d_value_l} | {mat_param_d_value_m1} | {mat_param_d_value_m2} | {mat_param_d_value_m3}")
                        fseek(trmtr, mat_param_d_ret)

                if mat_struct_ptr_param_e != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_e)
                    mat_param_e_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_e_start)
                    mat_param_e_count = readlong(trmtr)

                    for z in range(mat_param_e_count):
                        mat_param_e_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_e_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_e_offset)
                        mat_param_e_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_e_struct)
                        mat_param_e_struct_len = readshort(trmtr)

                        if mat_param_e_struct_len == 0x0006:
                            mat_param_e_struct_section_len = readshort(trmtr)
                            mat_param_e_struct_ptr_string = readshort(trmtr)
                            mat_param_e_struct_ptr_value = 0
                        elif mat_param_e_struct_len == 0x0008:
                            mat_param_e_struct_section_len = readshort(trmtr)
                            mat_param_e_struct_ptr_string = readshort(trmtr)
                            mat_param_e_struct_ptr_value = readshort(trmtr)
                        else:
                            raise Exception(f"Unknown mat_param_e struct length!")

                        if mat_param_e_struct_ptr_string != 0:
                            fseek(trmtr, mat_param_e_offset + mat_param_e_struct_ptr_string)
                            mat_param_e_string_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_e_string_start)
                            mat_param_e_string_len = readlong(trmtr)
                            mat_param_e_string = readfixedstring(trmtr, mat_param_e_string_len)

                        if mat_param_e_struct_ptr_value != 0:
                            fseek(trmtr, mat_param_e_offset + mat_param_e_struct_ptr_value)
                            mat_param_e_value = readfloat(trmtr)
                        else: mat_param_e_value = 0

                        if mat_param_e_string == "Roughness": mat_rgh_layer0 = mat_param_e_value
                        elif mat_param_e_string == "RoughnessLayer1": mat_rgh_layer1 = mat_param_e_value
                        elif mat_param_e_string == "RoughnessLayer2": mat_rgh_layer2 = mat_param_e_value
                        elif mat_param_e_string == "RoughnessLayer3": mat_rgh_layer3 = mat_param_e_value
                        elif mat_param_e_string == "RoughnessLayer4": mat_rgh_layer4 = mat_param_e_value
                        elif mat_param_e_string == "Metallic": mat_mtl_layer0 = mat_param_e_value
                        elif mat_param_e_string == "MetallicLayer1": mat_mtl_layer1 = mat_param_e_value
                        elif mat_param_e_string == "MetallicLayer2": mat_mtl_layer2 = mat_param_e_value
                        elif mat_param_e_string == "MetallicLayer3": mat_mtl_layer3 = mat_param_e_value
                        elif mat_param_e_string == "MetallicLayer4": mat_mtl_layer4 = mat_param_e_value
                        elif mat_param_e_string == "Reflectance": mat_reflectance = mat_param_e_value
                        elif mat_param_e_string == "EmissionIntensity": mat_emm_intensity = mat_param_e_value
                        
                        print(f"(param_e) {mat_param_e_string}: {mat_param_e_value}")
                        fseek(trmtr, mat_param_e_ret)

                if mat_struct_ptr_param_f != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_f)
                    mat_param_f_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_f_start)
                    mat_param_f_count = readlong(trmtr)

                    for z in range(mat_param_f_count):
                        mat_param_f_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_f_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_f_offset)
                        mat_param_f_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_f_struct)
                        mat_param_f_struct_len = readlong(trmtr)

                        if mat_param_f_struct_len != 0x0008:
                            raise Exception(f"Unknown mat_param_f struct length!")
                        mat_param_f_struct_section_len = readshort(trmtr)
                        mat_param_f_struct_ptr_string = readshort(trmtr)
                        mat_param_f_struct_ptr_values = readshort(trmtr)

                        if mat_param_f_struct_ptr_string != 0:
                            fseek(trmtr, mat_param_f_offset + mat_param_f_struct_ptr_string)
                            mat_param_f_string_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_f_string_start)
                            mat_param_f_string_len = readlong(trmtr)
                            mat_param_f_string = readfixedstring(trmtr, mat_param_f_string_len)

                        if mat_param_f_struct_ptr_values != 0:
                            fseek(trmtr, mat_param_f_offset + mat_param_f_struct_ptr_values)
                            mat_param_f_value1 = readfloat(trmtr)
                            mat_param_f_value2 = readfloat(trmtr)
                        else: mat_param_f_value1 = mat_param_f_value2 = 0

                        print(f"(param_f) {mat_param_f_string}: {mat_param_f_value1}, {mat_param_f_value2}")
                        fseek(trmtr, mat_param_f_ret)

                if mat_struct_ptr_param_g != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_g)
                    mat_param_g_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_g_start)
                    mat_param_g_count = readlong(trmtr)

                    for z in range(mat_param_g_count):
                        mat_param_g_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_g_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_g_offset)
                        mat_param_g_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_g_struct)
                        mat_param_g_struct_len = readlong(trmtr)

                        if mat_param_g_struct_len != 0x0008:
                            raise Exception(f"Unknown mat_param_g struct length!")
                        mat_param_g_struct_section_len = readshort(trmtr)
                        mat_param_g_struct_ptr_string = readshort(trmtr)
                        mat_param_g_struct_ptr_values = readshort(trmtr)

                        if mat_param_g_struct_ptr_string != 0:
                            fseek(trmtr, mat_param_g_offset + mat_param_g_struct_ptr_string)
                            mat_param_g_string_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_g_string_start)
                            mat_param_g_string_len = readlong(trmtr)
                            mat_param_g_string = readfixedstring(trmtr, mat_param_g_string_len)

                        if mat_param_g_struct_ptr_values != 0:
                            fseek(trmtr, mat_param_g_offset + mat_param_g_struct_ptr_values)
                            mat_param_g_value1 = readfloat(trmtr)
                            mat_param_g_value2 = readfloat(trmtr)
                            mat_param_g_value3 = readfloat(trmtr)
                        else: mat_param_g_value1 = mat_param_g_value2 = mat_param_g_value3 = 0

                        print(f"(param_g) {mat_param_g_string}: {mat_param_g_value1}, {mat_param_g_value2}, {mat_param_g_value3}")
                        fseek(trmtr, mat_param_g_ret)

                if mat_struct_ptr_param_h != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_h)
                    mat_param_h_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_h_start)
                    mat_param_h_count = readlong(trmtr)

                    for z in range(mat_param_h_count):
                        mat_param_h_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_h_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_h_offset)
                        mat_param_h_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_h_struct)
                        mat_param_h_struct_len = readshort(trmtr)

                        if mat_param_h_struct_len != 0x0008:
                            raise Exception(f"Unknown mat_param_h struct length!")
                        mat_param_h_struct_section_len = readshort(trmtr)
                        mat_param_h_struct_ptr_string = readshort(trmtr)
                        mat_param_h_struct_ptr_values = readshort(trmtr)

                        if mat_param_h_struct_ptr_string != 0:
                            fseek(trmtr, mat_param_h_offset + mat_param_h_struct_ptr_string)
                            mat_param_h_string_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_h_string_start)
                            mat_param_h_string_len = readlong(trmtr)
                            mat_param_h_string = readfixedstring(trmtr, mat_param_h_string_len)

                        if mat_param_h_struct_ptr_values != 0:
                            fseek(trmtr, mat_param_h_offset + mat_param_h_struct_ptr_values)
                            mat_param_h_value1 = readfloat(trmtr)
                            mat_param_h_value2 = readfloat(trmtr)
                            mat_param_h_value3 = readfloat(trmtr)
                            mat_param_h_value4 = readfloat(trmtr)
                        else: mat_param_h_value1 = mat_param_h_value2 = mat_param_h_value3 = mat_param_h_value4 = 0

                        if mat_param_h_string == "UVScaleOffset": mat_uv_scale_u = mat_param_h_value1; mat_uv_scale_v = mat_param_h_value2; mat_uv_trs_u = mat_param_h_value3; mat_uv_trs_v = mat_param_h_value4
                        elif mat_param_h_string == "UVScaleOffset1": mat_uv_scale2_u = mat_param_h_value1; mat_uv_scale2_v = mat_param_h_value2; mat_uv_trs2_u = mat_param_h_value3; mat_uv_trs2_v = mat_param_h_value4
                        elif mat_param_h_string == "BaseColorLayer1": mat_color1_r = mat_param_h_value1; mat_color1_g = mat_param_h_value2; mat_color1_b = mat_param_h_value3
                        elif mat_param_h_string == "BaseColorLayer2": mat_color2_r = mat_param_h_value1; mat_color2_g = mat_param_h_value2; mat_color2_b = mat_param_h_value3
                        elif mat_param_h_string == "BaseColorLayer3": mat_color3_r = mat_param_h_value1; mat_color3_g = mat_param_h_value2; mat_color3_b = mat_param_h_value3
                        elif mat_param_h_string == "BaseColorLayer4": mat_color4_r = mat_param_h_value1; mat_color4_g = mat_param_h_value2; mat_color4_b = mat_param_h_value3
                        elif mat_param_h_string == "EmissionColorLayer1": mat_emcolor1_r = mat_param_h_value1; mat_emcolor1_g = mat_param_h_value2; mat_emcolor1_b = mat_param_h_value3
                        elif mat_param_h_string == "EmissionColorLayer2": mat_emcolor2_r = mat_param_h_value1; mat_emcolor2_g = mat_param_h_value2; mat_emcolor2_b = mat_param_h_value3
                        elif mat_param_h_string == "EmissionColorLayer3": mat_emcolor3_r = mat_param_h_value1; mat_emcolor3_g = mat_param_h_value2; mat_emcolor3_b = mat_param_h_value3
                        elif mat_param_h_string == "EmissionColorLayer4": mat_emcolor4_r = mat_param_h_value1; mat_emcolor4_g = mat_param_h_value2; mat_emcolor4_b = mat_param_h_value3
                        elif mat_param_h_string == "EmissionColorLayer5": mat_emcolor5_r = mat_param_h_value1; mat_emcolor5_g = mat_param_h_value2; mat_emcolor5_b = mat_param_h_value3
                        else: print(f"Unknown mat_param_h: {mat_param_h_string}")

                        print(f"(param_h) {mat_param_h_string}: {mat_param_h_value1}, {mat_param_h_value2}, {mat_param_h_value3}, {mat_param_h_value4}")
                        fseek(trmtr, mat_param_h_ret)

                if mat_struct_ptr_param_i != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_i)
                    mat_param_i_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_i_start)
                    mat_param_i_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_i_struct)
                    mat_param_i_struct_len = readlong(trmtr)

                    if mat_param_i_struct_len != 0x0000:
                        raise Exception(f"Unknown mat_param_i struct length!")

                if mat_struct_ptr_param_j != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_j)
                    mat_param_j_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_j_start)
                    mat_param_j_count = readlong(trmtr)

                    for y in range(mat_param_j_count):
                        mat_param_j_offset = ftell(trmtr) + readlong(trmtr)
                        mat_param_j_ret = ftell(trmtr)
                        fseek(trmtr, mat_param_j_offset)
                        mat_param_j_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_j_struct)
                        mat_param_j_struct_len = readshort(trmtr)

                        if mat_param_j_struct_len == 0x0006:
                            mat_param_j_struct_section_len = readshort(trmtr)
                            mat_param_j_struct_ptr_string = readshort(trmtr)
                            mat_param_j_struct_ptr_value = 0
                        elif mat_param_j_struct_len == 0x0008:
                            mat_param_j_struct_section_len = readshort(trmtr)
                            mat_param_j_struct_ptr_string = readshort(trmtr)
                            mat_param_j_struct_ptr_value = readshort(trmtr)
                        else:
                            raise Exception(f"Unknown mat_param_j struct length!")

                        if mat_param_j_struct_ptr_string != 0:
                            fseek(trmtr, mat_param_j_offset + mat_param_j_struct_ptr_string)
                            mat_param_j_string_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_j_string_start)
                            mat_param_j_string_len = readlong(trmtr)
                            mat_param_j_string = readfixedstring(trmtr, mat_param_j_string_len)

                        if mat_param_j_struct_ptr_value != 0:
                            fseek(trmtr, mat_param_j_offset + mat_param_j_struct_ptr_value)
                            mat_param_j_value = readlong(trmtr)
                        else: mat_param_j_value = "0" # why is this a string?

                        print(f"(param_j) {mat_param_j_string}: {mat_param_j_value}")
                        fseek(trmtr, mat_param_j_ret)

                if mat_struct_ptr_param_k != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_k)
                    mat_param_k_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_k_start)
                    mat_param_k_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_k_struct)
                    mat_param_k_struct_len = readlong(trmtr)

                    if mat_param_k_struct_len != 0x0000:
                        raise Exception(f"Unexpected mat_param_k struct length!")

                if mat_struct_ptr_param_l != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_l)
                    mat_param_l_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_l_start)
                    mat_param_l_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_l_struct)
                    mat_param_l_struct_len = readlong(trmtr)

                    if mat_param_l_struct_len != 0x0000:
                        raise Exception(f"Unexpected mat_param_l struct length!")

                if mat_struct_ptr_param_m != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_m)
                    mat_param_m_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_m_start)
                    mat_param_m_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_m_struct)
                    mat_param_m_struct_len = readlong(trmtr)

                    if mat_param_m_struct_len != 0x0000:
                        raise Exception(f"Unexpected mat_param_m struct length!")

                if mat_struct_ptr_param_n != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_n)
                    mat_param_n_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_n_start)
                    mat_param_n_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_n_struct)
                    mat_param_n_struct_len = readshort(trmtr)

                    if mat_param_n_struct_len == 0x0004:
                        mat_param_n_struct_section_len = readshort(trmtr)
                        mat_param_n_struct_unk = 0
                    elif mat_param_n_struct_len == 0x0006:
                        mat_param_n_struct_section_len = readshort(trmtr)
                        mat_param_n_struct_unk = readshort(trmtr)
                    else:
                        raise Exception(f"Unexpected mat_param_n struct length!")

                    if mat_param_n_struct_unk != 0:
                        fseek(trmtr, mat_param_n_start + mat_param_n_struct_unk)
                        mat_param_n_value =  readbyte(trmtr)
                        print(f"Unknown value A = {mat_param_n_value}")

                if mat_struct_ptr_param_o != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_o)
                    mat_param_o_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_o_start)
                    mat_param_o_struct = ftell(trmtr) - readlong(trmtr); fseek(trmtr, mat_param_o_struct)
                    mat_param_o_struct_len = readshort(trmtr)

                    if mat_param_o_struct_len == 0x0004:
                        mat_param_o_struct_section_len = readshort(trmtr)
                        mat_param_o_struct_unk = 0
                        mat_param_o_struct_value = 0
                    elif mat_param_o_struct_len == 0x0008:
                        mat_param_o_struct_section_len = readshort(trmtr)
                        mat_param_o_struct_unk = readshort(trmtr)
                        mat_param_o_struct_value = readshort(trmtr)
                    else:
                        raise Exception(f"Unexpected mat_param_o struct length!")

                    if mat_param_o_struct_unk != 0:
                        fseek(trmtr, mat_param_o_start + mat_param_o_struct_unk)
                        mat_param_o_value =  readbyte(trmtr)
                        print(f"Unknown value B = {mat_param_o_value}")

                if mat_struct_ptr_param_p != 0:
                    fseek(trmtr, mat_offset + mat_struct_ptr_param_p)
                    mat_param_p_start = ftell(trmtr) + readlong(trmtr); fseek(trmtr, mat_param_p_start)
                    mat_param_p_string_len = readlong(trmtr)
                    mat_param_p_string = readfixedstring(trmtr, mat_param_p_string_len)
                    print(mat_param_p_string)

                mat_data_array.append({
                    "mat_name": mat_name,
                    "mat_shader": mat_shader,
                    "mat_col0": mat_col0,
                    "mat_lym0": mat_lym0,
                    "mat_nrm0": mat_nrm0,
                    "mat_ao0": mat_ao0,
                    "mat_emi0": mat_emi0,
                    "mat_rgh0": mat_rgh0,
                    "mat_mtl0": mat_mtl0,
                    "mat_msk0": mat_msk0,
                    "mat_highmsk0": mat_highmsk0,
                    "mat_color1_r": mat_color1_r, "mat_color1_g": mat_color1_g, "mat_color1_b": mat_color1_b,
                    "mat_color2_r": mat_color2_r, "mat_color2_g": mat_color2_g, "mat_color2_b": mat_color2_b,
                    "mat_color3_r": mat_color3_r, "mat_color3_g": mat_color3_g, "mat_color3_b": mat_color3_b,
                    "mat_color4_r": mat_color4_r, "mat_color4_g": mat_color4_g, "mat_color4_b": mat_color4_b,
                    "mat_emcolor1_r": mat_emcolor1_r, "mat_emcolor1_g": mat_emcolor1_g, "mat_emcolor1_b": mat_emcolor1_b,
                    "mat_emcolor2_r": mat_emcolor2_r, "mat_emcolor2_g": mat_emcolor2_g, "mat_emcolor2_b": mat_emcolor2_b,
                    "mat_emcolor3_r": mat_emcolor3_r, "mat_emcolor3_g": mat_emcolor3_g, "mat_emcolor3_b": mat_emcolor3_b,
                    "mat_emcolor4_r": mat_emcolor4_r, "mat_emcolor4_g": mat_emcolor4_g, "mat_emcolor4_b": mat_emcolor4_b,
                    "mat_emcolor5_r": mat_emcolor5_r, "mat_emcolor5_g": mat_emcolor5_g, "mat_emcolor5_b": mat_emcolor5_b,
                    "mat_rgh_layer0": mat_rgh_layer0, "mat_rgh_layer1": mat_rgh_layer1, "mat_rgh_layer2": mat_rgh_layer2, "mat_rgh_layer3": mat_rgh_layer3, "mat_rgh_layer4": mat_rgh_layer4,
                    "mat_mtl_layer0": mat_mtl_layer0, "mat_mtl_layer1": mat_mtl_layer1, "mat_mtl_layer2": mat_mtl_layer2, "mat_mtl_layer3": mat_mtl_layer3, "mat_mtl_layer4": mat_mtl_layer4,
                    "mat_reflectance": mat_reflectance,
                    "mat_emm_intensity": mat_emm_intensity,
                    "mat_uv_scale_u": mat_uv_scale_u, "mat_uv_scale_v": mat_uv_scale_v,
                    "mat_uv_scale2_u": mat_uv_scale2_u, "mat_uv_scale2_v": mat_uv_scale2_v,
                    "mat_enable_base_color_map": mat_enable_base_color_map,
                    "mat_enable_normal_map": mat_enable_normal_map,
                    "mat_enable_ao_map": mat_enable_ao_map,
                    "mat_enable_emission_color_map": mat_enable_emission_color_map,
                    "mat_enable_roughness_map": mat_enable_roughness_map,
                    "mat_enable_metallic_map": mat_enable_metallic_map,
                    "mat_enable_displacement_map": mat_enable_displacement_map,
                    "mat_enable_highlight_map": mat_enable_highlight_map
                })
                fseek(trmtr, mat_ret)
            print("--------------------")

        fclose(trmtr)

        if IN_BLENDER_ENV:
            # process materials
            for m, mat in enumerate(mat_data_array):
                material = bpy.data.materials.new(name=mat["mat_name"])
                material.use_nodes = True
                materials.append(material)

                blend_type = "MIX"

                material_output = material.node_tree.nodes.get("Material Output")
                principled_bsdf = material.node_tree.nodes.get("Principled BSDF")
                material.node_tree.links.new(principled_bsdf.outputs[0], material_output.inputs[0])

                print(f"mat_shader = {mat['mat_shader']}")
                
                material.blend_method = ("HASHED")
                material.shadow_method = ("OPAQUE")
                
                color_output = principled_bsdf.inputs[0]
                if mat["mat_shader"] == "Unlit":
                    color_output = material_output.inputs[0]
                if mat["mat_shader"] == "Transparent":
                    material.blend_method = ("BLEND")
                    reflectionpart1 = material.node_tree.nodes.new("ShaderNodeMath")
                    reflectionpart1.operation = "SQRT"
                    reflectionpart1.inputs[0].default_value = mat["mat_reflectance"]

                    reflectionpart2 = material.node_tree.nodes.new("ShaderNodeMath")
                    reflectionpart2.inputs[0].default_value = 1.0
                    reflectionpart2.operation = "ADD"
                    
                    reflectionpart3 = material.node_tree.nodes.new("ShaderNodeMath")
                    reflectionpart3.inputs[0].default_value = 1.0
                    reflectionpart3.operation = "SUBTRACT"

                    reflectionpart4 = material.node_tree.nodes.new("ShaderNodeMath")
                    reflectionpart4.operation = "DIVIDE"

                    reflectionpart5 = material.node_tree.nodes.new("ShaderNodeFresnel")
 
                    reflectionpart6 = material.node_tree.nodes.new("ShaderNodeMath")
                    reflectionpart6.inputs[0].default_value = 0.25
                    reflectionpart6.operation = "SUBTRACT"
 
                    material.node_tree.links.new(reflectionpart1.outputs[0], reflectionpart2.inputs[1])
                    material.node_tree.links.new(reflectionpart1.outputs[0], reflectionpart3.inputs[1])
                    material.node_tree.links.new(reflectionpart2.outputs[0], reflectionpart4.inputs[0])
                    material.node_tree.links.new(reflectionpart3.outputs[0], reflectionpart4.inputs[1])
                    material.node_tree.links.new(reflectionpart4.outputs[0], reflectionpart5.inputs[0])
                    
                material.use_backface_culling = True

                    
                if chara_check == "Pokemon" or mat["mat_name"] == "eye":
                    # LAYER MASK MAP
                    
                    lym_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                    if os.path.exists(os.path.join(filep, mat["mat_lym0"][:-5] + textureextension)) == True:
                        lym_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_lym0"][:-5] + textureextension))
                        lym_image_texture.image.colorspace_settings.name = "Non-Color"
                    huesaturationvalue = material.node_tree.nodes.new("ShaderNodeHueSaturation")
                    huesaturationvalue.inputs[2].default_value = 2.0
                    huesaturationvalue2 = material.node_tree.nodes.new("ShaderNodeHueSaturation")
                    huesaturationvalue2.inputs[2].default_value = 2.0
    
                    color1 = (mat["mat_color1_r"], mat["mat_color1_g"], mat["mat_color1_b"], 1.0)
                    color2 = (mat["mat_color2_r"], mat["mat_color2_g"], mat["mat_color2_b"], 1.0)
                    color3 = (mat["mat_color3_r"], mat["mat_color3_g"], mat["mat_color3_b"], 1.0)
                    color4 = (mat["mat_color4_r"], mat["mat_color4_g"], mat["mat_color4_b"], 1.0)
                    
                    
                    emcolor1 = (mat["mat_emcolor1_r"], mat["mat_emcolor1_g"], mat["mat_emcolor1_b"], 1.0)
                    emcolor2 = (mat["mat_emcolor2_r"], mat["mat_emcolor2_g"], mat["mat_emcolor2_b"], 1.0)
                    emcolor3 = (mat["mat_emcolor3_r"], mat["mat_emcolor3_g"], mat["mat_emcolor3_b"], 1.0)                   
                    emcolor4 = (mat["mat_emcolor4_r"], mat["mat_emcolor4_g"], mat["mat_emcolor4_b"], 1.0)
                    if emcolor1 == (1.0, 1.0, 1.0, 1.0) and emcolor2 == (1.0, 1.0, 1.0, 1.0) and emcolor3 == (1.0, 1.0, 1.0, 1.0) and emcolor4 == (1.0, 1.0, 1.0, 1.0):
                        emcolor1 = (0.0, 0.0, 0.0, 0.0)
                        emcolor2 = (0.0, 0.0, 0.0, 0.0)
                        emcolor3 = (0.0, 0.0, 0.0, 0.0)
                        emcolor4 = (0.0, 0.0, 0.0, 0.0)
                    print(f'Material {mat["mat_name"]}:')
                    print(f"Color 1: {color1}")
                    print(f"Color 2: {color2}")
                    print(f"Color 3: {color3}")
                    print(f"Color 4: {color4}")
                    print(f"Emission Color 1: {emcolor1}")
                    print(f"Emission Color 2: {emcolor2}")
                    print(f"Emission Color 3: {emcolor3}")
                    print(f"Emission Color 4: {emcolor4}")
                    print("---")
     
                    mix_color1 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                    mix_color1.blend_type = blend_type
                    mix_color1.inputs[1].default_value = (1, 1, 1, 1)
                    mix_color1.inputs[2].default_value = color1
                    mix_color2 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                    mix_color2.blend_type = blend_type
                    mix_color2.inputs[1].default_value = (0, 0, 0, 0)
                    mix_color2.inputs[2].default_value = color2
                    mix_color3 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                    mix_color3.blend_type = blend_type
                    mix_color3.inputs[1].default_value = (0, 0, 0, 0)
                    mix_color3.inputs[2].default_value = color3
                    mix_color4 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                    mix_color4.blend_type = blend_type
                    mix_color4.inputs[1].default_value = (0, 0, 0, 0)
                    mix_color4.inputs[2].default_value = color4
                    mix_color5 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                    mix_color5.blend_type = blend_type
                    mix_color5.inputs[0].default_value = 0.0
                    mix_color5.inputs[1].default_value = (0, 0, 0, 0)
                    mix_color5.inputs[2].default_value = (1, 1, 1, 1)
                    
                    
                    
                    mix_emcolor1 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                    mix_emcolor1.blend_type = blend_type
                    mix_emcolor1.inputs[1].default_value = (0, 0, 0, 0)
                    mix_emcolor1.inputs[2].default_value = emcolor1
                    mix_emcolor2 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                    mix_emcolor2.blend_type = blend_type
                    mix_emcolor2.inputs[1].default_value = (0, 0, 0, 0)
                    mix_emcolor2.inputs[2].default_value = emcolor2
                    mix_emcolor3 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                    mix_emcolor3.blend_type = blend_type
                    mix_emcolor3.inputs[1].default_value = (0, 0, 0, 0)
                    mix_emcolor3.inputs[2].default_value = emcolor3
                    mix_emcolor4 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                    mix_emcolor4.blend_type = blend_type
                    mix_emcolor4.inputs[1].default_value = (0, 0, 0, 0)
                    mix_emcolor4.inputs[2].default_value = emcolor4
                    
                    material.node_tree.links.new(mix_color1.outputs[0], mix_color2.inputs[1])
                    material.node_tree.links.new(mix_color2.outputs[0], mix_color3.inputs[1])
                    material.node_tree.links.new(mix_color3.outputs[0], mix_color4.inputs[1])
                    material.node_tree.links.new(mix_color3.outputs[0], mix_color4.inputs[1])
                    material.node_tree.links.new(mix_color4.outputs[0], color_output)

                    material.node_tree.links.new(mix_emcolor1.outputs[0], mix_emcolor2.inputs[1])
                    material.node_tree.links.new(mix_emcolor2.outputs[0], mix_emcolor3.inputs[1])
                    material.node_tree.links.new(mix_emcolor3.outputs[0], mix_emcolor4.inputs[1])
                    material.node_tree.links.new(mix_emcolor3.outputs[0], mix_emcolor4.inputs[1])
                    material.node_tree.links.new(mix_emcolor4.outputs[0], principled_bsdf.inputs[19]) 
              
                    
                    separate_color = material.node_tree.nodes.new("ShaderNodeSeparateRGB")
                    material.node_tree.links.new(lym_image_texture.outputs[0], huesaturationvalue.inputs[4])
                    material.node_tree.links.new(huesaturationvalue.outputs[0], separate_color.inputs[0])
                    material.node_tree.links.new(separate_color.outputs[0], mix_color1.inputs[0])
                    material.node_tree.links.new(separate_color.outputs[1], mix_color2.inputs[0])
                    material.node_tree.links.new(separate_color.outputs[2], mix_color3.inputs[0])
                    material.node_tree.links.new(lym_image_texture.outputs[1],  huesaturationvalue2.inputs[4])
                    material.node_tree.links.new(huesaturationvalue2.outputs[0],  mix_color4.inputs[0])

                    material.node_tree.links.new(separate_color.outputs[0], mix_emcolor1.inputs[0])
                    material.node_tree.links.new(separate_color.outputs[1], mix_emcolor2.inputs[0])
                    material.node_tree.links.new(separate_color.outputs[2], mix_emcolor3.inputs[0])
                    material.node_tree.links.new(huesaturationvalue2.outputs[0],  mix_emcolor4.inputs[0])
    
                
                    
                    if os.path.exists(os.path.join(filep, mat["mat_col0"][:-5] + textureextension)) == True:
                        alb_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                        alb_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_col0"][:-5] + textureextension))
                        material.node_tree.links.new(alb_image_texture.outputs[0], mix_color1.inputs[1])
                        material.node_tree.links.new(alb_image_texture.outputs[1],  principled_bsdf.inputs[21])

                    if mat["mat_enable_highlight_map"]:
                        highlight_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")                        
                        if os.path.exists(os.path.join(filep, mat["mat_highmsk0"][:-5] + ".png")) == True:
                            highlight_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_highmsk0"][:-5] + ".png"))
                            highlight_image_texture.image.colorspace_settings.name = "Non-Color"
                        elif os.path.exists(os.path.join(filep, mat["mat_col0"][:-8] + "msk.png")) == True:
                            highlight_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_col0"][:-8] + "msk.png"))
                            highlight_image_texture.image.colorspace_settings.name = "Non-Color"
                        elif os.path.exists(os.path.join(filep, mat["mat_col0"][:-8] + "msk.png")) == True:
                            highlight_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_col0"][:-8] + "msk.png"))
                            highlight_image_texture.image.colorspace_settings.name = "Non-Color"
                        elif os.path.exists(os.path.join(filep, mat["mat_col0"][:-12] + "r_eye_msk.png")) == True:
                            highlight_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_col0"][:-12] + "r_eye_msk.png"))
                            highlight_image_texture.image.colorspace_settings.name = "Non-Color"
                        elif os.path.exists(os.path.join(filep, mat["mat_col0"][:-12] + "l_eye_msk.png")) == True:
                            highlight_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_col0"][:-12] + "l_eye_msk.png"))
                            highlight_image_texture.image.colorspace_settings.name = "Non-Color"
                        else:
                            print("No Highlight")
                        material.node_tree.links.new(highlight_image_texture.outputs[0],  mix_color5.inputs[0])
                        material.node_tree.links.new(mix_color4.outputs[0], mix_color5.inputs[1])
                        material.node_tree.links.new(mix_color5.outputs[0], color_output)
                        
                        
                    if mat["mat_enable_normal_map"]:
                        normal_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                        if os.path.exists(os.path.join(filep, mat["mat_nrm0"][:-5] + textureextension)) == True:
                            normal_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_nrm0"][:-5] + textureextension))
                            normal_image_texture.image.colorspace_settings.name = "Non-Color"
                        separate_color2 = material.node_tree.nodes.new("ShaderNodeSeparateRGB")
                        combine_color2 = material.node_tree.nodes.new("ShaderNodeCombineColor")
                        normal_map2 = material.node_tree.nodes.new("ShaderNodeNormalMap")
                        material.node_tree.links.new(normal_image_texture.outputs[0], separate_color2.inputs[0])
                        material.node_tree.links.new(separate_color2.outputs[0], combine_color2.inputs[0])
                        material.node_tree.links.new(separate_color2.outputs[1], combine_color2.inputs[1])
                        material.node_tree.links.new(normal_image_texture.outputs[1], combine_color2.inputs[2])
                        material.node_tree.links.new(combine_color2.outputs[0], normal_map2.inputs[1])
                        material.node_tree.links.new(normal_map2.outputs[0], principled_bsdf.inputs[22])
                        if mat["mat_shader"] == "Transparent":
                            material.node_tree.links.new(normal_map2.outputs[0], reflectionpart5.inputs[1])
                            material.node_tree.links.new(reflectionpart5.outputs[0], reflectionpart6.inputs[1])                            
                            material.node_tree.links.new(reflectionpart6.outputs[0], principled_bsdf.inputs[21])
                        
                    if mat["mat_enable_metallic_map"]:
                        metalness_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                        if os.path.exists(os.path.join(filep, mat["mat_mtl0"][:-5] + textureextension)) == True:
                            metalness_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_mtl0"][:-5] + textureextension))
                            metalness_image_texture.image.colorspace_settings.name = "Non-Color"
                        material.node_tree.links.new(metalness_image_texture.outputs[0], principled_bsdf.inputs[6])

                    if mat["mat_enable_emission_color_map"]:
                        emission_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                        if os.path.exists(os.path.join(filep, mat["mat_emi0"][:-5] + textureextension)) == True:
                            emission_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_emi0"][:-5] + textureextension))
                        material.node_tree.links.new(emission_image_texture.outputs[0], principled_bsdf.inputs[19])                        
                        
                    if mat["mat_enable_roughness_map"]:
                        roughness_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                        if os.path.exists(os.path.join(filep, mat["mat_rgh0"][:-5] + textureextension)) == True:
                            roughness_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_rgh0"][:-5] + textureextension))
                            roughness_image_texture.image.colorspace_settings.name = "Non-Color"
                        material.node_tree.links.new(roughness_image_texture.outputs[0], principled_bsdf.inputs[9])
                        
                    if mat["mat_enable_ao_map"]:
                        ambientocclusion_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                        if os.path.exists(os.path.join(filep, mat["mat_ao0"][:-5] + textureextension)) == True:            
                            ambientocclusion_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_ao0"][:-5] + textureextension))
                            ambientocclusion_image_texture.image.colorspace_settings.name = "Non-Color"
                        mix_color6 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                        mix_color6.blend_type = "MULTIPLY"
                        if mat["mat_ao0"][:-5] == "../../glb_share_tex/texture_white_ao/texture_white_ao":
                            mix_color6.inputs[0].default_value = 0
                        else:
                            mix_color6.inputs[0].default_value = 1.0
                        if mix_color5 == True:
                            material.node_tree.links.new(mix_color5.outputs[0], mix_color6.inputs[0])
                            material.node_tree.links.new(ambientocclusion_image_texture.outputs[0], mix_color6.inputs[1])
                            material.node_tree.links.new(mix_color6.outputs[0], color_output)
                        else:
                            material.node_tree.links.new(mix_color4.outputs[0], mix_color6.inputs[1])
                            material.node_tree.links.new(ambientocclusion_image_texture.outputs[0], mix_color6.inputs[2])
                            material.node_tree.links.new(mix_color6.outputs[0], color_output)
                    if os.path.exists(os.path.join(filep, mat["mat_col0"][:-5] + textureextension)) == True:
                        if color1 == (1.0, 1.0, 1.0, 1.0) and color2 == (1.0, 1.0, 1.0, 1.0) and color3 == (1.0, 1.0, 1.0, 1.0) and color4 == (1.0, 1.0, 1.0, 1.0):
                            if mat["mat_enable_ao_map"]:
                                material.node_tree.links.new(alb_image_texture.outputs[0],  mix_color6.inputs[1])
                            else:
                                material.node_tree.links.new(alb_image_texture.outputs[0],  mix_color5.inputs[1])

                        
                else:
                    if mat["mat_enable_base_color_map"]:
                        alb_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                        if os.path.exists(os.path.join(filep, mat["mat_col0"][:-5] + textureextension)) == True:
                            alb_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_col0"][:-5] + textureextension))
                        material.node_tree.links.new(alb_image_texture.outputs[0], color_output)
                        material.node_tree.links.new(alb_image_texture.outputs[1],  principled_bsdf.inputs[21])



                    if mat["mat_enable_highlight_map"]:
                        highlight_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                        if os.path.exists(os.path.join(filep, mat["mat_highmsk0"][:-5] + ".png")) == True:
                            highlight_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_highmsk0"][:-5] + ".png"))
                            highlight_image_texture.image.colorspace_settings.name = "Non-Color"
                        else:
                            highlight_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_col0"][:-8] + "msk.png"))
                            highlight_image_texture.image.colorspace_settings.name = "Non-Color"                        
                        material.node_tree.links.new(highlight_image_texture.outputs[0],  mix_color5.inputs[0])
                        material.node_tree.links.new(mix_color4.outputs[0], mix_color5.inputs[1])
                        material.node_tree.links.new(mix_color5.outputs[0], color_output)

                    if mat["mat_enable_normal_map"]:
                        normal_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                        if os.path.exists(os.path.join(filep, mat["mat_nrm0"][:-5] + textureextension)) == True:
                            normal_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_nrm0"][:-5] + textureextension))
                            normal_image_texture.image.colorspace_settings.name = "Non-Color"
                        separate_color2 = material.node_tree.nodes.new("ShaderNodeSeparateRGB")
                        combine_color2 = material.node_tree.nodes.new("ShaderNodeCombineColor")
                        normal_map2 = material.node_tree.nodes.new("ShaderNodeNormalMap")
                        material.node_tree.links.new(normal_image_texture.outputs[0], separate_color2.inputs[0])
                        material.node_tree.links.new(separate_color2.outputs[0], combine_color2.inputs[0])
                        material.node_tree.links.new(separate_color2.outputs[1], combine_color2.inputs[1])
                        material.node_tree.links.new(normal_image_texture.outputs[1], combine_color2.inputs[2])
                        material.node_tree.links.new(combine_color2.outputs[0], normal_map2.inputs[1])
                        material.node_tree.links.new(normal_map2.outputs[0], principled_bsdf.inputs[22])
                        if mat["mat_shader"] == "Transparent":
                            material.node_tree.links.new(normal_map2.outputs[0], reflectionpart5.inputs[1])
                            material.node_tree.links.new(reflectionpart5.outputs[0], principled_bsdf.inputs[21])

                    if mat["mat_enable_emission_color_map"]:
                        emission_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                        if os.path.exists(os.path.join(filep, mat["mat_emi0"][:-5] + textureextension)) == True:
                            emission_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_emi0"][:-5] + textureextension))
                        material.node_tree.links.new(emission_image_texture.outputs[0], principled_bsdf.inputs[19])    
                        
                    if mat["mat_enable_metallic_map"]:
                        metalness_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                        if os.path.exists(os.path.join(filep, mat["mat_mtl0"][:-5] + textureextension)) == True:
                            metalness_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_mtl0"][:-5] + textureextension))
                            metalness_image_texture.image.colorspace_settings.name = "Non-Color"
                        material.node_tree.links.new(metalness_image_texture.outputs[0], principled_bsdf.inputs[6])
                        
                    if mat["mat_enable_roughness_map"]:
                        roughness_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                        if os.path.exists(os.path.join(filep, mat["mat_rgh0"][:-5] + textureextension)) == True:
                            roughness_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_rgh0"][:-5] + textureextension))
                            roughness_image_texture.image.colorspace_settings.name = "Non-Color"
                        material.node_tree.links.new(roughness_image_texture.outputs[0], principled_bsdf.inputs[9])  
                        
                    if mat["mat_enable_ao_map"]:
                        ambientocclusion_image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                        if os.path.exists(os.path.join(filep, mat["mat_ao0"][:-5] + textureextension)) == True:
                            ambientocclusion_image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_ao0"][:-5] + textureextension))
                            ambientocclusion_image_texture.image.colorspace_settings.name = "Non-Color"
                        mix_color6 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                        mix_color6.blend_type = "MULTIPLY"
                        if mat["mat_ao0"][:-5] == "../../glb_share_tex/texture_white_ao/texture_white_ao":
                            mix_color6.inputs[0].default_value = 0
                        else:
                            mix_color6.inputs[0].default_value = 1.0
                        material.node_tree.links.new(alb_image_texture.outputs[0], mix_color6.inputs[1])
                        material.node_tree.links.new(ambientocclusion_image_texture.outputs[0], mix_color6.inputs[2])
                        material.node_tree.links.new(mix_color6.outputs[0], color_output)

    if loadlods == False:
        trmsh_count = 1
                        
    for w in range(trmsh_count):
        if os.path.exists(os.path.join(filep, trmsh_lods_array[w])):
            poly_group_array = []
            trmsh = open(os.path.join(filep, trmsh_lods_array[w]), "rb")
            trmsh_file_start = readlong(trmsh)
            print("Parsing TRMSH...")
            fseek(trmsh, trmsh_file_start)
            trmsh_struct = ftell(trmsh) - readlong(trmsh); fseek(trmsh, trmsh_struct)
            trmsh_struct_len = readshort(trmsh)

            if trmsh_struct_len != 0x000A:
                raise AssertionError("Unexpected TRMSH header struct length!")
            trmsh_struct_section_len = readshort(trmsh)
            trmsh_struct_start = readshort(trmsh)
            trmsh_struct_poly_group = readshort(trmsh)
            trmsh_struct_trmbf = readshort(trmsh)

            if trmsh_struct_trmbf != 0:
                fseek(trmsh, trmsh_file_start + trmsh_struct_trmbf)
                trmbf_filename_start = ftell(trmsh) + readlong(trmsh)
                fseek(trmsh, trmbf_filename_start)
                trmbf_filename_len = readlong(trmsh)
                trmbf_filename = readfixedstring(trmsh, trmbf_filename_len)
                print(trmbf_filename)

                trmbf = None
                if os.path.exists(os.path.join(filep, trmbf_filename)):
                    trmbf = open(os.path.join(filep, trmbf_filename), "rb")
                else:
                    raise AssertionError(f"Can't find {trmbf_filename}!")

                if trmbf != None:
                    print("Parsing TRMBF...")
                    trmbf_file_start = readlong(trmbf); fseek(trmbf, trmbf_file_start)
                    trmbf_struct = ftell(trmbf) - readlong(trmbf); fseek(trmbf, trmbf_struct)
                    trmbf_struct_len = readshort(trmbf)

                    if trmbf_struct_len != 0x0008:
                        raise AssertionError("Unexpected TRMBF header struct length!")
                    trmbf_struct_section_len = readshort(trmbf)
                    trmbf_struct_start = readshort(trmbf)
                    trmbf_struct_buffer = readshort(trmbf)

                    if trmsh_struct_poly_group != 0:
                        fseek(trmsh, trmsh_file_start + trmsh_struct_poly_group)
                        poly_group_start = ftell(trmsh) + readlong(trmsh)
                        fseek(trmsh, poly_group_start)
                        poly_group_count = readlong(trmsh)

                        fseek(trmbf, trmbf_file_start + trmbf_struct_buffer)
                        vert_buffer_start = ftell(trmbf) + readlong(trmbf)
                        vert_buffer_count = readlong(trmbf)

                        for x in range(poly_group_count):
                            vert_array = []
                            normal_array = []
                            color_array = []
                            alpha_array = []
                            uv_array = []
                            uv2_array = []
                            uv3_array = []
                            uv4_array = []
                            face_array = []
                            face_mat_id_array = []
                            b1_array = []
                            w1_array = []
                            weight_array = []
                            poly_group_name = ""; vis_group_name = ""; vert_buffer_stride = 0; mat_id = 0
                            positions_fmt = "None"; normals_fmt = "None"; tangents_fmt = "None"; bitangents_fmt = "None"; tritangents_fmt = "None"
                            uvs_fmt = "None"; uvs2_fmt = "None"; uvs3_fmt = "None"; uvs4_fmt = "None"
                            colors_fmt = "None"; colors2_fmt = "None"; bones_fmt = "None"; weights_fmt = "None"; svunk_fmt = "None"

                            poly_group_offset = ftell(trmsh) + readlong(trmsh)
                            poly_group_ret = ftell(trmsh)
                            fseek(trmsh, poly_group_offset)
                            print(f"PolyGroup offset #{x}: {hex(poly_group_offset)}")
                            poly_group_struct = ftell(trmsh) - readlong(trmsh)
                            fseek(trmsh, poly_group_struct)
                            poly_group_struct_len = readshort(trmsh)


                            poly_group_struct_section_len = readshort(trmsh)
                            poly_group_struct_ptr_poly_group_name = readshort(trmsh)
                            poly_group_struct_ptr_bbbox = readshort(trmsh)
                            poly_group_struct_ptp_unc_a = readshort(trmsh)
                            poly_group_struct_ptr_vert_buff = readshort(trmsh)
                            poly_group_struct_ptr_mat_list = readshort(trmsh)
                            poly_group_struct_ptr_unk_b = readshort(trmsh)
                            poly_group_struct_ptr_unk_c = readshort(trmsh)
                            poly_group_struct_ptr_unk_d = readshort(trmsh)
                            poly_group_struct_ptr_unk_e = readshort(trmsh)
                            poly_group_struct_ptr_unk_float = readshort(trmsh)
                            poly_group_struct_ptr_unk_g = readshort(trmsh)
                            poly_group_struct_ptr_unk_h = readshort(trmsh)
                            poly_group_struct_ptr_vis_group_name = readshort(trmsh)

                            if poly_group_struct_ptr_mat_list != 0:
                                fseek(trmsh, poly_group_offset + poly_group_struct_ptr_mat_list)
                                mat_offset = ftell(trmsh) + readlong(trmsh)
                                fseek(trmsh, mat_offset)
                                mat_count = readlong(trmsh)
                                for y in range(mat_count):
                                    mat_entry_offset = ftell(trmsh) + readlong(trmsh)
                                    mat_ret = ftell(trmsh)
                                    fseek(trmsh, mat_entry_offset)
                                    mat_struct = ftell(trmsh) - readlong(trmsh)
                                    fseek(trmsh, mat_struct)
                                    mat_struct_len = readshort(trmsh)

                                    if mat_struct_len != 0x000E:
                                        raise AssertionError("Unexpected material struct length!")
                                    mat_struct_section_len = readshort(trmsh)
                                    mat_struct_ptr_facepoint_count = readshort(trmsh)
                                    mat_struct_ptr_facepoint_start = readshort(trmsh)
                                    mat_struct_ptr_unk_c = readshort(trmsh)
                                    mat_struct_ptr_string = readshort(trmsh)
                                    mat_struct_ptr_unk_d = readshort(trmsh)

                                    if mat_struct_ptr_facepoint_count != 0:
                                        fseek(trmsh, mat_entry_offset + mat_struct_ptr_facepoint_count)
                                        mat_facepoint_count = int(readlong(trmsh) / 3)

                                    if mat_struct_ptr_facepoint_start != 0:
                                        fseek(trmsh, mat_entry_offset + mat_struct_ptr_facepoint_start)
                                        mat_facepoint_start = int(readlong(trmsh) / 3)
                                    else: mat_facepoint_start = 0

                                    if mat_struct_ptr_unk_c != 0:
                                        fseek(trmsh, mat_entry_offset + mat_struct_ptr_unk_c)
                                        mat_unk_c = readlong(trmsh)

                                    if mat_struct_ptr_string != 0:
                                        fseek(trmsh, mat_entry_offset + mat_struct_ptr_string)
                                        mat_name_offset = ftell(trmsh) + readlong(trmsh)
                                        fseek(trmsh, mat_name_offset)
                                        mat_name_len = readlong(trmsh)
                                        mat_name = readfixedstring(trmsh, mat_name_len)

                                    if mat_struct_ptr_unk_d != 0:
                                        fseek(trmsh, mat_entry_offset + mat_struct_ptr_unk_d)
                                        mat_unk_d = readlong(trmsh)

                                    mat_id = 0
                                    for z in range(len(mat_data_array)):
                                        if mat_data_array[z]["mat_name"] == mat_name:
                                            mat_id = z
                                            break

                                    for z in range(mat_facepoint_count):
                                        face_mat_id_array.append(mat_id)

                                    print(f"Material {mat_name}: FaceCount = {mat_facepoint_count}, FaceStart = {mat_facepoint_start}")
                                    fseek(trmsh, mat_ret)

                            if poly_group_struct_ptr_poly_group_name != 0:
                                fseek(trmsh, poly_group_offset + poly_group_struct_ptr_poly_group_name)
                                poly_group_name_offset = ftell(trmsh) + readlong(trmsh); fseek(trmsh, poly_group_name_offset)
                                poly_group_name_len = readlong(trmsh)
                                poly_group_name = readfixedstring(trmsh, poly_group_name_len)
                                print(f"Building {poly_group_name}...")
                            if poly_group_struct_ptr_vis_group_name != 0:
                                fseek(trmsh, poly_group_offset + poly_group_struct_ptr_vis_group_name)
                                vis_group_name_offset = ftell(trmsh) + readlong(trmsh); fseek(trmsh, vis_group_name_offset)
                                vis_group_name_len = readlong(trmsh)
                                vis_group_name = readfixedstring(trmsh, vis_group_name_len)
                                # changed the output variable because the original seems to be a typo
                                print(f"VisGroup: {vis_group_name}")
                            if poly_group_struct_ptr_vert_buff != 0:
                                fseek(trmsh, poly_group_offset + poly_group_struct_ptr_vert_buff)
                                poly_group_vert_buff_offset = ftell(trmsh) + readlong(trmsh)
                                fseek(trmsh, poly_group_vert_buff_offset)
                                vert_buff_count = readlong(trmsh)
                                vert_buff_offset = ftell(trmsh) + readlong(trmsh)
                                fseek(trmsh, vert_buff_offset)
                                vert_buff_struct = ftell(trmsh) - readlong(trmsh)
                                fseek(trmsh, vert_buff_struct)
                                vert_buff_struct_len = readshort(trmsh)

                                if vert_buff_struct_len != 0x0008:
                                    raise AssertionError("Unexpected VertexBuffer struct length!")
                                vert_buff_struct_section_len = readshort(trmsh)
                                vert_buff_struct_ptr_param = readshort(trmsh)
                                vert_buff_struct_ptr_b = readshort(trmsh)

                                if vert_buff_struct_ptr_param != 0:
                                    fseek(trmsh, vert_buff_offset + vert_buff_struct_ptr_param)
                                    vert_buff_param_offset = ftell(trmsh) + readlong(trmsh)
                                    fseek(trmsh, vert_buff_param_offset)
                                    vert_buff_param_count = readlong(trmsh)
                                    for y in range(vert_buff_param_count):
                                        vert_buff_param_offset = ftell(trmsh) + readlong(trmsh)
                                        vert_buff_param_ret = ftell(trmsh)
                                        fseek(trmsh, vert_buff_param_offset)
                                        vert_buff_param_struct = ftell(trmsh) - readlong(trmsh)
                                        fseek(trmsh, vert_buff_param_struct)
                                        vert_buff_param_struct_len = readshort(trmsh)

                                        if vert_buff_param_struct_len == 0x000C:
                                            vert_buff_param_struct_section_len = readshort(trmsh)
                                            vert_buff_param_ptr_unk_a = readshort(trmsh)
                                            vert_buff_param_ptr_type = readshort(trmsh)
                                            vert_buff_param_ptr_layer = readshort(trmsh)
                                            vert_buff_param_ptr_fmt = readshort(trmsh)
                                            vert_buff_param_ptr_position = 0
                                        elif vert_buff_param_struct_len == 0x000E:
                                            vert_buff_param_struct_section_len = readshort(trmsh)
                                            vert_buff_param_ptr_unk_a = readshort(trmsh)
                                            vert_buff_param_ptr_type = readshort(trmsh)
                                            vert_buff_param_ptr_layer = readshort(trmsh)
                                            vert_buff_param_ptr_fmt = readshort(trmsh)
                                            vert_buff_param_ptr_position = readshort(trmsh)
                                        else:
                                            raise AssertionError("Unknown vertex buffer parameter struct length!")

                                        vert_buff_param_layer = 0

                                        if vert_buff_param_ptr_type != 0:
                                            fseek(trmsh, vert_buff_param_offset + vert_buff_param_ptr_type)
                                            vert_buff_param_type = readlong(trmsh)
                                        if vert_buff_param_ptr_layer != 0:
                                            fseek(trmsh, vert_buff_param_offset + vert_buff_param_ptr_layer)
                                            vert_buff_param_layer = readlong(trmsh)
                                        if vert_buff_param_ptr_fmt != 0:
                                            fseek(trmsh, vert_buff_param_offset + vert_buff_param_ptr_fmt)
                                            vert_buff_param_format = readlong(trmsh)
                                        if vert_buff_param_ptr_position != 0:
                                            fseek(trmsh, vert_buff_param_offset + vert_buff_param_ptr_position)
                                            vert_buff_param_position = readlong(trmsh)
                                        else:
                                            vert_buff_param_position = 0

                                        # -- Types:
                                        # -- 0x01: = Positions
                                        # -- 0x02 = Normals
                                        # -- 0x03 = Tangents
                                        # -- 0x05 = Colors
                                        # -- 0x06 = UVs
                                        # -- 0x07 = NodeIDs
                                        # -- 0x08 = Weights
                                        #
                                        # -- Formats:
                                        # -- 0x14 = 4 bytes as float
                                        # -- 0x16 = 4 bytes
                                        # -- 0x27 = 4 shorts as float
                                        # -- 0x2B = 4 half-floats
                                        # -- 0x30 = 2 floats
                                        # -- 0x33 = 3 floats
                                        # -- 0x36 = 4 floats

                                        if vert_buff_param_type == 0x01:
                                            if vert_buff_param_layer != 0:
                                                raise AssertionError("Unexpected positions layer!")

                                            if vert_buff_param_format != 0x33:
                                                raise AssertionError("Unexpected positions format!")

                                            positions_fmt = "3Floats"; vert_buffer_stride = vert_buffer_stride + 0x0C
                                        elif vert_buff_param_type == 0x02:
                                            if vert_buff_param_layer != 0:
                                                raise AssertionError("Unexpected normals layer!")

                                            if vert_buff_param_format != 0x2B:
                                                raise AssertionError("Unexpected normals format!")

                                            normals_fmt = "4HalfFloats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                        elif vert_buff_param_type == 0x03:
                                            if vert_buff_param_layer == 0:
                                                if vert_buff_param_format != 0x2B:
                                                    raise AssertionError("Unexpected tangents format!")

                                                tangents_fmt = "4HalfFloats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                            elif vert_buff_param_layer == 1:
                                                if vert_buff_param_format != 0x2B:
                                                    raise AssertionError("Unexpected bitangents format!")

                                                bitangents_fmt = "4HalfFloats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                            elif vert_buff_param_layer == 2:
                                                if vert_buff_param_format != 0x2B:
                                                    raise AssertionError("Unexpected tritangents format!")

                                                tritangents_fmt = "4HalfFloats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                            else:
                                                raise AssertionError("Unexpected tangents layer!")
                                        elif vert_buff_param_type == 0x05:
                                            if vert_buff_param_layer == 0:
                                                if vert_buff_param_format == 0x14:
                                                    colors_fmt = "4BytesAsFloat"; vert_buffer_stride = vert_buffer_stride + 0x04
                                                elif vert_buff_param_format == 0x36:
                                                    colors_fmt = "4Floats"; vert_buffer_stride = vert_buffer_stride + 0x10
                                                else:
                                                    raise AssertionError("Unexpected colors format!")
                                            elif vert_buff_param_layer == 1:
                                                if vert_buff_param_format == 0x14:
                                                    colors2_fmt = "4BytesAsFloat"; vert_buffer_stride = vert_buffer_stride + 0x04
                                                elif vert_buff_param_format == 0x36:
                                                    colors2_fmt = "4Floats"; vert_buffer_stride = vert_buffer_stride + 0x10
                                                else:
                                                    raise AssertionError("Unexpected colors2 format!")
                                        elif vert_buff_param_type == 0x06:
                                            if vert_buff_param_layer == 0:
                                                if vert_buff_param_format != 0x30:
                                                    raise AssertionError("Unexpected UVs format!")

                                                uvs_fmt = "2Floats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                            elif vert_buff_param_layer == 1:
                                                if vert_buff_param_format != 0x30:
                                                    raise AssertionError("Unexpected UVs2 format!")

                                                uvs2_fmt = "2Floats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                            elif vert_buff_param_layer == 2:
                                                if vert_buff_param_format != 0x30:
                                                    raise AssertionError("Unexpected UVs3 format!")

                                                uvs3_fmt = "2Floats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                            elif vert_buff_param_layer == 3:
                                                if vert_buff_param_format != 0x30:
                                                    raise AssertionError("Unexpected UVs4 format!")

                                                uvs4_fmt = "2Floats"; vert_buffer_stride = vert_buffer_stride + 0x08
                                            else:
                                                raise AssertionError("Unexpected UVs layer!")
                                        elif vert_buff_param_type == 0x07:
                                            if vert_buff_param_layer != 0:
                                                raise AssertionError("Unexpected node IDs layer!")

                                            if vert_buff_param_format != 0x16:
                                                raise AssertionError("Unexpected node IDs format!")

                                            bones_fmt = "4Bytes"; vert_buffer_stride = vert_buffer_stride + 0x04
                                        elif vert_buff_param_type == 0x08:
                                            if vert_buff_param_layer != 0:
                                                raise AssertionError("Unexpected weights layer!")

                                            if vert_buff_param_format != 0x27:
                                                raise AssertionError("Unexpected weights format!")

                                            weights_fmt = "4ShortsAsFloat"; vert_buffer_stride = vert_buffer_stride + 0x08
                                        elif vert_buff_param_type == 0x09:
                                            if vert_buff_param_layer != 0:
                                                raise AssertionError("Unexpected ?????? layer!")

                                            if vert_buff_param_format != 0x24:
                                                raise AssertionError("Unexpected ?????? layer!")

                                            svunk_fmt = "1Long?"; vert_buffer_stride = vert_buffer_stride + 0x04
                                        else:
                                            raise AssertionError("Unknown vertex type!")


                                        fseek(trmsh, vert_buff_param_ret)

                            poly_group_array.append(
                                {
                                    "poly_group_name": poly_group_name,
                                    "vis_group_name": vis_group_name,
                                    "vert_buffer_stride": vert_buffer_stride,
                                    "positions_fmt": positions_fmt,
                                    "normals_fmt": normals_fmt,
                                    "tangents_fmt": tangents_fmt,
                                    "bitangents_fmt": bitangents_fmt,
                                    "tritangents_fmt":tritangents_fmt,
                                    "uvs_fmt": uvs_fmt,
                                    "uvs2_fmt": uvs2_fmt,
                                    "uvs3_fmt": uvs3_fmt,
                                    "uvs4_fmt": uvs4_fmt,
                                    "colors_fmt": colors_fmt,
                                    "colors2_fmt": colors2_fmt,
                                    "bones_fmt": bones_fmt,
                                    "weights_fmt": weights_fmt,
                                    "svunk_fmt":svunk_fmt
                                }
                            )
                            fseek(trmsh, poly_group_ret)

                            vert_buffer_offset = ftell(trmbf) + readlong(trmbf)
                            vert_buffer_ret = ftell(trmbf)
                            fseek(trmbf, vert_buffer_offset)
                            vert_buffer_struct = ftell(trmbf) - readlong(trmbf); fseek(trmbf, vert_buffer_struct)
                            vert_buffer_struct_len = readshort(trmbf)

                            vert_buffer_struct_section_length = readshort(trmbf)
                            vert_buffer_struct_ptr_faces = readshort(trmbf)
                            vert_buffer_struct_ptr_verts = readshort(trmbf)

                            if vert_buffer_struct_ptr_verts != 0:
                                fseek(trmbf, vert_buffer_offset + vert_buffer_struct_ptr_verts)
                                vert_buffer_sub_start = ftell(trmbf) + readlong(trmbf); fseek(trmbf, vert_buffer_sub_start)
                                vert_buffer_sub_count = readlong(trmbf)

                                for y in range(vert_buffer_sub_count):
                                    vert_buffer_sub_offset = ftell(trmbf) + readlong(trmbf)
                                    vert_buffer_sub_ret = ftell(trmbf)
                                    fseek(trmbf, vert_buffer_sub_offset)
                                    if y == 0:
                                        print(f"Vertex buffer {x} header: {hex(ftell(trmbf))}")
                                    else:
                                        print(f"Vertex buffer {x} morph {y} header: {hex(ftell(trmbf))}")
                                    vert_buffer_sub_struct = ftell(trmbf) - readlong(trmbf); fseek(trmbf, vert_buffer_sub_struct)
                                    vert_buffer_sub_struct_len = readshort(trmbf)

                                    if vert_buffer_sub_struct_len != 0x0006:
                                        raise AssertionError("Unexpected vertex buffer struct length!")
                                    vert_buffer_sub_struct_section_length = readshort(trmbf)
                                    vert_buffer_sub_struct_ptr = readshort(trmbf)

                                    if vert_buffer_sub_struct_ptr != 0:
                                        fseek(trmbf, vert_buffer_sub_offset + vert_buffer_sub_struct_ptr)
                                        vert_buffer_start = ftell(trmbf) + readlong(trmbf); fseek(trmbf, vert_buffer_start)
                                        vert_buffer_byte_count = readlong(trmbf)
                                        if y == 0:
                                            print(f"Vertex buffer {x} start: {hex(ftell(trmbf))}")

                                            for v in range(vert_buffer_byte_count // poly_group_array[x]["vert_buffer_stride"]):
                                                if poly_group_array[x]["positions_fmt"] == "4HalfFloats":
                                                    vx = readhalffloat(trmbf)
                                                    vy = readhalffloat(trmbf)
                                                    vz = readhalffloat(trmbf)
                                                    vq = readhalffloat(trmbf)
                                                elif poly_group_array[x]["positions_fmt"] == "3Floats":
                                                    vx = readfloat(trmbf)
                                                    vy = readfloat(trmbf)
                                                    vz = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown positions type!")

                                                if poly_group_array[x]["normals_fmt"] == "4HalfFloats":
                                                    nx = readhalffloat(trmbf)
                                                    ny = readhalffloat(trmbf)
                                                    nz = readhalffloat(trmbf)
                                                    nq = readhalffloat(trmbf)
                                                elif poly_group_array[x]["normals_fmt"] == "3Floats":
                                                    nx = readfloat(trmbf)
                                                    ny = readfloat(trmbf)
                                                    nz = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown normals type!")

                                                if poly_group_array[x]["tangents_fmt"] == "None":
                                                    pass
                                                elif poly_group_array[x]["tangents_fmt"] == "4HalfFloats":
                                                    tanx = readhalffloat(trmbf)
                                                    tany = readhalffloat(trmbf)
                                                    tanz = readhalffloat(trmbf)
                                                    tanq = readhalffloat(trmbf)
                                                elif poly_group_array[x]["tangents_fmt"] == "3Floats":
                                                    tanx = readfloat(trmbf)
                                                    tany = readfloat(trmbf)
                                                    tanz = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown tangents type!")

                                                if poly_group_array[x]["bitangents_fmt"] == "None":
                                                    pass
                                                elif poly_group_array[x]["bitangents_fmt"] == "4HalfFloats":
                                                    bitanx = readhalffloat(trmbf)
                                                    bitany = readhalffloat(trmbf)
                                                    bitanz = readhalffloat(trmbf)
                                                    bitanq = readhalffloat(trmbf)
                                                elif poly_group_array[x]["bitangents_fmt"] == "3Floats":
                                                    bitanx = readfloat(trmbf)
                                                    bitany = readfloat(trmbf)
                                                    bitanz = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown bitangents type!")

                                                if poly_group_array[x]["tritangents_fmt"] == "None":
                                                    pass
                                                elif poly_group_array[x]["tritangents_fmt"] == "4HalfFloats":
                                                    tritanx = readhalffloat(trmbf)
                                                    tritany = readhalffloat(trmbf)
                                                    tritanz = readhalffloat(trmbf)
                                                    tritanq = readhalffloat(trmbf)
                                                elif poly_group_array[x]["tritangents_fmt"] == "3Floats":
                                                    tritanx = readfloat(trmbf)
                                                    tritany = readfloat(trmbf)
                                                    tritanz = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown bitangents type!")

                                                if poly_group_array[x]["uvs_fmt"] == "None":
                                                    tu = 0
                                                    tv = 0
                                                elif poly_group_array[x]["uvs_fmt"] == "2Floats":
                                                    tu = readfloat(trmbf)
                                                    tv = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown uvs type!")

                                                if poly_group_array[x]["uvs2_fmt"] == "None":
                                                    pass
                                                elif poly_group_array[x]["uvs2_fmt"] == "2Floats":
                                                    tu2 = readfloat(trmbf)
                                                    tv2 = readfloat(trmbf)
                                                    uv2_array.append((tu2, tv2))
                                                else:
                                                    raise AssertionError("Unknown uvs2 type!")

                                                if poly_group_array[x]["uvs3_fmt"] == "None":
                                                    pass
                                                elif poly_group_array[x]["uvs3_fmt"] == "2Floats":
                                                    tu3 = readfloat(trmbf)
                                                    tv3 = readfloat(trmbf)
                                                    uv3_array.append((tu3, tv3))
                                                else:
                                                    raise AssertionError("Unknown uvs3 type!")

                                                if poly_group_array[x]["uvs4_fmt"] == "None":
                                                    pass
                                                elif poly_group_array[x]["uvs4_fmt"] == "2Floats":
                                                    tu4 = readfloat(trmbf)
                                                    tv4 = readfloat(trmbf)
                                                    uv4_array.append((tu4, tv4))
                                                else:
                                                    raise AssertionError("Unknown uvs4 type!")

                                                if poly_group_array[x]["colors_fmt"] == "None":
                                                    colorr = 255
                                                    colorg = 255
                                                    colorb = 255
                                                    colora = 1
                                                elif poly_group_array[x]["colors_fmt"] == "4BytesAsFloat":
                                                    colorr = readbyte(trmbf)
                                                    colorg = readbyte(trmbf)
                                                    colorb = readbyte(trmbf)
                                                    colora = float(readbyte(trmbf)) / 255
                                                elif poly_group_array[x]["colors_fmt"] == "4Floats":
                                                    colorr = readfloat(trmbf) * 255
                                                    colorg = readfloat(trmbf) * 255
                                                    colorb = readfloat(trmbf) * 255
                                                    colora = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown colors type!")

                                                if poly_group_array[x]["colors2_fmt"] == "None":
                                                    colorr2 = 255
                                                    colorg2 = 255
                                                    colorb2 = 255
                                                    colora2 = 1
                                                elif poly_group_array[x]["colors2_fmt"] == "4BytesAsFloat":
                                                    colorr2 = readbyte(trmbf)
                                                    colorg2 = readbyte(trmbf)
                                                    colorb2 = readbyte(trmbf)
                                                    colora2 = readbyte(trmbf)
                                                elif poly_group_array[x]["colors2_fmt"] == "4Floats":
                                                    colorr2 = readfloat(trmbf) * 255
                                                    colorg2 = readfloat(trmbf) * 255
                                                    colorb2 = readfloat(trmbf) * 255
                                                    colora2 = readfloat(trmbf)
                                                else:
                                                    raise AssertionError("Unknown colors 2 type!")

                                                if poly_group_array[x]["bones_fmt"] == "None":
                                                    bone1 = 0
                                                    bone2 = 0
                                                    bone3 = 0
                                                    bone4 = 0
                                                elif poly_group_array[x]["bones_fmt"] == "4Bytes":
                                                    bone1 = readbyte(trmbf)
                                                    bone2 = readbyte(trmbf)
                                                    bone3 = readbyte(trmbf)
                                                    bone4 = readbyte(trmbf)
                                                else:
                                                    raise AssertionError("Unknown bones type!")

                                                if poly_group_array[x]["weights_fmt"] == "None":
                                                    weight1 = 0
                                                    weight2 = 0
                                                    weight3 = 0
                                                    weight4 = 0
                                                elif poly_group_array[x]["weights_fmt"] == "4ShortsAsFloat":
                                                    weight1 = readshort(trmbf) / 65535
                                                    weight2 = readshort(trmbf) / 65535
                                                    weight3 = readshort(trmbf) / 65535
                                                    weight4 = readshort(trmbf) / 65535
                                                else:
                                                    raise AssertionError("Unknown weights type!")

                                                vert_array.append((vx, vy, vz))
                                                normal_array.append((nx, ny, nz))
                                                color_array.append((colorr, colorg, colorb))
                                                alpha_array.append(colora)
                                                uv_array.append((tu, tv))
                                                if trskl is not None:
                                                    w1_array.append({"weight1": weight1, "weight2": weight2, "weight3": weight3, "weight4": weight4})
                                                    b1_array.append({"bone1": bone1, "bone2": bone2, "bone3": bone3, "bone4": bone4})

                                            print(f"Vertex buffer {x} end: {hex(ftell(trmbf))}")
                                        else:
                                            print(f"Vertex buffer {x} morph {y} start: {hex(ftell(trmbf))}")
                                            #MorphVert_array = #()
                                            #MorphNormal_array = #()
                                            for v in range(int(vert_buffer_byte_count / 0x1C)):
                                                #Morphs always seem to use this setup.
                                                vx = readlong(trmbf)
                                                vy = readlong(trmbf)
                                                vz = readlong(trmbf)
                                                nx = readhalffloat(trmbf)
                                                ny = readhalffloat(trmbf)
                                                nz = readhalffloat(trmbf)
                                                nq = readhalffloat(trmbf)
                                                tanx = readhalffloat(trmbf)
                                                tany = readhalffloat(trmbf)
                                                tanz = readhalffloat(trmbf)
                                                tanq = readhalffloat(trmbf)
                                                #append MorphVert_array [vx,vy,vz]
                                                #append MorphNormal_array [nx,ny,nz]
                                            print(f"Vertex buffer {x} morph {y} end: {hex(ftell(trmbf))}")
                                            #TODO: Continue implementing after line 3814
                                    fseek(trmbf,vert_buffer_sub_ret)

                            if vert_buffer_struct_ptr_faces != 0:
                                fseek(trmbf, vert_buffer_offset + vert_buffer_struct_ptr_faces)
                                face_buffer_start = ftell(trmbf) + readlong(trmbf); fseek(trmbf, face_buffer_start)
                                face_buffer_count = readlong(trmbf)

                                for y in range(face_buffer_count):
                                    face_buff_offset = ftell(trmbf) + readlong(trmbf)
                                    face_buff_ret = ftell(trmbf)
                                    fseek(trmbf, face_buff_offset)
                                    print(f"Facepoint {x} header: {hex(ftell(trmbf))}")
                                    face_buff_struct = ftell(trmbf) - readlong(trmbf); fseek(trmbf, face_buff_struct)
                                    face_buff_struct_len = readshort(trmbf)

                                    if face_buff_struct_len != 0x0006:
                                        raise AssertionError("Unexpected face buffer struct length!")
                                    face_buffer_struct_section_length = readshort(trmbf)
                                    face_buffer_struct_ptr = readshort(trmbf)

                                    if face_buffer_struct_ptr != 0:
                                        fseek(trmbf, face_buff_offset + face_buffer_struct_ptr)
                                        facepoint_start = ftell(trmbf) + readlong(trmbf); fseek(trmbf, facepoint_start)
                                        facepoint_byte_count = readlong(trmbf)
                                        print(f"Facepoint {x} start: {hex(ftell(trmbf))}")

                                        if len(vert_array) > 65536: # is this a typo? I would imagine it to be 65535
                                            for v in range(facepoint_byte_count // 12):
                                                fa = readlong(trmbf)
                                                fb = readlong(trmbf)
                                                fc = readlong(trmbf)
                                                face_array.append([fa, fb, fc])
                                        else:
                                            for v in range(facepoint_byte_count // 6):
                                                fa = readshort(trmbf)
                                                fb = readshort(trmbf)
                                                fc = readshort(trmbf)
                                                face_array.append([fa, fb, fc])
                                        print(f"Facepoint {x} end: {hex(ftell(trmbf))}")
                                    fseek(trmbf, face_buff_ret)
                            fseek(trmbf, vert_buffer_ret)

                            print("Making object...")

                            for b in range(len(w1_array)):
                                w = {"boneids": [], "weights": []}
                                maxweight = w1_array[b]["weight1"] +\
                                            w1_array[b]["weight2"] +\
                                            w1_array[b]["weight3"] +\
                                            w1_array[b]["weight4"]

                                if maxweight > 0:
                                    if (w1_array[b]["weight1"] > 0):
                                        w["boneids"].append(b1_array[b]["bone1"])
                                        w["weights"].append(w1_array[b]["weight1"])
                                    if (w1_array[b]["weight2"] > 0):
                                        w["boneids"].append(b1_array[b]["bone2"])
                                        w["weights"].append(w1_array[b]["weight2"])
                                    if (w1_array[b]["weight3"] > 0):
                                        w["boneids"].append(b1_array[b]["bone3"])
                                        w["weights"].append(w1_array[b]["weight3"])
                                    if (w1_array[b]["weight4"] > 0):
                                        w["boneids"].append(b1_array[b]["bone4"])
                                        w["weights"].append(w1_array[b]["weight4"])

                                weight_array.append(w)

                            if IN_BLENDER_ENV:
                                # LINE 3257

                                new_mesh = bpy.data.meshes.new(f"{poly_group_name}_mesh")
                                new_mesh.from_pydata(vert_array, [], face_array)
                                new_mesh.update()
                                new_object = bpy.data.objects.new(poly_group_name, new_mesh)

                                if bone_structure != None:
                                    new_object.parent = bone_structure
                                    new_object.modifiers.new(name='Skeleton', type='ARMATURE')
                                    new_object.modifiers['Skeleton'].object = bone_structure

                                    for face in new_object.data.polygons:
                                        for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                                            w = weight_array[vert_idx]

                                            for i in range(len(w["boneids"])):
                                                bone_id = bone_id_map[w['boneids'][i]]
                                                weight = w['weights'][i]

                                                group = None
                                                if new_object.vertex_groups.get(bone_id) == None:
                                                    group = new_object.vertex_groups.new(name=bone_id)
                                                else:
                                                    group = new_object.vertex_groups[bone_id]

                                                group.add([vert_idx], weight, 'REPLACE')

                                color_layer = new_object.data.vertex_colors.new(name="Color")
                                new_object.data.vertex_colors.active = color_layer
                                #print(f"color_array: {len(color_array)}")
                                #print(f"polygons: {len(new_object.data.polygons)}")
                                for i, poly in enumerate(new_object.data.polygons):
                                    #print(f"poly: {i}")
                                    for v, vert in enumerate(poly.vertices):
                                        loop_index = poly.loop_indices[v]
                                
                                        #print(f"loop_index: {loop_index}")
                                        #print((color_array[vert][0], color_array[vert][1], color_array[vert][2], 1))
                                
                                        color_layer.data[loop_index].color = (color_array[vert][0] / alpha_array[vert], color_array[vert][1] / alpha_array[vert], color_array[vert][2] / alpha_array[vert], alpha_array[vert])

                                for mat in materials:
                                    new_object.data.materials.append(mat)

                                # materials
                                for i, poly in enumerate(new_object.data.polygons):
                                    poly.material_index = face_mat_id_array[i]

                                # uvs
                                uv_layers = new_object.data.uv_layers
                                uv_layer = uv_layers.new(name="UVMap")
                                if len(uv2_array) > 0:
                                    uv2_layer = uv_layers.new(name="UV2Map")
                                if len(uv3_array) > 0:
                                    uv3_layer = uv_layers.new(name="UV3Map")
                                if len(uv4_array) > 0:
                                    uv4_layer = uv_layers.new(name="UV4Map")
                                uv_layers.active = uv_layer

                                for face in new_object.data.polygons:
                                    for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                                        uv_layer.data[loop_idx].uv = uv_array[vert_idx]
                                        if len(uv2_array) > 0:
                                            uv2_layer.data[loop_idx].uv = uv2_array[vert_idx]
                                        if len(uv3_array) > 0:
                                            uv3_layer.data[loop_idx].uv = uv3_array[vert_idx]
                                        if len(uv4_array) > 0:
                                            uv4_layer.data[loop_idx].uv = uv4_array[vert_idx]

                                #normals
                                new_object.data.use_auto_smooth = True
                                new_object.data.normals_split_custom_set_from_vertices(normal_array)
                                # add object to scene collection
                                new_collection.objects.link(new_object)

    



def readbyte(file):
    return int.from_bytes(file.read(1), byteorder='little')


def readshort(file):
    return int.from_bytes(file.read(2), byteorder='little')


# SIGNED!!!!
def readlong(file):
    bytes_data = file.read(4)
    # print(f"readlong: {bytes_data}")
    return int.from_bytes(bytes_data, byteorder='little', signed=True)


def readfloat(file):
    return struct.unpack('<f', file.read(4))[0]


def readhalffloat(file):
    return struct.unpack('<e', file.read(2))[0]


def readfixedstring(file, length):
    bytes_data = file.read(length)
    # print(f"readfixedstring ({length}): {bytes_data}")
    return bytes_data.decode('utf-8')


def fseek(file, offset):
    # print(f"Seeking to {offset}")
    file.seek(offset)


def ftell(file):
    return file.tell()


def fclose(file):
    file.close()

def menu_func_import(self, context):
    self.layout.operator(PokeArcImport.bl_idname, text="Legends Arceus (.trmdl)")
    self.layout.operator(PokeSVImport.bl_idname, text="Scarlet Violet (.trmdl)")
        
def register():
    bpy.utils.register_class(PokeArcImport)
    bpy.utils.register_class(PokeSVImport)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    
def unregister():
    bpy.utils.unregister_class(PokeArcImport)
    bpy.utils.unregister_class(PokeSVImport)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
