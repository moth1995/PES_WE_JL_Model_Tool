from file_structure import FacePCModel, FacePS2Model, Container, unzlib_it, file_read
from pathlib import Path

from file_structure.image import PESImage, PNGImage
from file_structure.models import FacePSPModel

def create_obj(pes_model:FacePCModel, folder:str, filename:str, export_normals:bool):
    with open (f"{folder}/{filename}.obj","w") as obj_file:
        obj_file.writelines("# PES/WE/JL Model Tool\n")
        obj_file.writelines(f"# OBJ Model {filename}\n")
        obj_file.writelines("\n")
        obj_file.writelines(f"mtllib {filename}.mtl\n")
        obj_file.writelines("\n")
        obj_file.writelines(f"o {filename} \n")
        obj_file.writelines("\n")
        obj_file.writelines(f"# Vertices {len(pes_model.vertex_list)}\n")
        for i in range(len(pes_model.vertex_list)):
            obj_file.writelines(f"v  {pes_model.vertex_list[i].x} {pes_model.vertex_list[i].y} {pes_model.vertex_list[i].z}\n")

        obj_file.writelines("\n")
        obj_file.writelines(f"# UVs {len(pes_model.vertex_texture_list)}\n")
        for x in range(len(pes_model.vertex_texture_list)):
            obj_file.write(f"vt  {pes_model.vertex_texture_list[x].u} {pes_model.vertex_texture_list[x].v}\n")

        if export_normals:
            obj_file.writelines("\n")
            obj_file.writelines(f"# Normals {len(pes_model.vertex_normal_list)}\n")
            for i in range(len(pes_model.vertex_normal_list)):
                obj_file.writelines(f"vn  {pes_model.vertex_normal_list[i].x} {pes_model.vertex_normal_list[i].y} {pes_model.vertex_normal_list[i].z}\n")

        obj_file.writelines("\n")
        obj_file.writelines("usemtl material1\n")
        obj_file.writelines("\n")
        obj_file.writelines(f"# Faces {len(pes_model.polygonal_faces_list)}\n")
        if export_normals:
            for i in range(len(pes_model.polygonal_faces_list)):
                obj_file.write(f"f  "
                + f"{pes_model.polygonal_faces_list[i].i1}/{pes_model.polygonal_faces_list[i].i1}/{pes_model.polygonal_faces_list[i].i1} "
                + f"{pes_model.polygonal_faces_list[i].i2}/{pes_model.polygonal_faces_list[i].i2}/{pes_model.polygonal_faces_list[i].i2} "
                + f"{pes_model.polygonal_faces_list[i].i3}/{pes_model.polygonal_faces_list[i].i3}/{pes_model.polygonal_faces_list[i].i3}\n"
                )
        else:
            for i in range(len(pes_model.polygonal_faces_list)):
                obj_file.write(f"f  "
                + f"{pes_model.polygonal_faces_list[i].i1}/{pes_model.polygonal_faces_list[i].i1}"
                + f"{pes_model.polygonal_faces_list[i].i2}/{pes_model.polygonal_faces_list[i].i2}"
                + f"{pes_model.polygonal_faces_list[i].i3}/{pes_model.polygonal_faces_list[i].i3}\n"
                )
            
def create_mtl(folder:str, filename:str):
    with open(f'{folder}/{filename}.mtl',"w") as mtl_file:
        mtl_file.writelines("newmtl material1 \n")
        mtl_file.writelines(f"\tmap_Kd {filename}.png \n")

def get_container(unzlibed_file:bytearray):
    return Container(unzlibed_file)

def get_face_hair_model(file_location:str, platform:int):
    bin_file = file_read(file_location)
    decompress_bin_file = unzlib_it(bin_file[32:])
    file_ctn = get_container(decompress_bin_file)
    if platform == 0:
        model = FacePCModel(file_ctn.files[0])
    elif platform == 1:
        model = FacePS2Model(file_ctn.files[0])
    else:
        model = FacePSPModel(file_ctn.files[0])
    return model

def is_hair(list_of_files:list):
    if len(list_of_files) == 3:
        return PESImage.PES_IMAGE_SIGNATURE == list_of_files[1][:4]
    else:
        return False

def get_pes_texture(file_location:str):
    bin_file = file_read(file_location)
    decompress_bin_file = unzlib_it(bin_file[32:])
    return get_container(decompress_bin_file).files[1] if is_hair(get_container(decompress_bin_file).files) else get_container(decompress_bin_file).files[-1]

def bin_to_obj(file:str, platform:int, export_normals):
    # from a string we get a Path object and then we get the values that we need
    bin_location = Path(file)
    bin_full_path = str(bin_location.resolve())
    bin_filename = bin_location.stem
    bin_folder_location = str(bin_location.parent)
    """
    if not Path(f"{bin_folder_location}/{bin_filename}.png").is_file():
        pes_image = PESImage()
        pes_image.from_bytes(get_pes_texture(bin_full_path))
        pes_image.bgr_to_bgri()
        png_image = PNGImage()
        #png_image.pes_img = pes_image
        png_image.png_from_pes_img(pes_image)
        with open(f"{bin_folder_location}/{bin_filename}.png", "wb") as png_file:
            png_file.write(png_image.png)
    #"""
    model = get_face_hair_model(bin_full_path, platform)

    # actions to create a obj and mtl file
    create_obj(model, bin_folder_location, bin_filename, export_normals)
    create_mtl(bin_folder_location, bin_filename)

if __name__ == "__main__":
    #bin_to_obj("./test/Beckham-models/pc/face-unnamed_2009.bin", 0, True)
    #bin_to_obj("./test/Beckham-models/pc/hair-unnamed_5041.bin", 0, True)
    #bin_to_obj("./test/Beckham-models/ps2/face-unnamed_2009.bin", 1, True)
    #bin_to_obj("./test/Beckham-models/ps2/hair-unnamed_5041.bin", 1, True)
    bin_to_obj("./test/Beckham-models/psp/face-unnamed_2142.bin", 2, False)
    #bin_to_obj("./test/Beckham-models/psp/hair-unnamed_5174.bin", 2, False)


