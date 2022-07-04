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

    def __init__(self,model_bytes:bytes):
        self.model_bytes = model_bytes
        self.validate()
        self.pieces_total = to_int(self.model_bytes[32 : 36])
        self.pieces_start_address = to_int(self.model_bytes[36 : 40])
        self.pieces_end_address =  to_int(self.model_bytes[44 : 48])
        self.vertex_list = []
        self.vertex_normal_list = []
        self.vertex_texture_list = []
        self.polygonal_faces_list = []
        self.set_pieces()
        self.read_pieces()

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
        tri_counter = 0
        for piece in self.pieces:
            sum1 = 2
            sum2 = 4
            #print("part #", i)
            vertex_in_piece = piece[to_int(piece[8:12]) + 96 + sum1]
            #print("vertex ",vertex_in_piece)
            vertex_start_address = to_int(piece[8:12]) + 96 + sum2
            if vertex_in_piece%2!=0:
                # if the number of vertes is not pair then we need to incress the movement of bytes by two
                sum1+=2
                sum2+=2
            """
            """
            normals_in_piece = piece[vertex_in_piece * vertex_size + vertex_start_address + sum1]
            #print("normals ", normals_in_piece)
            normals_start_address = vertex_in_piece * vertex_size + vertex_start_address + sum2
            uv_in_piece = piece[normals_in_piece * vertex_size + normals_start_address + sum1]
            #print("uv ", uv_in_piece)
            uv_start_address = normals_in_piece * vertex_size + normals_start_address + sum2
            # Load vertex
            self.load_vertex(piece, vertex_in_piece, vertex_start_address)
            # Load Normals
            self.load_vertex_normal(piece, normals_in_piece, normals_start_address)
            # Load UV
            self.load_vextex_texture(piece, uv_in_piece, uv_start_address)
            # Load triangles
            self.load_polygonal_faces(piece, tri_counter)
            tri_counter+=vertex_in_piece

    def load_vertex(self, piece, vertex_in_piece, vertex_start_address):
        vertex_size = 6 # 3 int16
        factor = 0.001953
        # Load vertex
        for j in range(vertex_in_piece):
            pos = vertex_start_address + j * vertex_size
            x,y,z = struct.unpack('<3h', piece[pos : pos + vertex_size])
            #print("vertex #", j)
            #print(x * factor, y * factor, z * factor)
            self.vertex_list.append(
                Vertex(
                    x * factor, 
                    y * factor *-1, 
                    z * factor,
                )
            )

    def load_vertex_normal(self, piece, normals_in_piece, normals_start_address):
        """
        Load all vertex normals into a list
        """
        vertex_size = 6 # 3 int16
        factor = 0.001953
        for j in range(normals_in_piece):
            pos = normals_start_address + j * vertex_size
            x,y,z = struct.unpack('<3h', piece[pos : pos + vertex_size])
            #print("vertex normals #", j)
            #print(x * factor, y * factor, z * factor)
            self.vertex_normal_list.append(
                VertexNormal(
                    x * factor, 
                    y * factor *-1, 
                    z * factor,
                )
            )

    def load_vextex_texture(self, piece, uv_in_piece, uv_start_address):
        """
        Load all vertex texture (uv map coordinates) into a list
        """
        uv_size = 4 # 3 int16
        factor_uv = 0.000244
        for j in range(uv_in_piece):
            pos = uv_start_address + j * uv_size
            u, v = struct.unpack('<2h', piece[pos : pos + uv_size])
            #print("vertex texture #", j)
            #print(u * factor_uv, v * factor_uv,)
            self.vertex_texture_list.append(
                VertexTexture(
                    u * factor_uv, 
                    1 - v * factor_uv, 
                )
            )

    def load_polygonal_faces(self, piece: bytearray, tri_counter:int):
        """
        Load all polygonal faces into a list
        """
        tri_idx = bytearray([0x01, 0x00, 0x00, 0x05, 0x01, 0x01, 0x00, 0x01])
        tri_start_address = piece.find(tri_idx) + len(tri_idx)
        tri_size = piece[tri_start_address + 2] * 0x8
        tri_data = piece[tri_start_address + 4 : tri_start_address + 4 + tri_size]
        tstrip_index_list = [int((x - 32768)/4) + tri_counter if x >= 32768 else int((x)/4) + tri_counter for x in struct.unpack(f'<{int(len(tri_data)/2)}H', tri_data)]
        for k in range(len(tstrip_index_list)-2):
            if (tstrip_index_list[k] != tstrip_index_list[k + 1]) and (tstrip_index_list[k + 1] != tstrip_index_list[k + 2]) and (tstrip_index_list[k + 2] != tstrip_index_list[k]):
                if k & 1:
                    self.polygonal_faces_list.append(
                        PolygonalFace(
                            tstrip_index_list[k + 1],
                            tstrip_index_list[k],
                            tstrip_index_list[k + 2]
                        )
                    )
                else:
                    self.polygonal_faces_list.append(
                        PolygonalFace(
                            tstrip_index_list[k],
                            tstrip_index_list[k + 1],
                            tstrip_index_list[k + 2]
                        )
                    )

