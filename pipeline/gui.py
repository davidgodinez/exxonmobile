import tkinter as tk
from tkinter import messagebox
from dataloader import dataloader, full_image_shower, box_shower
from table_classes import BoxedImages

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

def box_shower_btn():
    try:
        document_id = int(document_id_entry.get())
        image_number = int(image_number_entry.get())
        box_number = int(box_number_entry.get())
        box_shower(document_id, image_number, box_number)
    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id, image_number, or box_number")

def submit_comment_btn():
    comment = comment_entry.get()
    if comment:
        document_id = int(document_id_entry.get())
        image_number = int(image_number_entry.get())
        box_number = int(box_number_entry.get())

        key = {
            'document_id': document_id,
            'image_number': image_number,
            'box_number': box_number,
            'comment': comment,
        }

        # Insert the comment into the BoxedImages.BoxedImageComments table
        BoxedImages.BoxedImageComments.insert1(key, skip_duplicates=True)

        messagebox.showinfo("Info", f"Comment submitted: {comment}")
        # Add any processing or saving functionality here
    else:
        messagebox.showerror("Error", "Please enter a comment")


root = tk.Tk()
root.title("BJSS PDF Image Viewer")

# Create widgets
dataloader_button = tk.Button(root, text="Load Data", command=dataloader_btn)

document_id_label = tk.Label(root, text="Document ID:")
document_id_entry = tk.Entry(root)

image_number_label = tk.Label(root, text="Image Number:")
image_number_entry = tk.Entry(root)

full_image_shower_button = tk.Button(root, text="Show Full Image", command=full_image_shower_btn)

box_number_label = tk.Label(root, text="Box Number:")
box_number_entry = tk.Entry(root)

box_shower_button = tk.Button(root, text="Show Boxed Image", command=box_shower_btn)

comment_label = tk.Label(root, text="Comment:")
comment_entry = tk.Entry(root, width=50)

submit_comment_button = tk.Button(root, text="Submit Comment", command=submit_comment_btn)


# Place widgets on the window
dataloader_button.pack(pady=10)

document_id_label.pack()
document_id_entry.pack()

image_number_label.pack()
image_number_entry.pack()

full_image_shower_button.pack(pady=10)

box_number_label.pack()
box_number_entry.pack()

box_shower_button.pack(pady=10)

comment_label.pack()
comment_entry.pack()

submit_comment_button.pack(pady=10)


root.mainloop()
