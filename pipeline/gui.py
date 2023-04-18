import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from dataloader import dataloader, full_image_shower, box_shower, full_image_with_boxes_shower, boxed_paragraph_shower, export_to_json
from table_classes import BoxedImages
from dataloader_azure import azure_image_processing


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
azure_processing_button = tk.Button(root, text="Show Full Image with Boxes (Azure)", command=full_azure_image_processing_btn)

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

# Place widgets on the window
dataloader_button.pack(pady=10)

document_id_label.pack()
document_id_entry.pack()

image_number_label.pack()
image_number_entry.pack()

full_image_shower_button.pack(pady=10)
full_image_with_boxes_shower_button.pack(pady=10)
azure_processing_button.pack(pady=10)
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

root.mainloop()

