# import libraries
import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import json
from table_classes import AzureBoxedImages, ConvertedDocuments
from PIL import Image
import io

# Load the credentials from a JSON file
with open('credentials2.json', 'r') as f:
    credentials = json.load(f)

# Replace with your own values
subscription_key = credentials['API_key']
endpoint = credentials['endpoint']

def format_bounding_region(bounding_regions):
    if not bounding_regions:
        return "N/A"
    return ", ".join("Page #{}: {}".format(region.page_number, format_polygon(region.polygon)) for region in bounding_regions)

def format_polygon(polygon):
    if not polygon:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in polygon])


def form_recognizer_1(document_id, image_number):
    # Load the credentials from a JSON file
    with open('credentials2.json', 'r') as f:
        credentials = json.load(f)

    # Replace with your own values
    subscription_key = credentials['API_key']
    endpoint = credentials['endpoint']

    # sample document
    image_blob = (ConvertedDocuments.Images & f'document_id={document_id}' & f'image_number={image_number}').fetch1('image')
    image = Image.open(io.BytesIO(image_blob))
    print("Original image dimensions: width = {}, height = {}".format(image.width, image.height))


    # Check if image dimensions are within the supported range and resize if necessary
    max_dimension = 4200
    if image.width > max_dimension or image.height > max_dimension:
        aspect_ratio = float(image.width) / float(image.height)
        if image.width > image.height:
            new_width = max_dimension
            new_height = int(max_dimension / aspect_ratio)
        else:
            new_width = int(max_dimension * aspect_ratio)
            new_height = max_dimension

        image = image.resize((new_width, new_height), Image.ANTIALIAS)

    min_dimension = 500
    if image.width < min_dimension or image.height < min_dimension:
        aspect_ratio = float(image.width) / float(image.height)
        if image.width < image.height:
            new_width = min_dimension
            new_height = int(min_dimension / aspect_ratio)
        else:
            new_width = int(min_dimension * aspect_ratio)
            new_height = min_dimension

        image = image.resize((new_width, new_height), Image.ANTIALIAS)

    
    print("Resized image dimensions: width = {}, height = {}".format(image.width, image.height))
    image_data = io.BytesIO()
    image.save(image_data, format="PNG")
    image_data = image_data.getvalue()



    # create your `DocumentAnalysisClient` instance and `AzureKeyCredential` variable
    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(subscription_key))

    poller = document_analysis_client.begin_analyze_document(
            "prebuilt-document", image_data)
    result = poller.result()

    for style in result.styles:
        if style.is_handwritten:
            print("Document contains handwritten content: ")
            print(",".join([result.content[span.offset:span.offset + span.length] for span in style.spans]))
            return True
        else:
            print('There is no handwritten text')
            return False  
        

        

# ===============================

def form_recognizer2(document_id, image_number):
    # Load the credentials from a JSON file and other necessary steps
    with open('credentials2.json', 'r') as f:
        credentials = json.load(f)

    # Replace with your own values
    subscription_key = credentials['API_key']
    endpoint = credentials['endpoint']

    # sample document

    image_blob = (ConvertedDocuments.Images & f'document_id={document_id}' & f'image_number={image_number}').fetch1('image')
    image = Image.open(io.BytesIO(image_blob))
    print("Original image dimensions: width = {}, height = {}".format(image.width, image.height))


    # Check if image dimensions are within the supported range and resize if necessary
    max_dimension = 4200
    if image.width > max_dimension or image.height > max_dimension:
        aspect_ratio = float(image.width) / float(image.height)
        if image.width > image.height:
            new_width = max_dimension
            new_height = int(max_dimension / aspect_ratio)
        else:
            new_width = int(max_dimension * aspect_ratio)
            new_height = max_dimension

        image = image.resize((new_width, new_height), Image.ANTIALIAS)

    min_dimension = 500
    if image.width < min_dimension or image.height < min_dimension:
        aspect_ratio = float(image.width) / float(image.height)
        if image.width < image.height:
            new_width = min_dimension
            new_height = int(min_dimension / aspect_ratio)
        else:
            new_width = int(min_dimension * aspect_ratio)
            new_height = min_dimension

        image = image.resize((new_width, new_height), Image.ANTIALIAS)

    
    print("Resized image dimensions: width = {}, height = {}".format(image.width, image.height))
    image_data = io.BytesIO()
    image.save(image_data, format="PNG")
    image_data = image_data.getvalue()

    # create your `DocumentAnalysisClient` instance and `AzureKeyCredential` variable
    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(subscription_key))

    poller = document_analysis_client.begin_analyze_document(
            "prebuilt-document", image_data)
    result = poller.result()

    handwritten_content = []

    for style in result.styles:
        if style.is_handwritten:
            print("Document contains handwritten content: ")
            for span in style.spans:
                content = result.content[span.offset:span.offset + span.length]
                for page in result.pages:
                    for word in page.words:
                        if word.content == content:
                            bounding_box = format_polygon(word.polygon)
                            content_dict = {"content": content, "location": bounding_box}
                            handwritten_content.append(content_dict)
                            print(f"{content} at location {bounding_box}")
                            print(f'{handwritten_content}')

    if not handwritten_content:
        print('There is no handwritten text')

    return handwritten_content








# =================================