class FacePSPModel:
    magic_number = bytearray([0x03,0x00,0xFF,0xFF])
    data_size = 14 # 3 int16

    def __init__(self,model_bytes:bytes):
        self.model_bytes = model_bytes
        self.validate()
        self.pieces_total = to_int(self.model_bytes[32 : 36])
        #print("total of parts here is: ", self.pieces_total)
        self.pieces_start_address = to_int(self.model_bytes[36 : 40])
        self.pieces_end_address =  to_int(self.model_bytes[44 : 48])
        self.vertex_list = []
        self.vertex_normal_list = []
        self.vertex_texture_list = []
        self.polygonal_faces_list = []
        self.set_pieces()
        self.read_pieces()

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
        tri_counter = 1
        for i, piece in enumerate(self.pieces):
            #print("part #", i)
            vertex_in_piece = to_int(piece[92:94])
            vertex_start_address = to_int(piece[8:12])
            #print("vertex in this part: ",vertex_in_piece, " vertex start address: ", vertex_start_address)
            normals_start_address = vertex_start_address + 6
            uv_start_address = normals_start_address + 4
            tri_start_address = to_int(piece[12:16])
            tri_list_size = to_int(piece[16:20])
            
            #print("tri start address: ", tri_start_address, " tri list size: ", tri_list_size)
            
            self.load_vertex(piece, vertex_in_piece, vertex_start_address)
            # Load Normals !!!! NOT IMPLEMENTED YET NORMALS MUST BE X Y Z BUT IN PSP ARE JUST TWO INT16 VALUES
            #self.load_vertex_normal(piece, vertex_in_piece, normals_start_address)
            # Load UV
            self.load_vextex_texture(piece, vertex_in_piece, uv_start_address)
            # Load triangles in psp there are some parts that dont have triangles, we need to figure it out what to do with it
            if tri_start_address !=0:
                self.load_polygonal_faces(piece, tri_start_address, tri_list_size, tri_counter)
            tri_counter+=vertex_in_piece
            #if i==2:
                #raise NotImplementedError()

    def load_vertex(self, piece, vertex_in_piece, vertex_start_address):
        for i in range(vertex_in_piece):
            pos = vertex_start_address + (self.data_size * i)
            x,y,z = struct.unpack('<3h', piece[pos : pos + 6])
            #print(x,y,z)
            vertex = Vertex(
                x * 0.00001,
                y * 0.00001 *-1,
                z * 0.00001,
            )
            self.vertex_list.append(vertex)

    def load_vertex_normal(self, piece, normals_in_piece, normals_start_address):
        """
        Load all vertex normals into a list
        """
        raise NotImplementedError()

    def load_vextex_texture(self, piece, uv_in_piece, uv_start_address):
        """
        Load all vertex texture (uv map coordinates) into a list
        """
        for i in range(uv_in_piece):
            pos = uv_start_address + (self.data_size * i)
            u,v = struct.unpack('<2h', piece[pos : pos + 4])
            self.vertex_texture_list.append(
                VertexTexture(
                    u * 0.000244,
                    1 - v * 0.000244,
                )
            )

    def load_polygonal_faces(self, piece, tri_start_address, tri_size, tri_counter):
        """
        Load all polygonal faces into a list
        """
        #print(tri_size * 2)
        #print(tri_start_address)
        tstrip_index_list = [x + tri_counter for x in struct.unpack(f'<{tri_size}H', piece[tri_start_address : tri_start_address + tri_size * 2])]
        #print(tstrip_index_list)
        for k in range(len(tstrip_index_list)-2):
            if (tstrip_index_list[k] != tstrip_index_list[k + 1]) and (tstrip_index_list[k + 1] != tstrip_index_list[k + 2]) and (tstrip_index_list[k + 2] != tstrip_index_list[k]):
                if k & 1:
                    #print(tstrip_index_list[k + 1], tstrip_index_list[k], tstrip_index_list[k + 2])
                    self.polygonal_faces_list.append(
                        PolygonalFace(
                            tstrip_index_list[k + 1],
                            tstrip_index_list[k],
                            tstrip_index_list[k + 2]
                        )
                    )
                else:
                    #print(tstrip_index_list[k], tstrip_index_list[k + 1], tstrip_index_list[k + 2])
                    self.polygonal_faces_list.append(
                        PolygonalFace(
                            tstrip_index_list[k],
                            tstrip_index_list[k + 1],
                            tstrip_index_list[k + 2]
                        )
                    )






