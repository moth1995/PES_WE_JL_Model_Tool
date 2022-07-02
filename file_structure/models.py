import struct
from .object_3d import PolygonalFace, Vertex, VertexNormal, VertexTexture
from .utils.common_functions import to_float, to_int

class FacePCModel:
    magic_number = bytearray([0x20,0x05,0x04,0x20])
    data_size = 32

    def __init__(self,model_bytes):
        self.model_bytes = model_bytes
        self.validate()
        self.parts_counter_address = to_int(self.model_bytes[16:20])
        self.vertex_count_address = to_int(self.model_bytes[16:20]) + 8
        self.vertex_count = to_int(self.model_bytes[self.vertex_count_address : self.vertex_count_address + 2])
        self.vertex_start_address = self.vertex_count_address + 8
        self.vertex_normal_start_address = self.vertex_start_address + 12
        self.vextex_texture_start_address = self.vertex_start_address + 24
        self.load_vertex()
        self.load_vertex_normal()
        self.load_vextex_texture()
        self.poly_faces_address = to_int(self.model_bytes[20:24])
        self.poly_faces_count = to_int(self.model_bytes[self.poly_faces_address : self.poly_faces_address + 2])
        self.poly_faces_start_address = self.poly_faces_address + 2
        self.load_polygonal_faces()

    @property
    def parts_offset_table_address(self):
        return self.parts_counter_address + 4

    def validate(self):
        """
        Function to check if we have a proper PES PC Model
        """
        if self.magic_number != self.model_bytes[:4]:
            raise ValueError("Not a PC face model!")
        return True

    def load_vertex(self):
        """
        Load all vertex into a list
        """
        self.vertex_list = []
        for i in range(self.vertex_count):
            pos = self.vertex_start_address + (self.data_size * i)
            vertex = Vertex(
            (to_float(self.model_bytes[pos + 8 : pos + 12]) * 0.025) * 1.25029,
            ((to_float(self.model_bytes[pos + 4 : pos + 8]) * -0.025) * 1.25029) - 0.751679,
            (to_float(self.model_bytes[pos : pos + 4]) * 0.025) * 1.25029,
            )
            self.vertex_list.append(vertex)

    def load_vertex_normal(self):
        """
        Load all vertex normals into a list
        """
        self.vertex_normal_list = []
        for i in range(self.vertex_count):
            pos = self.vertex_normal_start_address + (self.data_size * i)
            vertex_normal = VertexNormal(
            to_float(self.model_bytes[pos + 8 : pos + 12]) * 0.025,
            to_float(self.model_bytes[pos + 4 : pos + 8]) * -0.025,
            to_float(self.model_bytes[pos : pos + 4]) * 0.025,
            )
            self.vertex_normal_list.append(vertex_normal)

    def load_vextex_texture(self):
        """
        Load all vertex texture (uv map coordinates) into a list
        """
        self.vertex_texture_list = []
        for i in range(self.vertex_count):
            pos = self.vextex_texture_start_address + (self.data_size * i)
            vertex_texture = VertexTexture(
            to_float(self.model_bytes[pos : pos + 4]),
            (1 - to_float(self.model_bytes[pos + 4 : pos + 8])),
            )
            self.vertex_texture_list.append(vertex_texture)
    
    def load_polygonal_faces(self):
        """
        Load all polygonal faces into a list
        """
        self.polygonal_faces_list = []
        tstrip_index_list = []
        for i in range(self.poly_faces_count):
            idx=to_int(self.model_bytes[
                    self.poly_faces_start_address + i * 2 : self.poly_faces_start_address + i * 2 + 2
                    ]) + 1
            tstrip_index_list.append(idx)

        for i in range(0, self.poly_faces_count - 2, 1):
            if (tstrip_index_list[i] != tstrip_index_list[i + 1]) and (tstrip_index_list[i + 1] != tstrip_index_list[i + 2]) and (tstrip_index_list[i + 2] != tstrip_index_list[i]):
                if i & 1:
                    self.polygonal_faces_list.append(
                        PolygonalFace(
                            tstrip_index_list[i + 1],
                            tstrip_index_list[i],
                            tstrip_index_list[i + 2]
                        )
                    )
                else:
                    self.polygonal_faces_list.append(
                        PolygonalFace(
                            tstrip_index_list[i],
                            tstrip_index_list[i + 1],
                            tstrip_index_list[i + 2]
                        )
                    )

