import os
import io
import json
import time
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes, VisualFeatureTypes
import requests
from PIL import Image, ImageDraw, ImageFont
from table_classes import ConvertedDocuments, AzureBoxedImages
import matplotlib.pyplot as plt


def azure_image_processing(document_id, image_number):
    print("Loading credentials...")
    credential = json.load(open('credentials.json'))
    API_KEY = credential['API_KEY']
    END_POINT = credential['END_POINT']

    print("Initializing Computer Vision Client...")
    cv_client = ComputerVisionClient(END_POINT, CognitiveServicesCredentials(API_KEY))

    print("Fetching image from database...")
    image_blob = (ConvertedDocuments.Images & f'document_id={document_id}' & f'image_number={image_number}').fetch1('image')
    image = Image.open(io.BytesIO(image_blob))

    print("Sending image for processing...")
    response = cv_client.read_in_stream(io.BytesIO(image_blob), Language="en", raw=True)
    operationLocation = response.headers['Operation-Location']
    operation_id = operationLocation.split('/')[-1]

    print("Waiting for the results...")
    time.sleep(10)

    print("Fetching results...")
    result = cv_client.get_read_result(operation_id)

    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default()  # Use the built-in font

    metadata = {
        "document_id": document_id,
        "image_number": image_number,
        "texts": []
    }

    if result.status == OperationStatusCodes.succeeded:
        read_results = result.analyze_result.read_results
        for analyzed_result in read_results:
            for line in analyzed_result.lines:
                x1, y1, x2, y2, x3, y3, x4, y4 = line.bounding_box
                draw.line(
                    ((x1, y1), (x2, y1), (x2, y2), (x3, y2), (x3, y3), (x4, y3), (x4, y4), (x1, y4), (x1, y1)),
                    fill=(255, 0, 0),
                    width=2  # Reduced width for thinner boxes
                )
                # Draw text labels and confidence scores on top of the boxes
                for word in line.words:
                    text = f"{word.text} ({word.confidence * 100:.1f}%)"
                    draw.text((word.bounding_box[0], word.bounding_box[1] - 20), text, font=font, fill=(255, 0, 0))
                    metadata["texts"].append({
                        "text": word.text,
                        "probability": word.confidence * 100
                    })

    print("Saving and displaying results...")
    image.convert('RGB').save('results.jpg')
    image.show()

    with open('metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    print("Finished.")


def azure_full_image_with_boxes_shower(document_id, image_number, scale_factor=2.0):
    full_boxed_image = (AzureBoxedImages & {'document_id': document_id, 'image_number': image_number}).fetch1('full_boxed_image')
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
