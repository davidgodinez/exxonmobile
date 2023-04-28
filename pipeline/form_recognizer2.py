# import libraries
import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import json
from table_classes import AzureBoxedImages, ConvertedDocuments
from PIL import Image
import io

# set `<your-endpoint>` and `<your-key>` variables with the values from the Azure portal
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


def analyze_general_documents(document_id, image_number, box_number):
    # sample document
    image_blob = (ConvertedDocuments.Images & f'document_id={document_id}' & f'image_number={image_number}').fetch1('image')  
    image = Image.open(io.BytesIO(image_blob))
    print("Original image dimensions: width = {}, height = {}".format(image.width, image.height))

    image_data = io.BytesIO()
    image.save(image_data, format="PNG")
    image_data = image_data.getvalue()

    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(subscription_key))

    poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-document", image_data)
    result = poller.result()

    for style in result.styles:
        if style.is_handwritten:
            print("Document contains handwritten content: ")
            print(",".join([result.content[span.offset:span.offset + span.length] for span in style.spans]))

    print("----Key-value pairs found in document----")
    for kv_pair in result.key_value_pairs:
        if kv_pair.key:
            print(
                    "Key '{}' found within '{}' bounding regions".format(
                        kv_pair.key.content,
                        format_bounding_region(kv_pair.key.bounding_regions),
                    )
                )
        if kv_pair.value:
            print(
                    "Value '{}' found within '{}' bounding regions\n".format(
                        kv_pair.value.content,
                        format_bounding_region(kv_pair.value.bounding_regions),
                    )
                )

    for page in result.pages:
        print("----Analyzing document from page #{}----".format(page.page_number))
        print(
            "Page has width: {} and height: {}, measured with unit: {}".format(
                page.width, page.height, page.unit
            )
        )

        for line_idx, line in enumerate(page.lines):
            print(
                "...Line # {} has text content '{}' within bounding box '{}'".format(
                    line_idx,
                    line.content,
                    format_polygon(line.polygon),
                )
            )

        for word in page.words:
            print(
                "...Word '{}' has a confidence of {}".format(
                    word.content, word.confidence
                )
            )

        for selection_mark in page.selection_marks:
            print(
                "...Selection mark is '{}' within bounding box '{}' and has a confidence of {}".format(
                    selection_mark.state,
                    format_polygon(selection_mark.polygon),
                    selection_mark.confidence,
                )
            )

    for table_idx, table in enumerate(result.tables):
        print(
            "Table # {} has {} rows and {} columns".format(
                table_idx, table.row_count, table.column_count
            )
        )
        for region in table.bounding_regions:
            print(
                "Table # {} location on page: {} is {}".format(
                    table_idx,
                    region.page_number,
                    format_polygon(region.polygon),
                )
            )
        for cell in table.cells:
            print(
                "...Cell[{}][{}] has content '{}'".format(
                    cell.row_index,
                    cell.column_index,
                    cell.content,
                )
            )
            for region in cell.bounding_regions:
                print(
                    "...content on page {} is within bounding box '{}'\n".format(
                        region.page_number,
                        format_polygon(region.polygon),
                    )
                )
    print("----------------------------------------")


# ===================================================================================================
from PIL import ImageDraw