class FacePS2Model:
    magic_number = bytearray([0x03,0x00,0xFF,0xFF])
    data_size = 32

    def __init__(self,model_bytes:bytes):
        self.model_bytes = model_bytes
        self.validate()
        self.pieces_total = to_int(self.model_bytes[32 : 36])
        self.pieces_start_address = to_int(self.model_bytes[36 : 40])
        self.pieces_end_address =  to_int(self.model_bytes[44 : 48])
        self.set_pieces()
        self.read_pieces()
        self.vertex_count_address = to_int(self.model_bytes[16:20]) + 8
        self.vertex_count = to_int(self.model_bytes[self.vertex_count_address : self.vertex_count_address + 2])
        self.vertex_start_address = self.vertex_count_address + 8
        self.vertex_normal_start_address = self.vertex_start_address + 12
        self.vextex_texture_start_address = self.vertex_start_address + 24
        self.vertex_list = []
        self.vertex_normal_list = []
        self.vertex_texture_list = []
        self.load_vertex()
        self.load_vertex_normal()
        self.load_vextex_texture()
        self.poly_faces_address = to_int(self.model_bytes[20:24])
        self.poly_faces_count = to_int(self.model_bytes[self.poly_faces_address : self.poly_faces_address + 2])
        self.poly_faces_start_address = self.poly_faces_address + 2
        self.load_polygonal_faces()

    def validate(self):
        """
        Function to check if we have a proper PES PS2 Model
        """
        if self.magic_number != self.model_bytes[:4]:
            raise ValueError("Not a PS2 face model!")
        return True

    def set_pieces(self):
        """
        A PS2 Model is divided by pieces or parts, called it as you want
        here we get all the pieces bytes into a list from the whole model bytes
        """
        pieces_bytes = self.model_bytes[self.pieces_start_address : self.pieces_end_address]
        sum_address = 0
        self.pieces = []
        i = 0
        while i < self.pieces_total:
            piece_size = to_int(pieces_bytes[sum_address : sum_address + 4])
            self.pieces.append(pieces_bytes[sum_address : sum_address + piece_size])
            sum_address += piece_size
            i +=1

    def read_pieces(self):
        vertex_size = 6 # 3 int16
        uv_size = 4 # 2 int16
        factor = 0.001953
        vertex_total = 0
        normals_total = 0
        uv_total = 0
        tri_idx = bytearray([0x01, 0x00, 0x00, 0x05, 0x01, 0x01, 0x00, 0x01])
        for i, piece in enumerate(self.pieces):
            sum1 = 2
            sum2 = 4
            print("part ", i)
            vertex_in_piece = piece[to_int(piece[8:12]) + 96 + sum1]
            print("vertex ",vertex_in_piece)
            vertex_start_address = to_int(piece[8:12]) + 96 + sum2
            if vertex_in_piece%2!=0:
                # if the number of vertes is not pair then we need to incress the movement of bytes by two
                sum1+=2
                sum2+=2
            normals_in_piece = piece[vertex_in_piece * vertex_size + vertex_start_address + sum1]
            print("normals ", normals_in_piece)
            normals_start_address = vertex_in_piece * vertex_size + vertex_start_address + sum2
            uv_in_piece = piece[normals_in_piece * vertex_size + normals_start_address + sum1]
            print("uv ", uv_in_piece)
            uv_start_address = normals_in_piece * vertex_size + normals_start_address + sum2
            if vertex_in_piece != normals_in_piece and vertex_in_piece != uv_in_piece:
                with open(f"piece{i}.bin","wb") as f:
                    f.write(piece)
            for j in range(vertex_in_piece):
                x,y,z = struct.unpack('<3h', piece[vertex_start_address + j * vertex_size : vertex_start_address + j * vertex_size + vertex_size])
                print("vertex #", j)
                print(x * factor, y * factor, z * factor)
            vertex_total+=vertex_in_piece
            normals_total+=normals_in_piece
            uv_total+=uv_in_piece
        print(vertex_total)
        print(normals_total)
        print(uv_total)
        raise NotImplementedError()

    def load_vertex(self):
        """
        Load all vertex into a list
        """
        for i in range(self.vertex_count):
            pos = self.vertex_start_address + (self.data_size * i)
            vertex = Vertex(
            to_float(self.model_bytes[pos + 8 : pos + 12]) * 0.025,
            to_float(self.model_bytes[pos + 4 : pos + 8]) * -0.025,
            to_float(self.model_bytes[pos : pos + 4]) * 0.025,
            )
            self.vertex_list.append(vertex)

    def load_vertex_normal(self):
        """
        Load all vertex normals into a list
        """
        for i in range(self.vertex_count):
            pos = self.vertex_normal_start_address + (self.data_size * i)
            vertex_normal = VertexNormal(
            to_float(self.model_bytes[pos + 8 : pos + 12]) * 0.025,
            to_float(self.model_bytes[pos + 4 : pos + 8]) * -0.025,
            to_float(self.model_bytes[pos : pos + 4]) * 0.025,
            )
            self.vertex_normal_list.append(vertex_normal)

    def load_vextex_texture(self):
        """
        Load all vertex texture (uv map coordinates) into a list
        """
        for i in range(self.vertex_count):
            pos = self.vextex_texture_start_address + (self.data_size * i)
            vertex_texture = VertexTexture(
            to_float(self.model_bytes[pos : pos + 4]),
            (1 - to_float(self.model_bytes[pos + 4 : pos + 8])),
            )
            self.vertex_texture_list.append(vertex_texture)
    
    def load_polygonal_faces(self):
        """
        Load all polygonal faces into a list
        """
        self.polygonal_faces_list = []
        # First we read index into a list, int16
        tstrip_index_list = [
            to_int(
                self.model_bytes[
                    self.poly_faces_start_address + i * 2 : self.poly_faces_start_address + i * 2 + 2
                    ]
                ) + 1 for i in range(self.poly_faces_count)
            ]

        # Now we create the triangles

        for i in range(self.poly_faces_count - 2):
            if i % 2 == 0:
                self.polygonal_faces_list.append(
                    PolygonalFace(
                        tstrip_index_list[i],
                        tstrip_index_list[i + 1],
                        tstrip_index_list[i + 2]
                    )
                )
            else:
                self.polygonal_faces_list.append(
                    PolygonalFace(
                        tstrip_index_list[i + 1],
                        tstrip_index_list[i],
                        tstrip_index_list[i + 2]
                    )
                )
            if (tstrip_index_list[i] != tstrip_index_list[i+1]) and (tstrip_index_list[i] != tstrip_index_list[i+2]):
                i+=3
