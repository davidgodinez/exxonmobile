import datajoint as dj
# from pdf2image import convert_from_path
import fitz
import io
from pathlib import Path
from PIL import Image
import numpy as np
from skimage.filters import unsharp_mask
import matplotlib.pyplot as plt
from numpy import asarray

schema = dj.Schema("exxonmobile")
folder_path = '../files'


@schema # 
class Documents(dj.Manual):
    definition = """
    document_id: int    # unique id for document
    ---
    datetime: varchar(50)   # time document was imported into table 
    file_name: varchar(1000)  # document filename

    """


@schema 
class ConvertedDocuments(dj.Imported):
    definition = """
    -> Documents     # using Documents' primary key as foreign key 
    """
    class Images(dj.Part):
        definition = """
        -> ConvertedDocuments
        image_number: int
        ---
        image: longblob
        """

    def make(self, key):
            self.insert1(key)
            for document_idx, document in enumerate(Documents.fetch('file_name')):
                print(document_idx, '=', document)
                doc = fitz.open(Path(folder_path,(Documents.fetch('file_name')[document_idx])))
                for page_number in range(len(doc)):
                    page = doc.load_page(page_number)
                    pix = page.get_pixmap(alpha=False)

                    # Save pixmap as a PNG image in memory
                    buffer = io.BytesIO()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    img.save(buffer, format='PNG')

                    # Store the PNG image as a longblob in the table
                    ConvertedDocuments.Images.insert1(dict(key, image_number=page_number + 1, image=buffer.getvalue()))

