import datajoint as dj
import fitz
import io
from pathlib import Path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from numpy import asarray
import cv2
from io import BytesIO
from boxing import boxing

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



@schema
class BoxedImages(dj.Imported):
    definition = """
    -> ConvertedDocuments.Images   # using ConvertedDocuments.Images primary key as foreign key
    """
    
    class BoxedImageBlobs(dj.Part):
        definition = """
        -> BoxedImages
        box_number: int
        ---
        boxed_image: longblob
        """

    class BoxedImageComments(dj.Part):
        definition = """
        -> BoxedImages.BoxedImageBlobs
        ---
        comment: varchar(1000)
        """

    def make(self, key):
        image_blob = (ConvertedDocuments.Images & key).fetch1('image')
        image = cv2.imdecode(np.frombuffer(image_blob, np.uint8), cv2.IMREAD_COLOR)
        cnts = boxing(image)

        # Insert the key into the BoxedImages table
        self.insert1(key)

        for idx, c in enumerate(cnts):
            x, y, w, h = cv2.boundingRect(c)
            boxed_image = image[y:y + h, x:x + w]

            # Save the boxed image as a PNG in memory
            boxed_buffer = BytesIO()
            boxed_image_pil = Image.fromarray(cv2.cvtColor(boxed_image, cv2.COLOR_BGR2RGB))
            boxed_image_pil.save(boxed_buffer, format='PNG')

            # Store the boxed image in the BoxedImageBlobs table
            BoxedImages.BoxedImageBlobs.insert1(dict(key, box_number=idx + 1, boxed_image=boxed_buffer.getvalue()))
