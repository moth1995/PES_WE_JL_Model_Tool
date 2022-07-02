from PIL import Image, ImageTk
import io
import zlib
from .utils.common_functions import to_int

class PESImage() :
    PES_IMAGE_SIGNATURE = bytearray([0x94, 0x72, 0x85, 0x29,])
    width = 0
    height = 0
    bpp = 8
    pes_idat = bytearray()
    pes_palette = bytearray()

    def from_bytes(self, pes_image_bytes:bytearray):
        magic_number = pes_image_bytes[:4]
        if not self.valid_PESImage(magic_number): 
            raise Exception("not valid PES IMAGE")
        size = to_int(pes_image_bytes[8:12])
        pes_image_bytes = pes_image_bytes[:size]
        self.width = to_int(pes_image_bytes[20:22])
        self.height = to_int(pes_image_bytes[22:24])
        pes_palette_start = to_int(pes_image_bytes[18:20])
        pes_idat_start = to_int(pes_image_bytes[16:18])
        self.pes_palette = pes_image_bytes[pes_palette_start:pes_idat_start]
        self.pes_idat = pes_image_bytes[pes_idat_start:size]

    def valid_PESImage(self,magic_number : bytearray):
        return magic_number == self.PES_IMAGE_SIGNATURE
        

class PNGImage:
    PNG_SIGNATURE = bytearray([137, 80, 78, 71, 13, 10, 26, 10])
    IHDR_LENGTH = bytearray((13).to_bytes(4, byteorder='big', signed=False))
    IHDR = bytearray([73,72,68,82])
    PLTE = bytearray([80,76,84,69])
    TRNS = bytearray([116,82,78,83])
    IDAT = bytearray([73,68,65,84])
    IEND_LENGTH = bytearray(4)
    IEND = bytearray([73,69,78,68])
    iend_crc32 = bytearray(zlib.crc32(IEND).to_bytes(4, byteorder='big', signed=False))
    iend_chunk = IEND_LENGTH + IEND + iend_crc32
    TEXT = bytearray([116,69,88,116])
    keyword_author = 'Author'.encode('iso-8859-1')
    text_author = 'PES 5 Indie Team & Yerry11'.encode('iso-8859-1')
    keyword_software = 'Software'.encode('iso-8859-1')
    text_software = 'OF Team Editor'.encode('iso-8859-1')
    separator = bytearray(1)
    pes_img = PESImage()
    #def __init__(self, pes_img:PESImage):
        #self.pes_img = pes_img
        #self.png_from_pes_img16()

    def png_from_pes_img16(self):
        """
        Returns a PNG image from a pes image
        """
        IHDR_DATA = (bytearray(self.pes_img.width.to_bytes(4, byteorder='big', signed=False)) 
        +  bytearray(self.pes_img.height.to_bytes(4, byteorder='big', signed=False)) 
        + bytearray([self.pes_img.bpp, 3, 0, 0, 0]))
        ihdr_crc32 = bytearray(zlib.crc32(self.IHDR + IHDR_DATA).to_bytes(4, byteorder='big', signed=False))
        ihdr_chunk = self.IHDR_LENGTH + self.IHDR + IHDR_DATA + ihdr_crc32
        palette_data = self.pes_palette_to_RGB()
        plte_lenght = bytearray(len(palette_data).to_bytes(4, byteorder='big', signed=False))
        plte_crc32 = bytearray(zlib.crc32(self.PLTE + palette_data).to_bytes(4, byteorder='big', signed=False))
        plt_chunk = plte_lenght + self.PLTE + palette_data + plte_crc32
        trns_data = self.pes_trns_to_alpha()
        trns_lenght = bytearray(len(trns_data).to_bytes(4, byteorder='big', signed=False))
        trns_crc32 = bytearray(zlib.crc32(self.TRNS+trns_data).to_bytes(4, byteorder='big', signed=False))
        trns_chunk = trns_lenght + self.TRNS + trns_data + trns_crc32
        idat_data = self.pes_px_to_idat()
        idat_lenght = bytearray(len(idat_data).to_bytes(4, byteorder='big', signed=False))
        idat_crc32 = bytearray(zlib.crc32(self.IDAT + idat_data).to_bytes(4, byteorder='big', signed=False))
        idat_chunk = bytearray(idat_lenght + self.IDAT + idat_data + idat_crc32)
        author_data = bytearray(self.keyword_author + self.separator + self.text_author)
        author_lenght = bytearray(len(author_data).to_bytes(4, byteorder='big', signed=False))
        author_crc32 = bytearray(zlib.crc32(self.TEXT + author_data).to_bytes(4, byteorder='big', signed=False))
        author_chunk = bytearray(author_lenght + self.TEXT + author_data + author_crc32)

        software_data = bytearray(self.keyword_software + self.separator + self.text_software)
        software_lenght = bytearray(len(software_data).to_bytes(4, byteorder='big', signed=False))
        software_crc32 = bytearray(zlib.crc32(self.TEXT + software_data).to_bytes(4, byteorder='big', signed=False))
        software_chunk = bytearray(software_lenght + self.TEXT + software_data + software_crc32)

        self.png = self.PNG_SIGNATURE + ihdr_chunk + plt_chunk + trns_chunk + author_chunk + software_chunk + idat_chunk + self.iend_chunk

    def png_bytes_to_tk_img(self):
        return ImageTk.PhotoImage(Image.open(io.BytesIO(self.png)).convert("RGBA"))

    def pes_palette_to_RGB(self):
        palette_data = bytearray()
        for j in range(0, len(self.pes_img.pes_palette), 4):
            palette_data += self.pes_img.pes_palette[j : j + 3]
        return palette_data

    def pes_trns_to_alpha(self):
        trns_data = bytearray()
        for j in range(3, len(self.pes_img.pes_palette), 4):
            trns_data += self.pes_img.pes_palette[j : j + 1]
        return trns_data

    def pes_px_to_idat(self):
        step = self.pes_img.width
        if step == 32:
            step = int(step / 2)
        idat_uncompress = bytearray()
        for j in range(0, len(self.pes_img.pes_idat), step):
            idat_uncompress += self.separator + self.pes_img.pes_idat[j : j + step]
        return bytearray(zlib.compress(idat_uncompress))
