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
import struct


import bpy


# READ THIS: change to True when running in Blender, False when running using fake-bpy-module-latest
IN_BLENDER_ENV = False


def from_trmdl(filep, trmdl):
    # make collection
    if IN_BLENDER_ENV:
        new_collection = bpy.data.collections.new('new_collection')
        bpy.context.scene.collection.children.link(new_collection)

    trskl = None
    trmsh = None
    trmtr = None

    trmsh_lods_array = []
    bone_array = []
    bone_rig_array = []
    trskl_bone_adjust = 1
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

            if os.path.exists(filep + trskl_name):
                trskl = open(filep + trskl_name, "rb")
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
            trmtr_name_len = readlong(trmdl) - 6
            trmtr_name = readfixedstring(trmdl, trmtr_name_len)
            # TODO ArceusShiny
            # LINE 1227
            print(trmtr_name)
            if x == 0:
                if os.path.exists(filep + trmtr_name):
                    trmtr = open(filep + trmtr_name, "rb")
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


    # TODO parse TRMTR file
    # LINE 1867

    # TODO parse TRMSH file
    # LINE 2593

    for w in range(trmsh_count):
        if os.path.exists(filep + trmsh_lods_array[w]):
            poly_group_array = []
            trmsh = open(filep + trmsh_lods_array[w], "rb")
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
                if os.path.exists(filep + trmbf_filename):
                    trmbf = open(filep + trmbf_filename, "rb")
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
                            poly_group_name = ""; vis_group_name = ""; vert_buffer_stride = 0; mat_id = 1
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
                                # TODO mat_list
                                # LINE 2693
                                pass

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
                                        print(poly_group_array[x])

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
                                                pass
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
                                            else:
                                                raise AssertionError("Unknown uvs2 type!")

                                            if poly_group_array[x]["uvs3_fmt"] == "None":
                                                pass
                                            elif poly_group_array[x]["uvs3_fmt"] == "2Floats":
                                                tu3 = readfloat(trmbf)
                                                tv3 = readfloat(trmbf)
                                            else:
                                                raise AssertionError("Unknown uvs3 type!")

                                            if poly_group_array[x]["uvs4_fmt"] == "None":
                                                pass
                                            elif poly_group_array[x]["uvs4_fmt"] == "2Floats":
                                                tu4 = readfloat(trmbf)
                                                tv4 = readfloat(trmbf)
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

                                            # vert_array.append((vx, vz, vy))  # ! Y and Z are swapped
                                            vert_array.append([vx, vz, vy])  # ! Y and Z are swapped
                                            # norm_array.append((nx, ny, nz))
                                            # # TODO vert_colors
                                            # # LINE 3157
                                            # uv_array.append((tu, tv, 0))
                                            # w1_array.append({weight1: weight1, weight2: weight2, weight3: weight3, weight4: weight4})
                                            # b1_array.append({bone1: bone1, bone2: bone2, bone3: bone3, bone4: bone4})

                                            print(f"Vertex buffer {x} end: {hex(ftell(trmbf))}")

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

                            if IN_BLENDER_ENV:
                                new_mesh = bpy.data.meshes.new('new_mesh')
                                new_mesh.from_pydata(vert_array, [], face_array)
                                new_mesh.update()
                                # make object from mesh
                                new_object = bpy.data.objects.new('new_object', new_mesh)
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


def readfixedstring (file, length):
    return file.read(length).decode('utf-8')


def fseek(file, offset):
    # print(f"Seeking to {offset}")
    file.seek(offset)


def ftell(file):
    return file.tell()


def fclose(file):
    file.close()


def main():
    # READ THIS: change this directory and filename to the directory of the model's files and the .trmdl file's name
    directory = "/home/kitten/プロジェクト/ProjectArceus/trmdl_0570_00_41/"
    filename = "pm0570_00_41.trmdl"
    f = open(f"{directory}{filename}", "rb")
    from_trmdl(directory, f)
    f.close()


main()
