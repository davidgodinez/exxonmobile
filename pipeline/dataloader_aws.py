import os
import io
import json
import time
import boto3
from PIL import Image, ImageDraw, ImageFont
from table_classes import ConvertedDocuments, BoxedImages


def aws_textract_processing(document_id, image_number):
    print("Loading credentials...")
    credential = json.load(open('credentials.json'))
    aws_secret_access_key = credential['aws_secret_access_key']
    aws_access_key_id = credential['aws_access_key_id']

    print("Initializing Textract Client...")
    client = boto3.client('textract', region_name='us-east-1', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    print("Fetching image from database...")
    image_blob = (ConvertedDocuments.Images & f'document_id={document_id}' & f'image_number={image_number}').fetch1('image')
    image = Image.open(io.BytesIO(image_blob))

    print("Sending image for processing...")
    response = client.detect_document_text(Document={'Bytes': image_blob})

    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default()  # Use the built-in font

    metadata = {
        "document_id": document_id,
        "image_number": image_number,
        "texts": []
    }

    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            print(f"{item['Text']} (Confidence: {item['Confidence']:.2f})")
            box = item['Geometry']['BoundingBox']
            left = image.width * box['Left']
            top = image.height * box['Top']
            width = image.width * box['Width']
            height = image.height * box['Height']
            draw.rectangle([left, top, left + width, top + height], outline='Blue', width=2)
            draw.text((left, top - 20), f"{item['Text']} ({item['Confidence']:.2f}%)", font=font, fill='Blue')
            metadata["texts"].append({
                "text": item['Text'],
                "confidence": item['Confidence']
            })

    print("Saving and displaying results...")
    image.convert('RGB').save('results_textract.jpg')
    image.show()

    with open('metadata_textract.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    print("Finished.")

