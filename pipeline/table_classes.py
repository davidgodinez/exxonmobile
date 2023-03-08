import datajoint as dj
from pdf2image import convert_from_path
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
        
            images = convert_from_path(Path(folder_path,(Documents.fetch('file_name')[document_idx])))
            for i in range(len(images)):
            # Save pages as images in the pdf
                # image = images[i].save(f'document{document_idx}_image{i+1}.png', 'PNG')
                array = np.array(images[i])
                ConvertedDocuments.Images.insert1(dict(key, image_number=i, image=array), skip_duplicates=True)
                print(f'saved document{document_idx}_image{i+1}.png')
        print(f'Finished saving images')


@schema 
class SharpenedImages(dj.Computed):
    definition = """
    -> ConvertedDocuments
    """    
    class ActualImages(dj.Part):
        definition = """
        -> SharpenedImages
        image_number: int
        ---
        image: longblob
        """

    def make(self, key):
        self.insert1(key)
        for doc_idx, documents in enumerate((ConvertedDocuments).fetch()):
            for image_idx, image in enumerate(ConvertedDocuments.Images.fetch('image')):
                data = (ConvertedDocuments.Images & f'document_id={doc_idx}' & f'image_number={image_idx}').fetch1('image')
                result = unsharp_mask(data, radius=100, amount=10)
                # sharpened_result = asarray(result)
                # fig, ax = plt.subplots(figsize=(10,10))
                # im = plt.imshow(result, cmap=plt.cm.gray)
                # ax.set_axis_off()
                # fig.tight_layout()
                # insert statement here -- insert into part table
                SharpenedImages.ActualImages.insert1(dict(key, image_number=image_idx, image=result ), skip_duplicates=True)
                print(f'sharpened document:{doc_idx}, image: {image_idx}')
                # plt.show()