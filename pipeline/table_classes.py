import datajoint as dj
import fitz
import io
from io import BytesIO
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
from easyocr import Reader


schema = dj.Schema("exxonmobile")
folder_path = '../files'


@schema # 
class Documents(dj.Manual):
    definition = """
    document_id: int    # unique id for document
    ---
    datetime: varchar(50)   # time document was imported into table 
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

        for idx, region in enumerate(paragraph_regions):
            ptl_y, pbr_y = region

            # Find the x coordinates for the region
            x_min, x_max = find_x_coordinates(results, region)

            # Debugging: Print the top-left and bottom-right coordinates
            print("Top-left:", x_min, ptl_y, "Bottom-right:", x_max, pbr_y)

            ptl = (int(x_min) - padding, int(ptl_y) - padding)
            pbr = (int(x_max) + padding, int(pbr_y) + padding)

            boxed_paragraph = image[ptl[1]:pbr[1], ptl[0]:pbr[0]]



        # Convert the boxed_paragraph NumPy array back to a PIL image
            boxed_paragraph_pil = Image.fromarray(cv2.cvtColor(boxed_paragraph, cv2.COLOR_BGR2RGB))

            # Save the PIL image as a PNG in memory
            boxed_paragraph_buffer = BytesIO()
            boxed_paragraph_pil.save(boxed_paragraph_buffer, format='PNG')

            # Store the PNG image in the BoxedImages.BoxedParagraphBlobs table
            BoxedImages.BoxedParagraphBlobs.insert1(dict(key, paragraph_number=idx + 1,
                                                        boxed_paragraph=boxed_paragraph_buffer.getvalue()))


