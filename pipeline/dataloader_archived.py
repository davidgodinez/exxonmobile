import os
from PIL import Image, ImageDraw
import io
from PDFloader import PDFFileLoader
from table_classes import ConvertedDocuments, BoxedImages, AzureBoxedImages, FormRecognizer
from boxing import boxing, draw
import cv2
import numpy as np
import matplotlib.pyplot as plt
import json


def dataloader():
    parent_directory = os.getcwd()
    folder_path = f'{parent_directory}/files'
    # folder_path = f'{parent_directory}'    
    loader = PDFFileLoader(folder_path=folder_path)
    loader.load_files()
    ConvertedDocuments.populate()
    print('ConvertedDocuments populated')
    # BoxedImages.populate()
    # print('BoxedImages populated')
    # AzureBoxedImages.populate()
    # print('AzureBoxedImages populated!')
    FormRecognizer.populate()
    print('Form Recognizer populated!')


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

    return len(ConvertedDocuments.Images & f'document_id={document_id}')


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


def Azure_box_shower(document_id, image_number, box_number):
    full_boxed_image = (AzureBoxedImages & {'document_id': document_id, 'image_number': image_number}).fetch1('full_boxed_image')
    boxed_image_pil = Image.open(io.BytesIO(full_boxed_image))
    
    boxed_image_blob = (AzureBoxedImages.AzureBoxedImageBlobs & {'document_id': document_id, 'image_number': image_number, 'box_number': box_number}).fetch1('boxed_image')
    ocr_prob = (AzureBoxedImages.AzureBoxedImageBlobs & {'document_id': document_id, 'image_number': image_number, 'box_number': box_number}).fetch1('ocr_prob')
    boxed_image = Image.open(io.BytesIO(boxed_image_blob))
    
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    axes[0].imshow(boxed_image_pil)
    axes[0].set_title("Full Image with Boxes")
    axes[0].axis("off")
    
    axes[1].imshow(boxed_image)
    axes[1].set_title(f"Box {box_number} - OCR Probability: {ocr_prob:.2f}")
    axes[1].axis("off")
    
    plt.show()


def Form_recognizer_box_shower(document_id, image_number, box_number):
    full_boxed_image = (FormRecognizer & {'document_id': document_id, 'image_number': image_number}).fetch1('form_recognizer_image')
    boxed_image_pil = Image.open(io.BytesIO(full_boxed_image))
    
    boxed_image_blob = (FormRecognizer.FormRecognizerBoxedImageBlobs & {'document_id': document_id, 'image_number': image_number, 'box_number': box_number}).fetch1('boxed_image')
    ocr_prob = (FormRecognizer.FormRecognizerBoxedImageBlobs & {'document_id': document_id, 'image_number': image_number, 'box_number': box_number}).fetch1('ocr_prob')
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


def Azure_boxed_paragraph_shower(document_id, image_number, paragraph_number):
    full_boxed_image = (AzureBoxedImages & {'document_id': document_id, 'image_number': image_number}).fetch1('full_boxed_image')
    boxed_image_pil = Image.open(io.BytesIO(full_boxed_image))
    
    boxed_paragraph_blob = (AzureBoxedImages.AzureBoxedParagraphBlobs & {'document_id': document_id, 'image_number': image_number, 'paragraph_number': paragraph_number}).fetch1('boxed_paragraph')
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
    
    
def Azure_average_ocr_prob(document, image):
    # Fetch the OCR probabilities for the given document and image
    ocr_probs = (AzureBoxedImages.AzureBoxedImageBlobs & f"document_id={document}" & f"image_number={image}").fetch('ocr_prob')

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



def Azure_export_to_json(document_id, image_number):
    # Get the full_text from the AzureBoxedImages table
    full_text = (AzureBoxedImages & f'document_id={document_id}' & f'image_number={image_number}').fetch1('full_text')

    
    # Create a dictionary to store the data
    data = {
        'document_id': document_id,
        'image_number': image_number,
        'average_ocr_prob': Azure_average_ocr_prob(document=document_id, image=image_number),
        'full_text': full_text
    }
    
    # Export the data to a JSON file
    filename = f"document_Azure_{document_id}_image_{image_number}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)




def Form_recognizer_export_to_json(document_id, image_number):

    # Fetch the required data from FormRecognizer and FormRecognizerBoxedImageBlobs
    data = (FormRecognizer & {'document_id': document_id, 'image_number': image_number}).fetch1()
    boxed_image_blobs = (FormRecognizer.FormRecognizerBoxedImageBlobs & {'document_id': document_id, 'image_number': image_number}).fetch('form_recognizer_text', 'ocr_prob')

    # Prepare the output data
    exported_data = {
        'document_id': document_id,
        'image_number': image_number,
        'average_ocr_prob': data['average_form_recognizer_text_confidence'],
        'full_text': [{'text': str(boxed_image_blobs[0][num]), 'probability': float(boxed_image_blobs[1][num])} for num in range(len(boxed_image_blobs[0]))]
    }

    # Export the data to a JSON file
    filename = f"document_Form_recognizer_{document_id}_image_{image_number}.json"
    with open(filename, 'w') as f:
        json.dump(exported_data, f, indent=4)




def form_recognizer_full_image_shower(document_id, image_number, scale_factor=2.0):
    image = (FormRecognizer & f'document_id={document_id}' & f'image_number={image_number}').fetch1('form_recognizer_image')
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

    return len(FormRecognizer & f'document_id={document_id}')











if __name__ == '__main__':
    full_image_with_boxes_shower(0,5)