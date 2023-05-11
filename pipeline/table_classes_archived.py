import datajoint as dj
import fitz
import io
from io import BytesIO
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
from easyocr import Reader
import json
import os
import time
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes, VisualFeatureTypes
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import requests
from PIL import Image, ImageDraw, ImageFont
import base64
from form_recognizer4 import process_analyzed_result



schema = dj.Schema("exxonmobile")
folder_path = '../files'


@schema
class Documents(dj.Manual):
    definition = """
    document_id: int    # unique id for document
    ---
    datetime: varchar(50)   # time document was imported into table 
    folder_path: varchar(1000) # folder path of the document
    file_name: varchar(1000)  # document filename
    """


@schema 
class ConvertedDocuments(dj.Imported):
    definition = """
    -> Documents     # using Documents' primary key as foreign key 
    """
    class Images(dj.Part):
        definition = """
        -> ConvertedDocuments
        image_number: int
        ---
        image: longblob
        """

    def make(self, key):
        self.insert1(key)
        for document_idx, document in enumerate(Documents.fetch('file_name')):
            print(document_idx, '=', document)
            doc = fitz.open(Path(folder_path, (Documents.fetch('file_name')[document_idx])))
            for page_number in range(len(doc)):
                page = doc.load_page(page_number)

                # Increase the zoom value to get a higher resolution image
                zoom = 3
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)

                # Save pixmap as a PNG image in memory
                buffer = io.BytesIO()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img.save(buffer, format='PNG')

                # Check if the combination of document_id and image_number already exists in the table
                existing_entry = (ConvertedDocuments.Images & dict(key, image_number=page_number + 1)).fetch()
                if not existing_entry:
                    # Store the PNG image as a longblob in the table
                    ConvertedDocuments.Images.insert1(dict(key, image_number=page_number + 1, image=buffer.getvalue()))