def form_recognizer3(document_id, image_number):
    # Load the credentials from a JSON file and other necessary steps
    # Load the credentials from a JSON file
    with open('credentials2.json', 'r') as f:
        credentials = json.load(f)

    # Replace with your own values
    subscription_key = credentials['API_key']
    endpoint = credentials['endpoint']

    # sample document
    image_blob = (ConvertedDocuments.Images & f'document_id={document_id}' & f'image_number={image_number}').fetch1('image')
    image = Image.open(io.BytesIO(image_blob))
    print("Original image dimensions: width = {}, height = {}".format(image.width, image.height))


    # Check if image dimensions are within the supported range and resize if necessary
    max_dimension = 4200
    if image.width > max_dimension or image.height > max_dimension:
        aspect_ratio = float(image.width) / float(image.height)
        if image.width > image.height:
            new_width = max_dimension
            new_height = int(max_dimension / aspect_ratio)
        else:
            new_width = int(max_dimension * aspect_ratio)
            new_height = max_dimension

        image = image.resize((new_width, new_height), Image.ANTIALIAS)

    min_dimension = 500
    if image.width < min_dimension or image.height < min_dimension:
        aspect_ratio = float(image.width) / float(image.height)
        if image.width < image.height:
            new_width = min_dimension
            new_height = int(min_dimension / aspect_ratio)
        else:
            new_width = int(min_dimension * aspect_ratio)
            new_height = min_dimension

        image = image.resize((new_width, new_height), Image.ANTIALIAS)

    
    print("Resized image dimensions: width = {}, height = {}".format(image.width, image.height))
    image_data = io.BytesIO()
    image.save(image_data, format="PNG")
    image_data = image_data.getvalue()

    # create your `DocumentAnalysisClient` instance and `AzureKeyCredential` variable
    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(subscription_key))

    poller = document_analysis_client.begin_analyze_document(
            "prebuilt-document", image_data)
    result = poller.result()

    handwritten_words = []
    bounding_boxes = []

    processed_word_ids = set()

    for style in result.styles:
        if style.is_handwritten:
            for span in style.spans:
                content = result.content[span.offset:span.offset + span.length]
                for page in result.pages:
                    for word in page.words:
                        if word.content in content and id(word) not in processed_word_ids:
                            bounding_box = format_polygon(word.polygon)
                            content_dict = {"content": word.content, "location": bounding_box}
                            handwritten_words.append(word.content)
                            bounding_boxes.append(bounding_box)
                            print(f"{word.content} at location {bounding_box}")
                            processed_word_ids.add(id(word))


    if not handwritten_words:
        print('There is no handwritten text')

    return list(zip(handwritten_words, bounding_boxes))




# ==================================================

def form_recognizer(document_id, image_number):
    # Load the credentials from a JSON file and other necessary steps
    # Load the credentials from a JSON file
    credentials_path = os.path.abspath('credentials2.json')
    with open(credentials_path, 'r') as f:
        credentials = json.load(f)

    # Replace with your own values
    subscription_key = credentials['API_key']
    endpoint = credentials['endpoint']

    # sample document
    image_blob = (ConvertedDocuments.Images & f'document_id={document_id}' & f'image_number={image_number}').fetch1('image')
    image = Image.open(io.BytesIO(image_blob))
    print("Original image dimensions: width = {}, height = {}".format(image.width, image.height))

    # Check if image dimensions are within the supported range and resize if necessary
    max_dimension = 4200
    if image.width > max_dimension or image.height > max_dimension:
        aspect_ratio = float(image.width) / float(image.height)
        if image.width > image.height:
            new_width = max_dimension
            new_height = int(max_dimension / aspect_ratio)
        else:
            new_width = int(max_dimension * aspect_ratio)
            new_height = max_dimension

        image = image.resize((new_width, new_height), Image.ANTIALIAS)

    min_dimension = 500
    if image.width < min_dimension or image.height < min_dimension:
        aspect_ratio = float(image.width) / float(image.height)
        if image.width < image.height:
            new_width = min_dimension
            new_height = int(min_dimension / aspect_ratio)
        else:
            new_width = int(min_dimension * aspect_ratio)
            new_height = min_dimension

        image = image.resize((new_width, new_height), Image.ANTIALIAS)

    print("Resized image dimensions: width = {}, height = {}".format(image.width, image.height))
    image_data = io.BytesIO()
    image.save(image_data, format="PNG")
    image_data = image_data.getvalue()

    handwritten_content = []

    # create your `DocumentAnalysisClient` instance and `AzureKeyCredential` variable
    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(subscription_key))

    poller = document_analysis_client.begin_analyze_document(
            "prebuilt-document", image_data)
    result = poller.result()

    for style in result.styles:
        if style.is_handwritten:
            print("Document contains handwritten content: ")
            handwritten_content = [result.content[span.offset:span.offset + span.length] for span in style.spans]
            print(",".join(handwritten_content))
            return handwritten_content
        else:
            print('There is no handwritten text')
            return []

    return handwritten_content



# ==================================== Additional features for now =======================================================================
def is_within_threshold(box1, box2, threshold):
    for point1, point2 in zip(box1, box2):
        if abs(point1[0] - point2[0]) > threshold or abs(point1[1] - point2[1]) > threshold:
            return False
    return True


# Assuming you have the OCR and handwritten data in the following format
# ocr_data = [{"text": "word", "bounding_box": [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]}, ...]
# handwritten_data = [{"text": "word", "bounding_box": [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]}, ...]

threshold = 10  # Set an appropriate threshold based on your use case
ocr_data = []
handwritten_data = []
for ocr_word in ocr_data:
    is_handwritten = False
    for handwritten_word in handwritten_data:
        if ocr_word['text'] == handwritten_word['text'] and is_within_threshold(ocr_word['bounding_box'], handwritten_word['bounding_box'], threshold):
            is_handwritten = True
            break
    # Update the handwritten field in the database for the specific instance based on the value of is_handwritten

# =========================================================================================================================================

if __name__ == "__main__":
    result = form_recognizer(document_id=0, image_number=4)
    print(result)


