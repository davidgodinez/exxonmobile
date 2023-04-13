import os
from PIL import Image, ImageDraw
import io
from PDFloader import PDFFileLoader
from table_classes import ConvertedDocuments, BoxedImages
from boxing import boxing, draw
import cv2
import numpy as np
import matplotlib.pyplot as plt
import json


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


def full_image_shower(document_id, image_number, scale_factor=2.0):
    image = (ConvertedDocuments.Images & f'document_id={document_id}' & f'image_number={image_number}').fetch1('image')
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


def box_shower(document_id, image_number, box_number):
    full_boxed_image = (BoxedImages & {'document_id': document_id, 'image_number': image_number}).fetch1('full_boxed_image')
    boxed_image_pil = Image.open(io.BytesIO(full_boxed_image))
    
    boxed_image_blob = (BoxedImages.BoxedImageBlobs & {'document_id': document_id, 'image_number': image_number, 'box_number': box_number}).fetch1('boxed_image')
    ocr_prob = (BoxedImages.BoxedImageBlobs & {'document_id': document_id, 'image_number': image_number, 'box_number': box_number}).fetch1('ocr_prob')
    boxed_image = Image.open(io.BytesIO(boxed_image_blob))
    
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    axes[0].imshow(boxed_image_pil)
    axes[0].set_title("Full Image with Boxes")
    axes[0].axis("off")
    
    axes[1].imshow(boxed_image)
    axes[1].set_title(f"Box {box_number} - OCR Probability: {ocr_prob:.2f}")
    axes[1].axis("off")
    
    plt.show()



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


def average_ocr_prob(document, image):
    # Fetch the OCR probabilities for the given document and image
    ocr_probs = (BoxedImages.BoxedImageBlobs & f"document_id={document}" & f"image_number={image}").fetch('ocr_prob')

    # Calculate and return the average OCR probability
    if len(ocr_probs) > 0:
        return sum(ocr_probs) / len(ocr_probs)
    else:
        return 0




def export_to_json(document_id, image_number):
    # Get the full_text from the BoxedImages table
    full_text = (BoxedImages & f'document_id={document_id}' & f'image_number={image_number}').fetch1('full_text')

    
    # Create a dictionary to store the data
    data = {
        'document_id': document_id,
        'image_number': image_number,
        'average_ocr_prob': average_ocr_prob(document=document_id, image=image_number),
        'full_text': full_text
    }
    
    # Export the data to a JSON file
    filename = f"document_{document_id}_image_{image_number}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)







if __name__ == '__main__':
    full_image_with_boxes_shower(0,5)