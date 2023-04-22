import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from dataloader import dataloader, full_image_shower, box_shower, full_image_with_boxes_shower, boxed_paragraph_shower, export_to_json
from table_classes import BoxedImages
from dataloader_azure import azure_image_processing
from dataloader_aws import aws_textract_processing
from tkinter import messagebox
from datetime import datetime


def search_word():
    search_term = search_entry.get()
    if not search_term:
        messagebox.showwarning("Warning", "Please enter a search term.")
        return

    search_terms = search_term.lower().split()

    # Query the BoxedImages.BoxedImageBlobs and BoxedImages.BoxedParagraphBlobs tables for the search terms
    try:
        boxed_image_results = BoxedImages.BoxedImageBlobs.fetch("ocr_text")
        boxed_paragraph_results = BoxedImages.BoxedParagraphBlobs.fetch("ocr_text")
        matches = set()

        for idx, ocr_text in enumerate(boxed_image_results):
            ocr_text_lower = ocr_text.lower()
            if all(term in ocr_text_lower for term in search_terms):
                document_ids, image_numbers, box_numbers = BoxedImages.BoxedImageBlobs.fetch("document_id", "image_number", "box_number")
                document_id = document_ids[idx]
                image_number = image_numbers[idx]
                box_number = box_numbers[idx]
                matches.add((document_id, image_number, box_number, "Box"))

        for idx, ocr_text in enumerate(boxed_paragraph_results):
            ocr_text_lower = ocr_text.lower()
            if all(term in ocr_text_lower for term in search_terms):
                document_ids, image_numbers, paragraph_numbers = BoxedImages.BoxedParagraphBlobs.fetch("document_id", "image_number", "paragraph_number")
                document_id = document_ids[idx]
                image_number = image_numbers[idx]
                paragraph_number = paragraph_numbers[idx]
                matches.add((document_id, image_number, paragraph_number, "Paragraph"))

        if matches:
            result_string = "Matches found in:\n"
            for document_id, image_number, item_number, item_type in matches:
                result_string += f"Document ID: {document_id}, Image: {image_number}, {item_type}: {item_number}\n"
        else:
            result_string = "No matches found."

        result_text.set(result_string)

        for child in scrollable_frame.winfo_children():
            child.destroy()

        for result in result_string.split('\n'):
            result_label = tk.Label(scrollable_frame, text=result, wraplength=380, justify="center")
            result_label.pack(anchor="w")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while searching: {e}")


def create_scrollable_frame(parent):
    canvas = tk.Canvas(parent)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return scrollable_frame



def dataloader_btn():
    dataloader()
    messagebox.showinfo("Info", "Data loaded and tables populated")

def full_image_shower_btn():
    try:
        document_id = int(document_id_entry.get())
        image_number = int(image_number_entry.get())
        full_image_shower(document_id, image_number)
    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id or image_number")

def full_image_with_boxes_shower_btn():
    try:
        document_id = int(document_id_entry.get())
        image_number = int(image_number_entry.get())
        full_image_with_boxes_shower(document_id, image_number)
    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id or image_number")


def full_azure_image_processing_btn():
    try:
        document_id = int(document_id_entry.get())
        image_number = int(image_number_entry.get())
        azure_image_processing(document_id, image_number)
    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id or image_number")


def full_aws_textract_processing_btn():
    try:
        document_id = int(document_id_entry.get())
        image_number = int(image_number_entry.get())
        aws_textract_processing(document_id, image_number)
    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id or image_number")


def box_shower_btn():
    try:
        document_id = int(document_id_entry.get())
        image_number = int(image_number_entry.get())
        box_number = int(box_number_entry.get())
        box_shower(document_id, image_number, box_number)
    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id, image_number, or box_number")

def boxed_paragraph_shower_btn():
    try:
        document_id = int(document_id_entry.get())
        image_number = int(image_number_entry.get())
        paragraph_number = int(paragraph_number_entry.get())
        boxed_paragraph_shower(document_id, image_number, paragraph_number)
    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id, image_number, or paragraph_number")

