import boto3
from PIL import Image, ImageDraw
import pandas as pd
import json


credential = json.load(open('credentials.json'))
aws_secret_access_key = credential['aws_secret_access_key']
aws_access_key_id=credential['aws_access_key_id'] 

client = boto3.client('textract', region_name='us-east-1', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

with open("/Users/David.Godinez/Desktop/BJSS/exxon2/exxonmobile/files/Figure_1.png", "rb") as image:
    img = bytearray(image.read())

response = client.detect_document_text(Document={'Bytes': img})

def show_bounding_box(draw, box, width, height, box_color, text, confidence):
    left = width * box['Left']
    top = height * box['Top']
    draw.rectangle([left, top, left + (width * box['Width']), top + (height * box['Height'])], outline=box_color)
    draw.text((left, top), f"{text} ({confidence:.2f})", fill=box_color)

image = Image.open('/Users/David.Godinez/Desktop/BJSS/exxon2/exxonmobile/files/Figure_1.png')
width, height = image.size
draw = ImageDraw.Draw(image)

for item in response["Blocks"]:
    if item["BlockType"] == "LINE":
        print(f"{item['Text']} (Confidence: {item['Confidence']:.2f})")
        show_bounding_box(draw, item['Geometry']['BoundingBox'], width, height, 'Blue', item['Text'], item['Confidence'])

image.show()
image.save('result_with_boxes.png')
