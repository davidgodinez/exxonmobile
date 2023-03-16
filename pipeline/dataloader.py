import os
from PIL import Image
import io
from PDFloader import PDFFileLoader
from table_classes import ConvertedDocuments, BoxedImages
from boxing import boxing, draw
import cv2
import numpy as np


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



def full_image_with_boxes_shower(document_id, image_number):
    # Load the image from the database
    image = (ConvertedDocuments.Images & f'document_id={document_id}' & f'image_number={image_number}').fetch1('image')
    pil_image = Image.open(io.BytesIO(image))

    # Convert the PIL image to an OpenCV image (BGR format)
    cv2_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Get the contours using boxing function
    contours = boxing(cv2_image)

    # Draw the contours as rectangles on the image
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(cv2_image, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Convert the OpenCV image back to a PIL.Image (RGB format)
    pil_image_with_boxes = Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))

    # Show the image with boxes
    pil_image_with_boxes.show()


if __name__ == '__main__':
    full_image_with_boxes_shower(0,5)