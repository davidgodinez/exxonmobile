import os
from PIL import Image, ImageDraw
import io
from PDFloader import PDFFileLoader
from table_classes import FormRecognizer
import cv2
import numpy as np
import matplotlib.pyplot as plt
import json


def dataloader():
    """
    This function loads the pdf file paths into the Documents Table, and calls the Form Recognizer api to read each document. The data returned is stored in the 
    FormRecognizer table and all its corresponding part tables.
    """
    parent_directory = os.getcwd()
    folder_path = f'{parent_directory}/files'
    loader = PDFFileLoader(folder_path=folder_path)
    loader.load_files()
    FormRecognizer.populate()
    print('Form Recognizer populated!')


def full_image_shower(document_id, page_number, scale_factor=2.0):
    """ This function shows the user the a full page with the handwritten text boxed in red.

    Args:
        document_id (int): document_id from FormRecognizer.PDFPages table
        page_number (int): Page Num
        scale_factor (float, optional): _description_. Defaults to 2.0.

    Returns:
        int: the number of pages in the document.
    """
    image = (FormRecognizer.PDFPages & f'document_id={document_id}' & f'page_number={page_number}').fetch1('page_image')
    boxed_image_pil = Image.open(io.BytesIO(image))
    
    # Resize the image
    new_width = int(boxed_image_pil.width * scale_factor)
    new_height = int(boxed_image_pil.height * scale_factor)
    resized_image = boxed_image_pil.resize((new_width, new_height), Image.ANTIALIAS)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(resized_image)
    ax.set_title("Full Image with Boxes")
    ax.axis("off")
    
    plt.show()

    return len(FormRecognizer.PDFPages & f'document_id={document_id}')



def Form_recognizer_box_shower(document_id, page_number, box_number):
    """This function 

    Args:
        document_id (int): document_id from FormRecognizer.BoxedImageBlobs table
        page_number (int): page_number from FormRecognizer.BoxedImageBlobs table
        box_number (int): box_number from FormRecognizer.BoxedImageBlobs table
    Returns:

    """
    full_boxed_image = (FormRecognizer.PDFPages & {'document_id': document_id, 'page_number': page_number}).fetch1('page_image')
    boxed_image_pil = Image.open(io.BytesIO(full_boxed_image))
    
    boxed_image_blob = (FormRecognizer.BoxedImageBlobs & {'document_id': document_id, 'page_number': page_number, 'box_number': box_number}).fetch1('boxed_image')
    confidence = (FormRecognizer.BoxedImageBlobs & {'document_id': document_id, 'page_number': page_number, 'box_number': box_number}).fetch1('confidence')
    boxed_image = Image.open(io.BytesIO(boxed_image_blob))
    text = (FormRecognizer.BoxedImageBlobs & {'document_id': document_id, 'page_number': page_number, 'box_number': box_number}).fetch1('form_recognizer_text')
    
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    axes[0].imshow(boxed_image_pil)
    axes[0].set_title("Full Image with Boxes")
    axes[0].axis("off")
    
    axes[1].imshow(boxed_image)
    axes[1].set_title(f"Text: {text} - Confidence: {confidence:.2f}")
    axes[1].axis("off")
    
    plt.show()




if __name__ == '__main__':
   dataloader()