def analyze_general_documents2(document_id, image_number, box_number):
    # sample document
    image_blob = (ConvertedDocuments.Images & f'document_id={document_id}' & f'image_number={image_number}').fetch1('image')  
    image = Image.open(io.BytesIO(image_blob))
    print("Original image dimensions: width = {}, height = {}".format(image.width, image.height))

    image_data = io.BytesIO()
    image.save(image_data, format="PNG")
    image_data = image_data.getvalue()

    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(subscription_key))

    poller = document_analysis_client.begin_analyze_document(
            "prebuilt-document", image_data)
    result = poller.result()

    draw = ImageDraw.Draw(image)

    # Collect all spans from the result.styles
    span_ranges = []
    for style in result.styles:
        if style.is_handwritten:
            for span in style.spans:
                span_ranges.append(range(span.offset, span.offset + span.length))

    # Check if a word is within any of the span_ranges
    def is_word_in_spans(word_idx):
        for span_range in span_ranges:
            if word_idx in span_range:
                return True
        return False

    def is_word_in_line(word, line):
        word_top_left = word.bounding_box[0]
        word_bottom_right = word.bounding_box[2]
        line_top_left = line.bounding_box[0]
        line_bottom_right = line.bounding_box[2]

        return (word_top_left.x >= line_top_left.x and word_top_left.y >= line_top_left.y
                and word_bottom_right.x <= line_bottom_right.x and word_bottom_right.y <= line_bottom_right.y)

    # Draw boxes around handwritten words in lines
    for page in result.pages:
        for line_idx, line in enumerate(page.lines):
            line_handwritten = False
            line_bounding_box = None

            for word in page.words:
                if is_word_in_line(word, line):
                    if is_word_in_spans(word):
                        line_handwritten = True
                        if line_bounding_box is None:
                            line_bounding_box = word.bounding_box
                        else:
                            # Extend line_bounding_box to include the word's bounding_box
                            line_bounding_box = [
                                line_bounding_box[0],
                                word.bounding_box[1],
                                word.bounding_box[2],
                                line_bounding_box[3],
                            ]

            if line_handwritten:
                print("Line contains handwritten content: '{}'".format(line.content))

                # Draw boxes around the identified handwritten text
                draw.polygon([
                    (line_bounding_box[0].x, line_bounding_box[0].y),
                    (line_bounding_box[1].x, line_bounding_box[1].y),
                    (line_bounding_box[2].x, line_bounding_box[2].y),
                    (line_bounding_box[3].x, line_bounding_box[3].y),
                ], outline="red")



    # Save the image with boxes around the handwritten text
    image.save("boxed_image.png")

    print("----Key-value pairs found in document----")
    for kv_pair in result.key_value_pairs:
        if kv_pair.key:
            print(
                    "Key '{}' found within '{}' bounding regions".format(
                        kv_pair.key.content,
                        format_bounding_region(kv_pair.key.bounding_regions),
                    )
                )
        if kv_pair.value:
            print(
                    "Value '{}' found within '{}' bounding regions\n".format(
                        kv_pair.value.content,
                        format_bounding_region(kv_pair.value.bounding_regions),
                    )
                )

    for page in result.pages:
        print("----Analyzing document from page #{}----".format(page.page_number))
        print(
            "Page has width: {} and height: {}, measured with unit: {}".format(
                page.width, page.height, page.unit
            )
        )

        for line_idx, line in enumerate(page.lines):
            print(
                "...Line # {} has text content '{}' within bounding box '{}'".format(
                    line_idx,
                    line.content,
                    format_polygon(line.polygon),
                )
            )

        for word in page.words:
            print(
                "...Word '{}' has a confidence of {}".format(
                    word.content, word.confidence
                )
            )

        for selection_mark in page.selection_marks:
            print(
                "...Selection mark is '{}' within bounding box '{}' and has a confidence of {}".format(
                    selection_mark.state,
                    format_polygon(selection_mark.polygon),
                    selection_mark.confidence,
                )
            )

    for table_idx, table in enumerate(result.tables):
        print(
            "Table # {} has {} rows and {} columns".format(
                table_idx, table.row_count, table.column_count
            )
        )
        for region in table.bounding_regions:
            print(
                "Table # {} location on page: {} is {}".format(
                    table_idx,
                    region.page_number,
                    format_polygon(region.polygon),
                )
            )
        for cell in table.cells:
            print(
                "...Cell[{}][{}] has content '{}'".format(
                    cell.row_index,
                    cell.column_index,
                    cell.content,
                )
            )
            for region in cell.bounding_regions:
                print(
                    "...content on page {} is within bounding box '{}'\n".format(
                        region.page_number,
                        format_polygon(region.polygon),
                    )
                )
    print("----------------------------------------")



from PIL import ImageDraw

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

    # Code for resizing the image if necessary

    image_data = io.BytesIO()
    image.save(image_data, format="PNG")
    image_data = image_data.getvalue()

    # create your `DocumentAnalysisClient` instance and `AzureKeyCredential` variable
    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(subscription_key))

    poller = document_analysis_client.begin_analyze_document(
            "prebuilt-document", image_data)
    result = poller.result()

    draw = ImageDraw.Draw(image)

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

                            bounding_box = [point for point in word.polygon]
                            draw.polygon(bounding_box, outline="red")



    image.save(f"boxed_image_{image_number}.png")
    print("Image with boxes around handwritten content saved as 'boxed_image.png'")

    return

if __name__ == "__main__":
    form_recognizer(0, 5)
