import sys
import os.path as path

import texture2ddecoder


"""
Config
"""
support_formats = ['dds', 'jpg', 'jpeg', 'png', 'tif', 'tiff']

#  DDS Data
dds_magic = 542327876
support_sizes = [4096, 2048, 1024, 512]

#  PIXEL FORMAT
BC1 = 0
BC3 = 1
RGBA8_UNORM = 2
RGBA8_SNORM = 3
BC6H = 4
BC7 = 5
RG8_UNORM = 6
RG8_SNORM = 7
DEPTH_32F_S8 = 8
DEPTH_32F = 9
R32_F = 10
RGBA16_F = 11
RG16_F = 12
RGBA16_U = 13
R8_UNORM = 14
R8_U = 15
RGB10_UNORM_A2_UNORM = 16
RGB10_SNORM_A2_UNORM = 17
R11G11B10_F = 18
R16_UNORM = 19
R32_U = 20
RGBA32_F = 21
PPS = 22
BGRA8_UNORM = 23

"""
App
"""


def convert_metro_texture(relative_path: str):
    if not relative_path:
        return None

    relative_path = relative_path.strip()

    for support_format in support_formats:
        format_path = f"{relative_path}.{support_format}"

        if path.isfile(format_path):
            return format_path

    for size in support_sizes:
        texture_data = None

        dds_path = f"{relative_path}.dds"
        texture_path = f"{relative_path}.{size}"
        crunch_texture_path = f"{texture_path}c"

        if path.isfile(crunch_texture_path):
            texture_path = crunch_texture_path

        if path.isfile(texture_path):
            with open(texture_path, "rb+") as texture:
                texture_data = texture.read()
                texture.close()

            if texture_path.endswith('c'):
                texture_data = texture2ddecoder.unpack_crunch(texture_data)

        if texture_data and len(texture_data) > 0:
            with open(dds_path, "wb+") as texture:
                #  dds params
                dds_size = 124
                dds_flag = 0x1 | 0x2 | 0x4 | 0x1000

                dds_unused = 0

                dds_pitch = 0
                dds_depth = 0
                dds_mip_count = 0
                dds_reversed = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

                dw_caps = 0x1000
                dw_caps_1 = 0
                dw_caps_2 = 0
                dw_caps_3 = 0

                if size == 512:
                    dds_flag = dds_flag | 0x20000
                    dw_caps = dw_caps | 0x400000
                    dds_mip_count = 10

                #  dds pixel format
                dpf_size = 32
                dpf_flags = 4
                dpf_four_cc = 827611204  # DXT1
                dpf_rgb_bit_count = 0
                dpf_r_mask = 0
                dpf_g_mask = 0
                dpf_b_mask = 0
                dpf_a_mask = 0

                if size == 512 and len(texture_data) != 174776:
                    dpf_four_cc = 894720068  # DXT5
                elif size == 1024 and len(texture_data) != 524288:
                    dpf_four_cc = 894720068
                elif size == 2048 and len(texture_data) != 2097152:
                    dpf_four_cc = 894720068
                elif size == 4096 and len(texture_data) != 8388608:
                    dpf_four_cc = 894720068

                #  make dds header
                texture.write(dds_magic.to_bytes(4, byteorder=sys.byteorder))
                texture.write(dds_size.to_bytes(4, byteorder=sys.byteorder))
                texture.write(dds_flag.to_bytes(4, byteorder=sys.byteorder))

                texture.write(size.to_bytes(4, byteorder=sys.byteorder))
                texture.write(size.to_bytes(4, byteorder=sys.byteorder))

                texture.write(dds_pitch.to_bytes(4, byteorder=sys.byteorder))
                texture.write(dds_depth.to_bytes(4, byteorder=sys.byteorder))
                texture.write(dds_mip_count.to_bytes(4, byteorder=sys.byteorder))

                for rever in dds_reversed:
                    texture.write(rever.to_bytes(4, byteorder=sys.byteorder))

                texture.write(dpf_size.to_bytes(4, byteorder=sys.byteorder))
                texture.write(dpf_flags.to_bytes(4, byteorder=sys.byteorder))
                texture.write(dpf_four_cc.to_bytes(4, byteorder=sys.byteorder))
                texture.write(dpf_rgb_bit_count.to_bytes(4, byteorder=sys.byteorder))
                texture.write(dpf_r_mask.to_bytes(4, byteorder=sys.byteorder))
                texture.write(dpf_g_mask.to_bytes(4, byteorder=sys.byteorder))
                texture.write(dpf_b_mask.to_bytes(4, byteorder=sys.byteorder))
                texture.write(dpf_a_mask.to_bytes(4, byteorder=sys.byteorder))

                texture.write(dw_caps.to_bytes(4, byteorder=sys.byteorder))
                texture.write(dw_caps_1.to_bytes(4, byteorder=sys.byteorder))
                texture.write(dw_caps_2.to_bytes(4, byteorder=sys.byteorder))
                texture.write(dw_caps_3.to_bytes(4, byteorder=sys.byteorder))

                texture.write(dds_unused.to_bytes(4, byteorder=sys.byteorder))

                #  write dds data
                texture.write(texture_data)
                texture.close()

                return dds_path

    return None


def try_convert_metro_texture(relative_path: str):
    try:
        return convert_metro_texture(relative_path)
    except:
        return None
