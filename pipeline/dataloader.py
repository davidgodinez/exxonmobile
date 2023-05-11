import os
from PIL import Image, ImageDraw
import io
from PDFloader import PDFFileLoader
from table_classes import FormRecognizer
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
    # print('ConvertedDocuments populated')
    # BoxedImages.populate()
    # print('BoxedImages populated')
    # AzureBoxedImages.populate()
    # print('AzureBoxedImages populated!')
    FormRecognizer.populate()
    print('Form Recognizer populated!')




def full_image_shower(document_id, page_number, scale_factor=2.0):
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





def export_pdf(document_id, image_number):
    pass

    # Fetch the required data from FormRecognizer and FormRecognizerBoxedImageBlobs
    # data = (FormRecognizer & {'document_id': document_id, 'image_number': image_number}).fetch1()
    # boxed_image_blobs = (FormRecognizer.FormRecognizerBoxedImageBlobs & {'document_id': document_id, 'image_number': image_number}).fetch('form_recognizer_text', 'ocr_prob')

    # # Prepare the output data
    # exported_data = {
    #     'document_id': document_id,
    #     'image_number': image_number,
    #     'average_ocr_prob': data['average_form_recognizer_text_confidence'],
    #     'full_text': [{'text': str(boxed_image_blobs[0][num]), 'probability': float(boxed_image_blobs[1][num])} for num in range(len(boxed_image_blobs[0]))]
    # }

    # Export the data to a JSON file
    # filename = f"document_Form_recognizer_{document_id}_image_{image_number}.json"
    # with open(filename, 'w') as f:
    #     json.dump(exported_data, f, indent=4)











if __name__ == '__main__':
    print('This is main!')