@schema
class BoxedImages(dj.Imported):
    definition = """
    -> ConvertedDocuments.Images   # using ConvertedDocuments.Images primary key as foreign key
    ---
    full_boxed_image: longblob # full boxed image
    full_text: varchar(10000) # full text
    """
    
    class BoxedImageBlobs(dj.Part):
        definition = """
        -> BoxedImages
        box_number: int
        ---
        boxed_image: longblob
        ocr_text: varchar(1000)
        ocr_prob: float
        """
    

    class BoxedParagraphBlobs(dj.Part):
        definition = """
        -> BoxedImages
        paragraph_number: int
        ---
        boxed_paragraph: longblob
        ocr_text: varchar(10000)
        ocr_prob: float
        """


    class BoxedImageComments(dj.Part):
        definition = """
        -> BoxedImages.BoxedImageBlobs
        comment_timestamp: datetime   # unique timestamp for each comment
        ---
        comment: varchar(1000)
        """
    
    class BoxedParagraphComments(dj.Part):
        definition = """
        -> BoxedImages.BoxedParagraphBlobs
        comment_timestamp: datetime   # unique timestamp for each comment
        ---
        comment: varchar(1000)
        """


    def make(self, key):
        image_blob = (ConvertedDocuments.Images & key).fetch1('image')
        image = cv2.imdecode(np.frombuffer(image_blob, np.uint8), cv2.IMREAD_COLOR)
        
        # Resize the image
        new_width = int(image.shape[1] * 1.5)
        new_height = int(image.shape[0] * 1.5)
        image = cv2.resize(image, (new_width, new_height))

        # OCR the input image using EasyOCR
        langs = ["en"]
        reader = Reader(langs, gpu=False)
        results = reader.readtext(image)

        padding = 2  # Adjust this value to change the padding around the text

        # Loop over the results and draw bounding boxes
        for (bbox, text, prob) in results:
            (tl, tr, br, bl) = bbox
            tl = (int(tl[0]) - padding, int(tl[1]) - padding)
            tr = (int(tr[0]) + padding, int(tr[1]) - padding)
            br = (int(br[0]) + padding, int(br[1]) + padding)
            bl = (int(bl[0]) - padding, int(bl[1]) + padding)

            cv2.rectangle(image, tl, br, (0, 255, 0), 2)
            cv2.putText(image, text, (tl[0], tl[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Save the full boxed image as a PNG in memory
        full_boxed_buffer = BytesIO()
        full_boxed_image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        full_boxed_image_pil.save(full_boxed_buffer, format='PNG')

        # saving the full text as a string 
        final_string = ''
        for text in range(len(results)):
            # concatenate the text 
            final_string += results[text][1] + ' '

        # Insert the key and the full boxed image into the BoxedImages table
        self.insert1(dict(key, full_boxed_image=full_boxed_buffer.getvalue(), full_text=final_string))

        # Loop over the results and store each boxed image with the box, text, and probability
        for idx, (bbox, text, prob) in enumerate(results):
            (tl, tr, br, bl) = bbox
            tl = (int(tl[0]) - padding, int(tl[1]) - padding)
            tr = (int(tr[0]) + padding, int(tr[1]) - padding)
            br = (int(br[0]) + padding, int(br[1]) + padding)
            bl = (int(bl[0]) - padding, int(bl[1]) + padding)

            boxed_image = image[tl[1]:br[1], tl[0]:br[0]]

            # Convert the boxed_image NumPy array back to a PIL image
            boxed_image_pil = Image.fromarray(cv2.cvtColor(boxed_image, cv2.COLOR_BGR2RGB))

            # Save the PIL image as a PNG in memory
            boxed_image_buffer = BytesIO()
            boxed_image_pil.save(boxed_image_buffer, format='PNG')

            # Store the PNG image in the BoxedImages.BoxedImageBlobs table
            BoxedImages.BoxedImageBlobs.insert1(dict(key, box_number=idx + 1,
                                                    boxed_image=boxed_image_buffer.getvalue(),
                                                    ocr_text=text,
                                                    ocr_prob=prob))
            
        # Find paragraph regions using the 'results' variable from the EasyOCR step
        def find_paragraph_regions(results, line_threshold=50):
            lines = []
            for bbox, _, _ in results:
                (tl, tr, br, bl) = bbox
                top = min(tl[1], tr[1])
                bottom = max(br[1], bl[1])
                lines.append((top, bottom))

            lines.sort(key=lambda x: x[0])

            merged_lines = []
            current_line = lines[0]
            for i in range(1, len(lines)):
                if lines[i][0] - current_line[1] < line_threshold:
                    current_line = (current_line[0], lines[i][1])
                else:
                    merged_lines.append(current_line)
                    current_line = lines[i]
            merged_lines.append(current_line)

            paragraph_regions = [(tl, br) for tl, br in merged_lines]
            return paragraph_regions
        
        def find_x_coordinates(results, region):
            x_min = float("inf")
            x_max = 0

            for bbox, _, _ in results:
                (tl, tr, br, bl) = bbox
                top = min(tl[1], tr[1])
                bottom = max(br[1], bl[1])

                if top >= region[0] and bottom <= region[1]:
                    x_min = min(x_min, tl[0], bl[0])
                    x_max = max(x_max, tr[0], br[0])

            return x_min, x_max



        paragraph_regions = find_paragraph_regions(results)

        # Debugging: Print the paragraph regions
        print("Paragraph regions:", paragraph_regions)
        # Inside the make function
        for idx, region in enumerate(paragraph_regions):
            ptl_y, pbr_y = region

            # Find the x coordinates for the region
            x_min, x_max = find_x_coordinates(results, region)

            ptl = (int(x_min) - padding, int(ptl_y) - padding)
            pbr = (int(x_max) + padding, int(pbr_y) + padding)

            boxed_paragraph = image[ptl[1]:pbr[1], ptl[0]:pbr[0]]

            # Extract the ocr_text and ocr_prob for the paragraph
            paragraph_text = []
            paragraph_prob = []
            for bbox, text, prob in results:
                (tl, tr, br, bl) = bbox
                top = min(tl[1], tr[1])
                bottom = max(br[1], bl[1])

                if top >= ptl_y and bottom <= pbr_y:
                    paragraph_text.append(text)
                    paragraph_prob.append(prob)

            # Combine the paragraph text and calculate the average probability
            combined_text = ' '.join(paragraph_text)
            avg_prob = sum(paragraph_prob) / len(paragraph_prob) if paragraph_prob else 0

            # Convert the boxed_paragraph NumPy array back to a PIL image
            boxed_paragraph_pil = Image.fromarray(cv2.cvtColor(boxed_paragraph, cv2.COLOR_BGR2RGB))

            # Save the PIL image as a PNG in memory
            boxed_paragraph_buffer = BytesIO()
            boxed_paragraph_pil.save(boxed_paragraph_buffer, format='PNG')

            # Store the PNG image, ocr_text, and ocr_prob in the BoxedImages.BoxedParagraphBlobs table
            BoxedImages.BoxedParagraphBlobs.insert1(dict(key, paragraph_number=idx + 1,
                                                        boxed_paragraph=boxed_paragraph_buffer.getvalue(),
                                                        ocr_text=combined_text,
                                                        ocr_prob=avg_prob))



@schema
class AzureBoxedImages(dj.Imported):
    definition = """
    -> ConvertedDocuments.Images   # using ConvertedDocuments.Images primary key as foreign key
    ---
    full_boxed_image: longblob  # full boxed image
    full_text: varchar(10000)    # full text
    """

    class AzureBoxedImageBlobs(dj.Part):
        definition = """
        -> AzureBoxedImages
        box_number: int
        ---
        boxed_image: longblob
        ocr_text: varchar(1000)
        ocr_prob: float
        handwritten: tinyint(1) DEFAULT 0
        """

    class AzureBoxedImageComments(dj.Part):
        definition = """
        -> AzureBoxedImages.AzureBoxedImageBlobs
        comment_timestamp: datetime   # unique timestamp for each comment
        ---
        comment: varchar(1000)
        """

    class AzureBoxedParagraphBlobs(dj.Part):
        definition = """
        -> AzureBoxedImages
        paragraph_number: int
        ---
        boxed_paragraph: longblob
        ocr_text: varchar(10000)
        ocr_prob: float
        """

    class AzureBoxedParagraphComments(dj.Part):
        definition = """
        -> AzureBoxedImages.AzureBoxedParagraphBlobs
        comment_timestamp: datetime   # unique timestamp for each comment
        ---
        comment: varchar(1000)
        """

    @staticmethod
    def azure_image_processing(document_id, image_number):
        def group_lines_into_paragraphs(lines, threshold=50):
            paragraphs = []
            current_paragraph = []

            for i, line in enumerate(lines):
                if i == 0:
                    current_paragraph.append(line)
                    continue

                prev_line = lines[i - 1]
                prev_line_y = (prev_line.bounding_box[1] + prev_line.bounding_box[5]) / 2
                current_line_y = (line.bounding_box[1] + line.bounding_box[5]) / 2

                if abs(current_line_y - prev_line_y) <= threshold:
                    current_paragraph.append(line)
                else:
                    paragraphs.append(current_paragraph)
                    current_paragraph = [line]

            if current_paragraph:
                paragraphs.append(current_paragraph)

            # Ensure that each paragraph contains a list of lines
            for i, paragraph in enumerate(paragraphs):
                if not isinstance(paragraph, list):
                    paragraphs[i] = [paragraph]

            return paragraphs

        print("Loading credentials...")
        credential = json.load(open('../credentials.json'))
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
            "texts": [],
            "paragraphs": [],
            "lines": []
        }

        if result.status == OperationStatusCodes.succeeded:
            read_results = result.analyze_result.read_results
            for analyzed_result in read_results:
                lines = analyzed_result.lines
                paragraphs = group_lines_into_paragraphs(lines)

                for line in lines:
                    x1, y1, x2, y2, x3, y3, x4, y4 = line.bounding_box
                    draw.rectangle(((x1, y1), (x3, y3)), outline='red', width=2)  # Draw the box around each word

                    boxed_image = image.crop((x1, y1, x3, y3))
                    boxed_image_buffer = io.BytesIO()
                    boxed_image.save(boxed_image_buffer, format='PNG')
                    boxed_image_encoded = base64.b64encode(boxed_image_buffer.getvalue())

                    metadata["texts"].append({
                        "text": line.text,
                        "probability": line.appearance.style.confidence,
                        "boxed_image": boxed_image_encoded.decode('utf-8')
                    })

                for paragraph in paragraphs:
                    x1, y1, x2, y2, x3, y3, x4, y4 = [min(line.bounding_box[0] for line in paragraph),
                                                    min(line.bounding_box[1] for line in paragraph),
                                                    max(line.bounding_box[2] for line in paragraph),
                                                    min(line.bounding_box[3] for line in paragraph),
                                                    max(line.bounding_box[4] for line in paragraph),
                                                    max(line.bounding_box[5] for line in paragraph),
                                                    min(line.bounding_box[6] for line in paragraph),
                                                    max(line.bounding_box[7] for line in paragraph)]
                    boxed_paragraph = image.crop((x1, y1, x3, y3))
                    boxed_paragraph_buffer = io.BytesIO()
                    boxed_paragraph.save(boxed_paragraph_buffer, format='PNG')
                    boxed_paragraph_encoded = base64.b64encode(boxed_paragraph_buffer.getvalue())

                    paragraph_text = ' '.join(line.text for line in paragraph)

                    metadata["paragraphs"].append({
                        "text": paragraph_text,
                        "probability": None,  # You can update this if you want to calculate the probability for the entire paragraph
                        "boxed_paragraph": boxed_paragraph_encoded.decode('utf-8'),
                        "lines": [{**line.as_dict(), "probability": line.appearance.style.confidence} for line in paragraph]
                    })

        print("Saving results...")
        full_boxed_image = image
        full_text = ' '.join([item['text'] for item in metadata['texts']])

        with open('metadata.json', 'w') as f:
            metadata['lines'] = [line.as_dict() for line in metadata['lines']]  # add this line to convert Line objects to dictionary
            json.dump(metadata, f, indent=2)
        print("Finished.")

        return full_boxed_image, full_text, metadata



    def make(self, key):
        # from form_recognizer import form_recognizer
        print(os.getcwd())
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
        # Load the image from the key
        image_blob = (ConvertedDocuments.Images & key).fetch1('image')
        image = Image.open(io.BytesIO(image_blob))

        # Call the Azure OCR function
        metadata = AzureBoxedImages.azure_image_processing(key['document_id'], key['image_number'])

        # Extract the full_text from the metadata
        full_text = ' '.join([text_info['text'] for text_info in metadata[2]['texts']])
        # Save the full_boxed_image
        full_boxed_image = metadata[0].convert('RGB')
        full_boxed_buffer = io.BytesIO()
        full_boxed_image.save(full_boxed_buffer, format='PNG')
        full_boxed_buffer = io.BytesIO()
        full_boxed_image.save(full_boxed_buffer, format='PNG')

        # Insert the key, full_boxed_image, and full_text into the AzureBoxedImages table
        self.insert1(dict(key, full_boxed_image=full_boxed_buffer.getvalue(), full_text=full_text))

        # Get the handwritten content from the form_recognizer function
        handwritten_content = form_recognizer(key['document_id'], key['image_number'])

        # Insert the boxed image blobs and their respective OCR text, probability, and a boolean for being handwritten
        for idx, text_info in enumerate(metadata[2]['texts']):
            is_handwritten = text_info['text'] in handwritten_content
            boxed_image_key = dict(key, box_number=idx, boxed_image=base64.b64decode(text_info['boxed_image'].encode('utf-8')),
                                ocr_text=text_info['text'], ocr_prob=text_info['probability'], handwritten=is_handwritten)
            self.AzureBoxedImageBlobs.insert1(boxed_image_key)

        # Insert the boxed paragraph blobs and their respective OCR text and probability
        for idx, paragraph_info in enumerate(metadata[2]['paragraphs']):
            boxed_paragraph_key = dict(key, paragraph_number=idx, boxed_paragraph=base64.b64decode(paragraph_info['boxed_paragraph'].encode('utf-8')),
                                    ocr_text=paragraph_info['text'], ocr_prob=0.0)
            self.AzureBoxedParagraphBlobs.insert1(boxed_paragraph_key)


@schema
class FormRecognizer(dj.Imported):
    definition = """
    -> ConvertedDocuments.Images   # using ConvertedDocuments.Images primary key as foreign key
    ---
    form_recognizer_image: longblob  # image blob from form recognizer
    average_form_recognizer_text_confidence: varchar(10000)  # text and confidence generated from form recognizer
    """


    class Metadata(dj.Part):
        definition = """
        -> FormRecognizer
        ---
        offset: int
        length: int
        content: varchar(10000)
        polygon: blob
        confidence: float
        is_handwritten: bool
        """


    class FormRecognizerBoxedImageBlobs(dj.Part):
        definition = """
        -> FormRecognizer
        box_number: int
        ---
        boxed_image: longblob
        form_recognizer_text: varchar(1000)
        ocr_prob: float
        """

    class FormRecognizerBoxedImageComments(dj.Part):
        definition = """
        -> FormRecognizer.FormRecognizerBoxedImageBlobs
        comment_timestamp: datetime   # unique timestamp for each comment
        ---
        comment: varchar(1000)
        """




    def resize_image(self, image, max_allowed_size):
        while True:
            # Save the image to a bytes buffer
            image_data = io.BytesIO()
            image.save(image_data, format="PNG")

            # Check if the image size is within the allowed limit
            if image_data.tell() <= max_allowed_size:
                break

            # Reduce the image size by 10%
            new_width = int(0.9 * image.width)
            new_height = int(0.9 * image.height)
            image = image.resize((new_width, new_height), Image.ANTIALIAS)

        return image, image_data.getvalue()
    

    def form_recognizer(self, image_blob):
        # Load the credentials from a JSON file and other necessary steps
        # Load the credentials from a JSON file
        credentials_path = os.path.abspath('credentials2.json')
        with open(credentials_path, 'r') as f:
            credentials = json.load(f)

        # Replace with your own values
        subscription_key = credentials['API_key']
        endpoint = credentials['endpoint']

        # document
        image = Image.open(io.BytesIO(image_blob))
        print("Original image dimensions: width = {}, height = {}".format(image.width, image.height))

        # Define the maximum allowed size (in bytes)
        max_allowed_size = 4 * 1024 * 1024  # 4 MB

        # Resize the image if it exceeds the maximum allowed size
        image, image_data = self.resize_image(image, max_allowed_size)
        print("Resized image dimensions: width = {}, height = {}".format(image.width, image.height))

        # create your `DocumentAnalysisClient` instance and `AzureKeyCredential` variable
        document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(subscription_key))

        poller = document_analysis_client.begin_analyze_document(
                "prebuilt-document", image_data)
        result = poller.result()

        # Extract the text and confidence from the result object
        handwritten_words = []
        for style in result.styles:
            if style.is_handwritten:
                print("Document contains handwritten content: ")
                for span in style.spans:
                    start_idx = span.offset
                    end_idx = start_idx + span.length

                    for page in result.pages:
                        for word in page.words:
                            word_idx = result.content.index(word.content)
                            if word_idx >= start_idx and word_idx < end_idx:
                                print(word.content)
                                handwritten_words.append({
                                    "text": word.content,
                                    "confidence": word.confidence,
                                    "polygon": [point for point in word.polygon]
                                })
        # PAY SPECIAL ATTENTION TO THE TWO LINES BELOW. This is our 'big filter'
        # Apply the min_word_length filtering
        min_word_length = 2  # Adjust this value based on your observations
        handwritten_words = [word for word in handwritten_words if len(word['text']) >= min_word_length]


        # Draw the bounding boxes around the handwritten words
        draw = ImageDraw.Draw(image)
        for word in handwritten_words:
            bounding_box = word['polygon']
            draw.polygon(bounding_box, outline="red")

        # Save the modified image to a bytes buffer
        boxed_image_data = io.BytesIO()
        image.save(boxed_image_data, format="PNG")
        boxed_image_data = boxed_image_data.getvalue()

        return boxed_image_data, handwritten_words




    def make(self, key):
        # Fetch the image blob from the ConvertedDocuments.Images table
        image_blob = (ConvertedDocuments.Images & key).fetch1('image')

        # Call your form_recognizer function on the image_blob and get the resulting image and text with confidence values
        form_recognizer_image, handwritten_words = self.form_recognizer(image_blob)

        # Calculate the average OCR probability
        average_ocr_prob = round(sum([word['confidence'] for word in handwritten_words]) / len(handwritten_words), 3) if handwritten_words else 0

        # Insert the key and the resulting image and text with confidence values into the FormRecognizer table
        self.insert1(dict(key, form_recognizer_image=form_recognizer_image, average_form_recognizer_text_confidence=average_ocr_prob))

        # Create the image object
        original_image = Image.open(io.BytesIO(image_blob))

        # Populate the FormRecognizerBoxedImageBlobs table
        for idx, word in enumerate(handwritten_words):
            # Draw the bounding box around the word
            draw = ImageDraw.Draw(original_image)
            bounding_box = word['polygon']
            draw.polygon(bounding_box, outline="red")

            # Compute the minimum and maximum coordinates for both x and y
            min_x = min(point.x for point in bounding_box)
            min_y = min(point.y for point in bounding_box)
            max_x = max(point.x for point in bounding_box)
            max_y = max(point.y for point in bounding_box)

            # Crop the boxed image using the proper coordinates
            cropped_box = original_image.crop((min_x, min_y, max_x, max_y))

            # Save the cropped box image to a bytes buffer
            cropped_box_data = io.BytesIO()
            cropped_box.save(cropped_box_data, format="PNG")
            cropped_box_data = cropped_box_data.getvalue()

            self.FormRecognizerBoxedImageBlobs.insert1({
                **key,
                'box_number': idx,
                'boxed_image': cropped_box_data,
                'form_recognizer_text': word['text'],
                'ocr_prob': word['confidence']
            })
    
    def make2(self, key):
        pass



