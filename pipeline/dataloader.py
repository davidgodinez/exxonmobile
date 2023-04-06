import os
from PIL import Image
import io
from PDFloader import PDFFileLoader
from table_classes import ConvertedDocuments, BoxedImages
from boxing import boxing, draw
import cv2
import numpy as np
import matplotlib.pyplot as plt


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


def box_shower(document_id, image_number, box_number, scale_factor=2):
    image = (BoxedImages.BoxedImageBlobs & f'document_id={document_id}' & f'image_number={image_number}' & f'box_number={box_number}').fetch1('boxed_image')
    boxed_image = Image.open(io.BytesIO(image))
    
    # Enlarge the image by the specified scale factor
    width, height = boxed_image.size
    enlarged_image = boxed_image.resize((width * scale_factor, height * scale_factor), Image.ANTIALIAS)
    
    enlarged_image.show()


def show_image_with_boxes(image):
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    cnts = boxing(img)
    draw(img, cnts)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img_rgb)


def full_image_with_boxes_shower(document_id, image_number, scale_factor=2.0):
    full_boxed_image = (BoxedImages & {'document_id': document_id, 'image_number': image_number}).fetch1('full_boxed_image')
    boxed_image_pil = Image.open(io.BytesIO(full_boxed_image))
    
    # Resize the image
    new_width = int(boxed_image_pil.width * scale_factor)
    new_height = int(boxed_image_pil.height * scale_factor)
    resized_image = boxed_image_pil.resize((new_width, new_height), Image.ANTIALIAS)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(resized_image)
    ax.set_title("Full Image with Boxes")
    ax.axis("off")
    
    plt.show()




def boxed_paragraph_shower(document_id, image_number, paragraph_number):
    full_boxed_image = (BoxedImages & {'document_id': document_id, 'image_number': image_number}).fetch1('full_boxed_image')
    boxed_image_pil = Image.open(io.BytesIO(full_boxed_image))
    
    boxed_paragraph_blob = (BoxedImages.BoxedParagraphBlobs & {'document_id': document_id, 'image_number': image_number, 'paragraph_number': paragraph_number}).fetch1('boxed_paragraph')
    boxed_paragraph_pil = Image.open(io.BytesIO(boxed_paragraph_blob))
    
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    axes[0].imshow(boxed_image_pil)
    axes[0].set_title("Full Image with Boxes")
    axes[0].axis("off")
    
    axes[1].imshow(boxed_paragraph_pil)
    axes[1].set_title(f"Paragraph {paragraph_number}")
    axes[1].axis("off")
    
    plt.show()






if __name__ == '__main__':
    full_image_with_boxes_shower(0,5)