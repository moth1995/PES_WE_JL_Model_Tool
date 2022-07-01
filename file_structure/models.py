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
            to_float(self.model_bytes[pos + 8 : pos + 12]) * 0.025,
            to_float(self.model_bytes[pos + 4 : pos + 8]) * -0.025,
            to_float(self.model_bytes[pos : pos + 4]) * 0.025,
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

    def __init__(self,model_bytes):
        self.model_bytes = model_bytes
        self.validate()
        self.pieces_total = to_int(self.model_bytes[32 : 36])
        self.pieces_start_address = to_int(self.model_bytes[36 : 40])
        self.pieces_end_address =  to_int(self.model_bytes[44 : 48])
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
