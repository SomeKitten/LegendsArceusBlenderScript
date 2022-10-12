# HUGE thanks to Random Talking Bush for making the original maxscript for this
# https://www.vg-resource.com/thread-29836.html

# The formatting of this script is a bit wonky, but that's because I wanted to make it
# look as close to the original maxscript as possible.
# That way, it's easier to compare the two and see what's different.

# ***I have marked places where you need to change variables with "READ THIS:"***

# READ THIS: paste this into blender and run, make sure you change the path to this file's name
# filename = "/home/kitten/PycharmProjects/Arceus/PokemonSwitch.py"
# exec(compile(open(filename).read(), filename, 'exec'))


import os.path
import random
import struct


import bpy


# READ THIS: change to True when running in Blender, False when running using fake-bpy-module-latest
IN_BLENDER_ENV = True


def from_trmdl(filep, trmdl):
    # make collection
    if IN_BLENDER_ENV:
        new_collection = bpy.data.collections.new(os.path.basename(trmdl.name))
        bpy.context.scene.collection.children.link(new_collection)

    materials = []

    trskl = None
    trmsh = None
    trmtr = None

    trmsh_lods_array = []
    bone_array = []
    bone_rig_array = []
    trskl_bone_adjust = 0
    CharaCheck = "None"

    print("Parsing TRMDL...")

    trmdl_file_start = readlong(trmdl); fseek(trmdl, trmdl_file_start)
    trmdl_struct = ftell(trmdl) - readlong(trmdl); fseek(trmdl, trmdl_struct)
    trmdl_struct_len = readshort(trmdl)

    if trmdl_struct_len != 0x0012:
        raise AssertionError("Unexpected TRMDL header struct length!")

    trmdl_struct_section_len = readshort(trmdl)
    trmdl_struct_start = readshort(trmdl)
    trmdl_struct_trmsh = readshort(trmdl)
    trmdl_struct_trskl = readshort(trmdl)
    trmdl_struct_trmtr = readshort(trmdl)
    trmdl_struct_custom = readshort(trmdl)
    trmdl_struct_bound_box = readshort(trmdl)
    trmdl_struct_float = readshort(trmdl)

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

                if chara_check == "au_": chara_check = "CommonNPC"
                elif chara_check == "bu_": chara_check = "CommonNPC"
                elif chara_check == "cf_": chara_check = "CommonNPC"
                elif chara_check == "cm_": chara_check = "CommonNPC"
                elif chara_check == "df_": chara_check = "CommonNPC"
                elif chara_check == "dm_": chara_check = "CommonNPC"
                elif chara_check == "p1_": chara_check = "Rei"
                elif chara_check == "p2_": chara_check = "Akari"
                else: chara_check = "None"

                trmsh_name = readfixedstring(trmdl, trmsh_name_len)
                print(trmsh_name)
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
                if os.path.exists(os.path.join(filep, trmtr_name)):
                    trmtr = open(os.path.join(filep, trmtr_name), "rb")
                else:
                    print(f"Can't find {trmtr_name}!")
            fseek(trmdl, trmtr_ret)
    fclose(trmdl)

    # TODO create bone_rig_array
    # LINE 1247

    # if trskl is not None:
    #     print("Parsing TRSKL...")
    #     trskl_file_start = readlong(trskl)
    #     fseek(trskl, trskl_file_start)
    #     trskl_struct = ftell(trskl) - readlong(trskl); fseek(trskl, trskl_struct)
    #     trskl_struct_len = readshort(trskl)
    #     if trskl_struct_len == 0x000C:
    #         trskl_struct_section_len = readshort(trskl)
    #         trskl_struct_start = readshort(trskl)
    #         trskl_struct_bone = readshort(trskl)
    #         trskl_struct_b = readshort(trskl)
    #         trskl_struct_c = readshort(trskl)
    #         trskl_struct_bone_adjust = 0
    #     elif trskl_struct_len == 0x000E:
    #         trskl_struct_section_len = readshort(trskl)
    #         trskl_struct_start = readshort(trskl)
    #         trskl_struct_bone = readshort(trskl)
    #         trskl_struct_b = readshort(trskl)
    #         trskl_struct_c = readshort(trskl)
    #         trskl_struct_bone_adjust = readshort(trskl)
    #     else:
    #         raise AssertionError("Unexpected TRSKL header struct length!")
    #
    #     if trskl_struct_bone_adjust != 0:
    #         fseek(trskl, trskl_file_start + trskl_struct_bone_adjust)
    #         trskl_bone_adjust = readlong(trskl) + 1; print(f"Mesh node IDs start at {trskl_bone_adjust}")
    #
    #     if trskl_struct_bone != 0:
    #         fseek(trskl, trskl_file_start + trskl_struct_bone)
    #         trskl_bone_start = ftell(trskl) + readlong(trskl); fseek(trskl, trskl_bone_start)
    #         bone_count = readlong(trskl)
    #
    #         for i in range(bone_count):
    #             x = i + 1
    #             bone_offset = ftell(trskl) + readlong(trskl)
    #             bone_ret = ftell(trskl)
    #             fseek(trskl, bone_offset)
    #             print(f"Bone {x} start: {hex(bone_offset)}")
    #             trskl_bone_struct = ftell(trskl) - readlong(trskl); fseek(trskl, trskl_bone_struct)
    #             trskl_bone_struct_len = readshort(trskl)
    #
    #             if trskl_bone_struct_len == 0x0012:
    #                 trskl_bone_struct_ptr_section_len = readshort(trskl)
    #                 trskl_bone_struct_ptr_string = readshort(trskl)
    #                 trskl_bone_struct_ptr_bone = readshort(trskl)
    #                 trskl_bone_struct_ptr_c = readshort(trskl)
    #                 trskl_bone_struct_ptr_d = readshort(trskl)
    #                 trskl_bone_struct_ptr_parent = readshort(trskl)
    #                 trskl_bone_struct_ptr_rig_id = readshort(trskl)
    #                 trskl_bone_struct_ptr_bone_merge = readshort(trskl)
    #                 trskl_bone_struct_ptr_h = 0
    #             elif trskl_bone_struct_len == 0x0014:
    #                 trskl_bone_struct_ptr_section_len = readshort(trskl)
    #                 trskl_bone_struct_ptr_string = readshort(trskl)
    #                 trskl_bone_struct_ptr_bone = readshort(trskl)
    #                 trskl_bone_struct_ptr_c = readshort(trskl)
    #                 trskl_bone_struct_ptr_d = readshort(trskl)
    #                 trskl_bone_struct_ptr_parent = readshort(trskl)
    #                 trskl_bone_struct_ptr_rig_id = readshort(trskl)
    #                 trskl_bone_struct_ptr_bone_merge = readshort(trskl)
    #                 trskl_bone_struct_ptr_h = readshort(trskl)
    #             else:
    #                 raise AssertionError("Unexpected TRSKL bone struct length!")
    #
    #             if trskl_bone_struct_ptr_bone_merge != 0:
    #                 fseek(trskl, bone_offset + trskl_bone_struct_ptr_bone_merge)
    #                 bone_merge_start = ftell(trskl) + readlong(trskl); fseek(trskl, bone_merge_start)
    #                 bone_merge_string_len = readlong(trskl)
    #                 if bone_merge_string_len != 0:
    #                     bone_merge_string = readfixedstring(trskl, bone_merge_string_len)
    #                     print(f"BoneMerge to {bone_merge_string}")
    #                 else: bone_merge_string = ""
    #
    #             if trskl_bone_struct_ptr_bone != 0:
    #                 fseek(trskl, bone_offset + trskl_bone_struct_ptr_bone)
    #                 bone_pos_start = ftell(trskl) + readlong(trskl); fseek(trskl, bone_pos_start)
    #                 bone_pos_struct = ftell(trskl) - readlong(trskl); fseek(trskl, bone_pos_struct)
    #                 bone_pos_struct_len = readshort(trskl)
    #
    #                 if bone_pos_struct_len != 0x000A:
    #                     raise AssertionError("Unexpected bone position struct length!")
    #
    #                 bone_pos_struct_section_len = readshort(trskl)
    #                 bone_pos_struct_ptr_scl = readshort(trskl)
    #                 bone_pos_struct_ptr_rot = readshort(trskl)
    #                 bone_pos_struct_ptr_trs = readshort(trskl)
    #
    #                 fseek(trskl, bone_pos_start + bone_pos_struct_ptr_trs)
    #                 bone_tx = readfloat(trskl); bone_ty = readfloat(trskl); bone_tz = readfloat(trskl)
    #                 # TODO ArceusScale
    #                 # LINE 1797
    #                 fseek(trskl, bone_pos_start + bone_pos_struct_ptr_rot)
    #                 bone_rx = readfloat(trskl); bone_ry = readfloat(trskl); bone_rz = readfloat(trskl); bone_rw = readfloat(trskl)
    #                 fseek(trskl, bone_pos_start + bone_pos_struct_ptr_scl)
    #                 bone_sx = readfloat(trskl); bone_sy = readfloat(trskl); bone_sz = readfloat(trskl)
    #
    #                 if trskl_bone_struct_ptr_string != 0:
    #                     fseek(trskl, bone_offset + trskl_bone_struct_ptr_string)
    #                     bone_string_start = ftell(trskl) + readlong(trskl); fseek(trskl, bone_string_start)
    #                     bone_str_len = readlong(trskl); bone_name = readfixedstring(trskl, bone_str_len)
    #                 if trskl_bone_struct_ptr_parent != 0x00:
    #                     fseek(trskl, bone_offset + trskl_bone_struct_ptr_parent)
    #                     bone_parent = readlong(trskl) + 1
    #                 else:
    #                     bone_parent = 0
    #                 if trskl_bone_struct_ptr_rig_id != 0:
    #                     fseek(trskl, bone_offset + trskl_bone_struct_ptr_rig_id)
    #                     bone_rig_id = readlong(trskl) + trskl_bone_adjust
    #                     bone_rig_array[bone_rig_id] = bone_name
    #
    #                 # TODO matrix math!!
    #                 # LINE 1820

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
                mat_shader = "Standard"; mat_col0 = ""; mat_lym0 = ""; mat_nrm0 = ""; mat_emi0 = ""; mat_rgh0 = ""; mat_mtl0 = ""
                mat_uv_scale_u = 1.0; mat_uv_scale_v = 1.0; mat_uv_trs_u = 0; mat_uv_trs_v = 0
                mat_uv_scale2_u = 1.0; mat_uv_scale2_v = 1.0; mat_uv_trs2_u = 0; mat_uv_trs2_v = 0
                mat_color1_r = 1.0; mat_color1_g = 1.0; mat_color1_b = 1.0
                mat_color2_r = 1.0; mat_color2_g = 1.0; mat_color2_b = 1.0
                mat_color3_r = 1.0; mat_color3_g = 1.0; mat_color3_b = 1.0
                mat_color4_r = 1.0; mat_color4_g = 1.0; mat_color4_b = 1.0
                mat_rgh_layer0 = 1.0; mat_rgh_layer1 = 1.0; mat_rgh_layer2 = 1.0; mat_rgh_layer3 = 1.0; mat_rgh_layer4 = 1.0
                mat_mtl_layer0 = 0.0; mat_mtl_layer1 = 0.0; mat_mtl_layer2 = 0.0; mat_mtl_layer3 = 0.0; mat_mtl_layer4 = 0.0
                mat_offset = ftell(trmtr) + readlong(trmtr)
                mat_ret = ftell(trmtr)
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
                            if z == 1: mat_shader = mat_param_b_shader_string
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
                                    print(f"{mat_param_b_sub_string}: {mat_param_b_sub_value}")
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
                        elif mat_param_c_string == "EmissionColorMap": mat_emi0 = mat_param_c_value
                        elif mat_param_c_string == "RoughnessMap": mat_rgh0 = mat_param_c_value
                        elif mat_param_c_string == "MetalicMap": mat_mtl0 = mat_param_c_value

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

                        print(f"{mat_param_c_string}: {mat_param_c_value} [{mat_param_c_id}]")
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
                        elif mat_param_e_string == "Metallic": mat_met_layer0 = mat_param_e_value
                        elif mat_param_e_string == "MetallicLayer1": mat_met_layer1 = mat_param_e_value
                        elif mat_param_e_string == "MetallicLayer2": mat_met_layer2 = mat_param_e_value
                        elif mat_param_e_string == "MetallicLayer3": mat_met_layer3 = mat_param_e_value
                        elif mat_param_e_string == "MetallicLayer4": mat_met_layer4 = mat_param_e_value

                        print(f"{mat_param_e_string}: {mat_param_e_value}")
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

                        print(f"{mat_param_f_string}: {mat_param_f_value1}, {mat_param_f_value2}")
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

                        print(f"{mat_param_g_string}: {mat_param_g_value1}, {mat_param_g_value2}, {mat_param_g_value3}")
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
                        else: print(f"Unknown mat_param_h: {mat_param_h_string}")

                        print(f"{mat_param_h_string}: {mat_param_h_value1}, {mat_param_h_value2}, {mat_param_h_value3}, {mat_param_h_value4}")
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

                        print(f"{mat_param_j_string}: {mat_param_j_value}")
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

                mat_data_array.append({"mat_name": mat_name, "mat_shader": mat_shader, "mat_col0": mat_col0, "mat_lym0": mat_lym0, "mat_nrm0": mat_nrm0, "mat_emi0": mat_emi0, "mat_rgh0": mat_rgh0, "mat_mtl0": mat_mtl0, "mat_color1_r": mat_color1_r, "mat_color1_g": mat_color1_g, "mat_color1_b": mat_color1_b, "mat_color2_r": mat_color2_r, "mat_color2_g": mat_color2_g, "mat_color2_b": mat_color2_b, "mat_color3_r": mat_color3_r, "mat_color3_g": mat_color3_g, "mat_color3_b": mat_color3_b, "mat_color4_r": mat_color4_r, "mat_color4_g": mat_color4_g, "mat_color4_b": mat_color4_b, "mat_rgh_layer0": mat_rgh_layer0, "mat_rgh_layer1": mat_rgh_layer1, "mat_rgh_layer2": mat_rgh_layer2, "mat_rgh_layer3": mat_rgh_layer3, "mat_rgh_layer4": mat_rgh_layer4, "mat_mtl_layer0": mat_mtl_layer0, "mat_mtl_layer1": mat_mtl_layer1, "mat_mtl_layer2": mat_mtl_layer2, "mat_mtl_layer3": mat_mtl_layer3, "mat_mtl_layer4": mat_mtl_layer4, "mat_uv_scale_u": mat_uv_scale_u, "mat_uv_scale_v": mat_uv_scale_v, "mat_uv_scale2_u": mat_uv_scale2_u, "mat_uv_scale2_v": mat_uv_scale2_v})
                fseek(trmtr, mat_ret)
            print("--------------------")

        fclose(trmtr)

        if IN_BLENDER_ENV:
            # process materials
            for m, mat in enumerate(mat_data_array):
                material = bpy.data.materials.new(name=mat["mat_name"])
                material.use_nodes = True
                materials.append(material)

                blend_type = "ADD"

                material_output = material.node_tree.nodes.get("Material Output")
                principled_bsdf = material.node_tree.nodes.get("Principled BSDF")

                image_texture = material.node_tree.nodes.new("ShaderNodeTexImage")
                image_texture.image = bpy.data.images.load(os.path.join(filep, mat["mat_lym0"][:-5] + ".png"))
                image_texture.image.colorspace_settings.name = "Non-Color"

                color1 = (mat["mat_color1_r"], mat["mat_color1_g"], mat["mat_color1_b"], 1.0)
                color2 = (mat["mat_color2_r"], mat["mat_color2_g"], mat["mat_color2_b"], 1.0)
                color3 = (mat["mat_color3_r"], mat["mat_color3_g"], mat["mat_color3_b"], 1.0)
                color4 = (mat["mat_color4_r"], mat["mat_color4_g"], mat["mat_color4_b"], 1.0)

                print(f'Material {mat["mat_name"]}:')
                print(f"Color 1: {color1}")
                print(f"Color 2: {color2}")
                print(f"Color 3: {color3}")
                print(f"Color 4: {color4}")
                print("---")

                uv_map = material.node_tree.nodes.new("ShaderNodeUVMap")
                separate_xyz = material.node_tree.nodes.new("ShaderNodeSeparateXYZ")

                math_multiply = material.node_tree.nodes.new("ShaderNodeMath")
                math_multiply.operation = "MULTIPLY"
                math_multiply.inputs[1].default_value = mat["mat_uv_scale_u"]

                math_multiply2 = material.node_tree.nodes.new("ShaderNodeMath")
                math_multiply2.operation = "MULTIPLY"
                math_multiply2.inputs[1].default_value = mat["mat_uv_scale_v"]

                math_ping_pong = material.node_tree.nodes.new("ShaderNodeMath")
                math_ping_pong.operation = "PINGPONG"
                math_ping_pong.inputs[1].default_value = 1.0

                combine_xyz = material.node_tree.nodes.new("ShaderNodeCombineXYZ")

                color_inp1 = material.node_tree.nodes.new("ShaderNodeRGB")
                color_inp1.outputs[0].default_value = color1
                color_inp2 = material.node_tree.nodes.new("ShaderNodeRGB")
                color_inp2.outputs[0].default_value = color2
                color_inp3 = material.node_tree.nodes.new("ShaderNodeRGB")
                color_inp3.outputs[0].default_value = color3
                color_inp4 = material.node_tree.nodes.new("ShaderNodeRGB")
                color_inp4.outputs[0].default_value = color4

                mix_color1 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_color1.blend_type = blend_type
                mix_color1.inputs[1].default_value = (0, 0, 0, 0)
                mix_color2 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_color2.blend_type = blend_type
                mix_color2.inputs[1].default_value = (0, 0, 0, 0)
                mix_color3 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_color3.blend_type = blend_type
                mix_color3.inputs[1].default_value = (0, 0, 0, 0)
                mix_color4 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_color4.blend_type = blend_type
                mix_color4.inputs[1].default_value = (0, 0, 0, 0)

                separate_color = material.node_tree.nodes.new("ShaderNodeSeparateRGB")

                material.node_tree.links.new(uv_map.outputs[0], separate_xyz.inputs[0])
                material.node_tree.links.new(separate_xyz.outputs[0], math_multiply.inputs[0])
                material.node_tree.links.new(math_multiply.outputs[0], math_ping_pong.inputs[0])
                material.node_tree.links.new(math_ping_pong.outputs[0], combine_xyz.inputs[0])

                material.node_tree.links.new(separate_xyz.outputs[1], math_multiply2.inputs[0])
                material.node_tree.links.new(math_multiply2.outputs[0], combine_xyz.inputs[1])

                material.node_tree.links.new(combine_xyz.outputs[0], image_texture.inputs[0])

                material.node_tree.links.new(image_texture.outputs[0], separate_color.inputs[0])

                material.node_tree.links.new(separate_color.outputs[0], mix_color1.inputs[0])
                material.node_tree.links.new(separate_color.outputs[1], mix_color2.inputs[0])
                material.node_tree.links.new(separate_color.outputs[2], mix_color3.inputs[0])
                material.node_tree.links.new(image_texture.outputs[1],  mix_color4.inputs[0])

                material.node_tree.links.new(color_inp1.outputs[0], mix_color1.inputs[2])
                material.node_tree.links.new(color_inp2.outputs[0], mix_color2.inputs[2])
                material.node_tree.links.new(color_inp3.outputs[0], mix_color3.inputs[2])
                material.node_tree.links.new(color_inp4.outputs[0], mix_color4.inputs[2])

                mix_color_final1 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_color_final1.blend_type = blend_type
                mix_color_final2 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_color_final2.blend_type = blend_type
                mix_color_final3 = material.node_tree.nodes.new("ShaderNodeMixRGB")
                mix_color_final3.blend_type = blend_type

                material.node_tree.links.new(mix_color1.outputs[0], mix_color_final1.inputs[1])
                material.node_tree.links.new(mix_color2.outputs[0], mix_color_final1.inputs[2])
                material.node_tree.links.new(mix_color3.outputs[0], mix_color_final2.inputs[1])
                material.node_tree.links.new(mix_color4.outputs[0], mix_color_final2.inputs[2])

                material.node_tree.links.new(mix_color_final1.outputs[0], mix_color_final3.inputs[1])
                material.node_tree.links.new(mix_color_final2.outputs[0], mix_color_final3.inputs[2])

                material.node_tree.links.new(mix_color_final3.outputs[0], principled_bsdf.inputs[0])

                material.node_tree.links.new(principled_bsdf.outputs[0], material_output.inputs[0])

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
                            positions_fmt = "None"; normals_fmt = "None"; tangents_fmt = "None"; bitangents_fmt = "None"
                            uvs_fmt = "None"; uvs2_fmt = "None"; uvs3_fmt = "None"; uvs4_fmt = "None"
                            colors_fmt = "None"; colors2_fmt = "None"; bones_fmt = "None"; weights_fmt = "None"

                            poly_group_offset = ftell(trmsh) + readlong(trmsh)
                            poly_group_ret = ftell(trmsh)
                            fseek(trmsh, poly_group_offset)
                            print(f"PolyGroup offset #{x}: {hex(poly_group_offset)}")
                            poly_group_struct = ftell(trmsh) - readlong(trmsh)
                            fseek(trmsh, poly_group_struct)
                            poly_group_struct_len = readshort(trmsh)

                            if poly_group_struct_len != 0x001E:
                                raise AssertionError("Unexpected PolyGroup struct length!")
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
                                    for k in range(vert_buff_param_count):
                                        y = k + 1
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
                                    "uvs_fmt": uvs_fmt,
                                    "uvs2_fmt": uvs2_fmt,
                                    "uvs3_fmt": uvs3_fmt,
                                    "uvs4_fmt": uvs4_fmt,
                                    "colors_fmt": colors_fmt,
                                    "colors2_fmt": colors2_fmt,
                                    "bones_fmt": bones_fmt,
                                    "weights_fmt": weights_fmt
                                }
                            )
                            fseek(trmsh, poly_group_ret)

                            vert_buffer_offset = ftell(trmbf) + readlong(trmbf)
                            vert_buffer_ret = ftell(trmbf)
                            fseek(trmbf, vert_buffer_offset)
                            vert_buffer_struct = ftell(trmbf) - readlong(trmbf); fseek(trmbf, vert_buffer_struct)
                            vert_buffer_struct_len = readshort(trmbf)

                            if vert_buffer_struct_len != 0x0008:
                                raise AssertionError("Unexpected vertex buffer struct length!")
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
                                    print(f"Vertex buffer {x} header: {hex(ftell(trmbf))}")
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
                                                pass
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
                                                pass
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
                                                pass
                                            elif poly_group_array[x]["bones_fmt"] == "4Bytes":
                                                bone1 = readbyte(trmbf)
                                                bone2 = readbyte(trmbf)
                                                bone3 = readbyte(trmbf)
                                                bone4 = readbyte(trmbf)
                                            else:
                                                raise AssertionError("Unknown bones type!")

                                            if poly_group_array[x]["weights_fmt"] == "None":
                                                pass
                                            elif poly_group_array[x]["weights_fmt"] == "4ShortsAsFloat":
                                                weight1 = readshort(trmbf) / 65535
                                                weight2 = readshort(trmbf) / 65535
                                                weight3 = readshort(trmbf) / 65535
                                                weight4 = readshort(trmbf) / 65535
                                            else:
                                                raise AssertionError("Unknown weights type!")

                                            vert_array.append((-vx, vz, vy))  # ! Y and Z are swapped, and X is negated
                                            normal_array.append((-nx, nz, ny))  # ! Y and Z are swapped, and X is negated
                                            # color_array.append((colorr, colorg, colorb))
                                            # alpha_array.append(colora)
                                            uv_array.append((tu, tv))
                                            # w1_array.append({"weight1": weight1, "weight2": weight2, "weight3": weight3, "weight4": weight4})
                                            # b1_array.append({"bone1": bone1, "bone2": bone2, "bone3": bone3, "bone4": bone4})

                                            # print(f"Vertex buffer {x} end: {hex(ftell(trmbf))}")

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

                            if IN_BLENDER_ENV:
                                # LINE 3257
                                new_mesh = bpy.data.meshes.new(f"{poly_group_name}_mesh")
                                # print(f"face: {face_array[1]}")
                                new_mesh.from_pydata(vert_array, [], face_array)
                                new_mesh.update()
                                # make object from mesh
                                new_object = bpy.data.objects.new(poly_group_name, new_mesh)

                                # # vertex colours
                                # color_layer = new_object.data.vertex_colors.new()
                                # new_object.data.vertex_colors.active = color_layer
                                #
                                # print(f"color_array: {len(color_array)}")
                                # print(f"polygons: {len(new_object.data.polygons)}")
                                #
                                # for i, poly in enumerate(new_object.data.polygons):
                                #     print(f"poly: {i}")
                                #     for v, vert in enumerate(poly.vertices):
                                #         loop_index = poly.loop_indices[v]
                                #
                                #         # print(f"loop_index: {loop_index}")
                                #         # print(f"vert: {vert}")
                                #
                                #         color_layer.data[loop_index].color = (color_array[vert][0] / 255, color_array[vert][1] / 255, color_array[vert][2] / 255, 1)

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


def main():
    # READ THIS: change this directory and filename to the directory of the model's files and the .trmdl file's name
    directory = "/home/kitten/VirtualBox Shared/Arceus/romfs/bin/archive/pokemon/pm0134_00_00_mdl"
    filename = "pm0134_00_00.trmdl"
    f = open(os.path.join(directory, filename), "rb")
    from_trmdl(directory, f)
    f.close()


main()