def submit_comment_btn():
    comment = comment_entry.get()
    if comment:
        document_id = int(document_id_entry.get())
        image_number = int(image_number_entry.get())
        item_type = item_type_var.get()
        item_number = int(item_number_entry.get())

        key = {
            'document_id': document_id,
            'image_number': image_number,
            item_type + '_number': item_number,
            'comment_timestamp': datetime.now(),  # insert current timestamp
            'comment': comment,
        }

        # Insert the comment into the appropriate table
        if item_type == 'box':
            BoxedImages.BoxedImageComments.insert1(key)
        elif item_type == 'paragraph':
            BoxedImages.BoxedParagraphComments.insert1(key)

        messagebox.showinfo("Info", f"Comment submitted: {comment}")
    else:
        messagebox.showerror("Error", "Please enter a comment")


def export_to_json_btn():
    try:
        document_id = int(document_id_entry.get())
        image_number = int(image_number_entry.get())
        export_to_json(document_id, image_number)
        messagebox.showinfo("Info", "Export to JSON successful")
    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id or image_number")


root = tk.Tk()
root.title("PDF Image Viewer")

# Create widgets

dataloader_button = tk.Button(root, text="Load Data", command=dataloader_btn)

document_id_label = tk.Label(root, text="Document ID:")
document_id_entry = tk.Entry(root)

image_number_label = tk.Label(root, text="Image Number:")
image_number_entry = tk.Entry(root)

full_image_shower_button = tk.Button(root, text="Show Full Image", command=full_image_shower_btn)
full_image_with_boxes_shower_button = tk.Button(root, text="Show Full Image with Boxes (CRAFT-Pytorch)", command=full_image_with_boxes_shower_btn)
azure_processing_button = tk.Button(root, text="Show Full Image with Boxes (Azure Computer Vision)", command=full_azure_image_processing_btn)
aws_textract_processing_button = tk.Button(root, text="Show Full Image with Boxes (AWS Textract)", command=full_aws_textract_processing_btn)


export_to_json_button = tk.Button(root, text="Export to JSON", command=export_to_json_btn)


box_number_label = tk.Label(root, text="Box Number:")
box_number_entry = tk.Entry(root)
box_shower_button = tk.Button(root, text="Show Boxed Image", command=box_shower_btn)

paragraph_number_label = tk.Label(root, text="Paragraph Number:")
paragraph_number_entry = tk.Entry(root)
boxed_paragraph_shower_button = tk.Button(root, text="Show Boxed Paragraph", command=boxed_paragraph_shower_btn)

comment_label = tk.Label(root, text="Comment:")
comment_entry = tk.Entry(root, width=50)

item_type_var = tk.StringVar(root)
item_type_var.set('box')  # Set default value
item_type_label = tk.Label(root, text="Comment Type:")
item_type_optionmenu = tk.OptionMenu(root, item_type_var, 'box', 'paragraph')

item_number_label = tk.Label(root, text="Item Number:")
item_number_entry = tk.Entry(root)

submit_comment_button = tk.Button(root, text="Submit Comment", command=submit_comment_btn)

# Create search widgets
search_label = tk.Label(root, text="Search for word(s):")
search_entry = tk.Entry(root)
search_button = tk.Button(root, text="Search", command=search_word)

result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, wraplength=400)

# Place widgets on the window
dataloader_button.pack(pady=10)

document_id_label.pack()
document_id_entry.pack()

image_number_label.pack()
image_number_entry.pack()

full_image_shower_button.pack(pady=10)
full_image_with_boxes_shower_button.pack(pady=10)
azure_processing_button.pack(pady=10)
aws_textract_processing_button.pack(pady=10)
export_to_json_button.pack(pady=10)

box_number_label.pack()
box_number_entry.pack()

box_shower_button.pack(pady=10)

paragraph_number_label.pack()
paragraph_number_entry.pack()

boxed_paragraph_shower_button.pack(pady=10)

comment_label.pack()
comment_entry.pack()

item_type_label.pack()
item_type_optionmenu.pack()

item_number_label.pack()
item_number_entry.pack()

submit_comment_button.pack(pady=10)


# Place search widgets on the window
search_label.pack()
search_entry.pack()
search_button.pack(pady=10)
scrollable_frame = create_scrollable_frame(root)

root.mainloop()

