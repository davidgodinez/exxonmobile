import os
import io
import json
import time
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes, VisualFeatureTypes
import requests 
from PIL import Image, ImageDraw, ImageFont


credential = json.load(open('credentials.json'))
API_KEY = credential['API_KEY']
END_POINT = credential['END_POINT']

cv_client = ComputerVisionClient(END_POINT, CognitiveServicesCredentials(API_KEY))

image_location= "/Users/David.Godinez/Desktop/BJSS/exxon2/exxonmobile/files/Figure_1.png"

response = cv_client.read_in_stream(open(image_location, 'rb'), Language="en", raw=True)
operationLocation = response.headers['Operation-Location']
operation_id = operationLocation.split('/')[-1]

time.sleep(5)

result = cv_client.get_read_result(operation_id)
print(result)


if result.status == OperationStatusCodes.succeeded:
	read_results = result.analyze_result.read_results
	for analyzed_result in read_results:
		for line in analyzed_result.lines:
			print('Line: ')			
			print(line.text)
			for words in line.words:
				print('Words: ')
				print(words.text)
			break

image = Image.open(image_location)
if result.status == OperationStatusCodes.succeeded:
	read_results = result.analyze_result.read_results
	for analyzed_result in read_results:
		for line in analyzed_result.lines:
			x1, y1, x2, y2, x3, y3, x4, y4 = line.bounding_box
			draw = ImageDraw.Draw(image)
			draw.line(
				((x1,y1), (x2,y1), (x2,y2), (x3,y2), (x3,y3), (x4,y3), (x4,y4), (x1,y4), (x1,y1)),
				fill=(255, 0, 0),
				width=(5)
				)
image.show()
image.convert('RGB').save('results.jpg')
