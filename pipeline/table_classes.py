# Working and Updated Form recognizer2 :) 
import datajoint as dj
import fitz
import io
from io import BytesIO
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
import json
import os
import time
import requests
from PIL import Image, ImageDraw, ImageFont
import base64
from form_recognizer import analyze_document, create_paragraph_dataframe, create_style_dataframe, merge_dataframes
import pandas as pd



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
class FormRecognizer(dj.Computed):
    definition = """
    -> Documents
    ---
    boxed_pdf_blob: longblob
    json_result_path: varchar(500)
    """

    class Metadata(dj.Part):
        definition = """
        -> FormRecognizer
        offset: int
        length: int
        ---
        content: varchar(10000)
        polygon: blob
        confidence: float
        page_number: int
        is_handwritten: bool
        """

        
    class PDFPages(dj.Part):
        definition = """
        -> FormRecognizer
        page_number: int
        ---
        page_image: longblob
        """
        
        
    class BoxedImageBlobs(dj.Part):
        definition = """
        -> FormRecognizer.PDFPages
        box_number: int
        ---
        boxed_image: longblob
        form_recognizer_text: varchar(1000)
        confidence: float
        """


    class BoxedImageComments(dj.Part):
        definition = """
        -> FormRecognizer.BoxedImageBlobs
        comment_timestamp: datetime   # unique timestamp for each comment
        ---
        comment: varchar(1000)
        """
    
    def make(self, key):
        # Get the file path of the document
        document = (Documents & key).fetch1()
        file_path = os.path.join(document['folder_path'], document['file_name'])

        # Process the document
        result = analyze_document(file_path)
        df_paragraph_spans = create_paragraph_dataframe(result)
        df_style_spans = create_style_dataframe(result)
        # filtering for words with a confidence equal to or greater than 90%
        df_style_spans = df_style_spans[(df_style_spans['confidence'] >= 0.9) & (df_style_spans['length'] > 1)]
        df_merged = merge_dataframes(df_paragraph_spans, df_style_spans)

        # Convert the AnalyzeResult object to a JSON string and write it to a file
        analyze_result = vars(result)
        def unknown_object_handler(obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            else:
                return str(obj)
        json_string = json.dumps(analyze_result, indent=4, default=unknown_object_handler)
        # improve hard coded path later 
        json_file_path = f"/Users/David.Godinez/Desktop/BJSS/exxon3/exxonmobile/json_files/document{key['document_id']}_result.json"
        with open(json_file_path, 'w') as f:
            f.write(json_string)

        # Open the document
        doc = fitz.open(file_path)

        # Iterate over each page in the document
        for page_number in range(len(doc)):
            # Get the page
            page = doc[page_number]

            # Select the rows for this page
            df_page = df_merged[df_merged['page_number'] == page_number + 1]

            # If there are no rows for this page, continue to the next page
            if df_page.empty:
                continue

            # Iterate over each row in your DataFrame
            for index, row in df_page.iterrows():
                # Fetch the coordinates for each box
                coordinates = row['polygon']
                # Scale the coordinates if they are not in the PDF's coordinate system
                scaled_coordinates = [(x * 72, y * 72) for x, y in coordinates]
                scaled_coordinates.append(scaled_coordinates[0])

                # Get the 'is_handwritten' value directly
                is_handwritten = row['is_handwritten']

                # Only add the box if the word is handwritten
                if is_handwritten:
                    # Add the polyline annotation
                    annot = page.add_polyline_annot(scaled_coordinates)
                    annot.set_border(width=0.6)

                    # Set the colors
                    annot.set_opacity(0.8)
                    annot.set_colors({'stroke':[1.0, 0.0, 0.0]})

        # Save the document to a PDF stream
        pdf_stream = BytesIO()
        doc.save(pdf_stream, garbage=4, deflate=True, clean=True)
        pdf_stream.seek(0)

        # Insert the main key to the master table
        self.insert1(dict(key, boxed_pdf_blob=pdf_stream.read(), json_result_path=json_file_path))


        # Iterate over rows in the DataFrame
        for _, row in df_merged.iterrows():
            # Check if the confidence value is NaN
            if pd.isnull(row['confidence']):
                row['confidence'] = -1  # replace NaN with -1

            # Check if content value is null  
            if pd.isnull(row['content']):
                row['content'] = "NULL"
            
            # if pd.isnull(row['page_number']):
            #     row['page_number'] = 2

            # Each row becomes a new entry in the Metadata table
            self.Metadata.insert1(dict(key,
                                       offset=row['offset'],
                                       length=row['length'],
                                       content=row['content'],
                                       page_number=row['page_number'],
                                       polygon=row['polygon'],
                                       confidence=row['confidence'],
                                       is_handwritten=row['is_handwritten']))

        # Iterate over each page in the document
        for page_number in range(len(doc)):
            # Get the page
            page = doc[page_number]

            # Convert the page to an image
            page_image = page.get_pixmap()
            img = Image.frombytes("RGB", [page_image.width, page_image.height], page_image.samples)

            png_io = BytesIO()
            img.save(png_io, format="PNG")
            png_io.seek(0)
            png_image = png_io.read()

            # Insert the page image into the PDFPages table
            self.PDFPages.insert1(dict(key, page_number=page_number+1, page_image=png_image))

        # Filter the dataframe based on the conditions
        df_filtered = df_merged[(df_merged['is_handwritten'] == True) 
                                & (df_merged['length']>1)
                                & (df_merged['content'].notnull()) 
                                & (df_merged['confidence'] > 0.5)].reset_index()

        
        # Iterate over each row in the filtered DataFrame
        for index, row in df_filtered.iterrows():
            # Get the page
            page = doc[row['page_number'] - 1]

            # Fetch the coordinates for each box
            coordinates = row['polygon']

            # Scale the coordinates if they are not in the PDF's coordinate system
            scaled_coordinates = [(x * 72, y * 72) for x, y in coordinates]
            scaled_coordinates.append(scaled_coordinates[0])

            # Convert the page to a pixmap and then to a PIL Image
            page_pixmap = page.get_pixmap()
            page_image = Image.frombytes("RGB", [page_pixmap.width, page_pixmap.height], page_pixmap.samples)

            # Compute the bounding box for the cropped area
            min_x = min(point[0] for point in scaled_coordinates)
            min_y = min(point[1] for point in scaled_coordinates)
            max_x = max(point[0] for point in scaled_coordinates)
            max_y = max(point[1] for point in scaled_coordinates)
            bbox = (min_x, min_y, max_x, max_y)

            # Crop the page image around the box
            cropped_image = page_image.crop(bbox)

            # Convert the cropped image to a PNG stream
            cropped_io = BytesIO()
            cropped_image.save(cropped_io, format="PNG")
            cropped_io.seek(0)
            cropped_png_image = cropped_io.read()

            # Insert the cropped image, content, and confidence into the BoxedImageBlobs table
            self.BoxedImageBlobs.insert1(dict(key, 
                                              page_number=row['page_number'],
                                              box_number=index,
                                              boxed_image=cropped_png_image, 
                                              form_recognizer_text=row['content'], 
                                              confidence=row['confidence']))

