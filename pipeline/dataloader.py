import os
from PIL import Image
import io
from PDFloader import PDFFileLoader
from table_classes import ConvertedDocuments, BoxedImages

def dataloader():
    parent_directory = os.getcwd()
    folder_path = f'{parent_directory}/files'
    loader = PDFFileLoader(folder_path=folder_path)
    loader.load_files()
    ConvertedDocuments.populate()
    print('ConvertedDocuments populated')
    BoxedImages.populate()
    print('BoxedImages populated')
    print('Populate complete!')


def full_image_shower(document_id, image_number):
    image = (ConvertedDocuments.Images & f'document_id={document_id}' & f'image_number={image_number}').fetch1('image')
    boxed_image = Image.open(io.BytesIO(image))
    boxed_image.show()


def box_shower(document_id, image_number, box_number):
    image = (BoxedImages.BoxedImageBlobs & f'document_id={document_id}' & f'image_number={image_number}' & f'box_number={box_number}').fetch1('boxed_image')
    boxed_image = Image.open(io.BytesIO(image))
    boxed_image.show()






if __name__ == '__main__':
    dataloader()
    full_image_shower(document_id=0, image_number=3)
    box_shower(document_id=0, image_number=3, box_number=10)
