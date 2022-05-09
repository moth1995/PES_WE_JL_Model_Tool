from file_structure import FacePCModel, Container, unzlib_it, file_read

def create_obj(pes_model:FacePCModel, bin_source:str):
    with open ("Messi.obj","w") as obj_file:
        obj_file.writelines("# PES/WE/JL Model Tool\n")
        obj_file.writelines(f"# OBJ Model {bin_source}\n")
        obj_file.writelines("\n")
        obj_file.writelines("mtllib Messi.mtl\n")
        obj_file.writelines("\n")
        obj_file.writelines("o Messi_face \n")
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

def create_mtl():
    with open('Messi.mtl',"w") as mtl_file:
        mtl_file.writelines("newmtl material1 \n")
        mtl_file.writelines("\tmap_Kd Messi.png \n")

def get_face_hair_model(file_location:str):
    bin_file = file_read(file_location)
    decompress_bin_file = unzlib_it(bin_file[32:])
    file_ctn = Container(decompress_bin_file)
    return FacePCModel(file_ctn.files[0])

def main():
    bin_location = "Messi.bin"
    face_pc_model = get_face_hair_model(bin_location)
    create_obj(face_pc_model, bin_location)
    create_mtl()

if __name__ == "__main__":
	main()
