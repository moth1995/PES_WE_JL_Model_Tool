from file_structure import FacePCModel, Container, unzlib_it, file_read
from pathlib import Path

def create_obj(pes_model:FacePCModel, folder:str, filename:str):
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

        obj_file.writelines("\n")
        obj_file.writelines(f"# Normals {len(pes_model.vertex_normal_list)}\n")
        for i in range(len(pes_model.vertex_normal_list)):
            obj_file.writelines(f"vn  {pes_model.vertex_normal_list[i].x} {pes_model.vertex_normal_list[i].y} {pes_model.vertex_normal_list[i].z}\n")

        obj_file.writelines("\n")
        obj_file.writelines("usemtl material1\n")
        obj_file.writelines("\n")
        obj_file.writelines(f"# Faces {len(pes_model.polygonal_faces_list)}\n")
        for i in range(len(pes_model.polygonal_faces_list)):
            obj_file.write(f"f  "
            + f"{pes_model.polygonal_faces_list[i].i1}/{pes_model.polygonal_faces_list[i].i1}/{pes_model.polygonal_faces_list[i].i1} "
            + f"{pes_model.polygonal_faces_list[i].i2}/{pes_model.polygonal_faces_list[i].i2}/{pes_model.polygonal_faces_list[i].i2} "
            + f"{pes_model.polygonal_faces_list[i].i3}/{pes_model.polygonal_faces_list[i].i3}/{pes_model.polygonal_faces_list[i].i3}\n"
            )

def create_mtl(folder:str, filename:str):
    with open(f'{folder}/{filename}.mtl',"w") as mtl_file:
        mtl_file.writelines("newmtl material1 \n")
        mtl_file.writelines(f"\tmap_Kd {filename}.png \n")

def get_container(unzlibed_file:bytearray):
    return Container(unzlibed_file)

def get_face_hair_model(file_location:str):
    bin_file = file_read(file_location)
    decompress_bin_file = unzlib_it(bin_file[32:])
    file_ctn = get_container(decompress_bin_file)
    return FacePCModel(file_ctn.files[0])

def main():
    # from a string we get a Path object and from that we get the values that we need
    bin_location = Path("./Beckham-models/pc/face-unnamed_2009.bin")
    bin_full_path = str(bin_location.resolve())
    bin_filename = bin_location.stem
    bin_folder_location = str(bin_location.parent)
    
    model = get_face_hair_model(bin_full_path)
    
    create_obj(model, bin_folder_location, bin_filename)
    create_mtl(bin_folder_location, bin_filename)

if __name__ == "__main__":
	main()
