import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from dataloader import dataloader, full_image_shower, box_shower, full_image_with_boxes_shower, boxed_paragraph_shower, export_to_json, Azure_box_shower, Azure_boxed_paragraph_shower, Azure_export_to_json, form_recognizer_full_image_shower
from table_classes import BoxedImages, AzureBoxedImages
from dataloader_azure import azure_image_processing, azure_full_image_with_boxes_shower
from dataloader_aws import aws_textract_processing
from tkinter import messagebox
from datetime import datetime


def search_word():
    search_term = search_entry.get()
    if not search_term:
        messagebox.showwarning("Warning", "Please enter a search term.")
        return

    search_terms = search_term.lower().split()

    filter_value = filter_option.get()
    
    if filter_value == "Handwritten":
        filter_condition = "handwritten=1"
    elif filter_value == "Not Handwritten":
        filter_condition = "handwritten=0"
    else:
        filter_condition = None

    try:
        if filter_condition:
            boxed_image_results = (AzureBoxedImages.AzureBoxedImageBlobs & f'{filter_condition}').fetch("ocr_text")
            # boxed_paragraph_results = AzureBoxedImages.AzureBoxedParagraphBlobs.fetch("ocr_text", filter_condition)
        else:
            boxed_image_results = AzureBoxedImages.AzureBoxedImageBlobs.fetch("ocr_text")
            # boxed_paragraph_results = AzureBoxedImages.AzureBoxedParagraphBlobs.fetch("ocr_text")
        
        matches = set()

        for idx, ocr_text in enumerate(boxed_image_results):
            ocr_text_lower = ocr_text.lower()
            if all(term in ocr_text_lower for term in search_terms):
                document_ids, image_numbers, box_numbers = AzureBoxedImages.AzureBoxedImageBlobs.fetch("document_id", "image_number", "box_number")
                document_id = document_ids[idx]
                image_number = image_numbers[idx]
                box_number = box_numbers[idx]
                matches.add((document_id, image_number, box_number, "Box"))

        # for idx, ocr_text in enumerate(boxed_paragraph_results):
        #     ocr_text_lower = ocr_text.lower()
        #     if all(term in ocr_text_lower for term in search_terms):
        #         document_ids, image_numbers, paragraph_numbers = BoxedImages.BoxedParagraphBlobs.fetch("document_id", "image_number", "paragraph_number")
        #         document_id = document_ids[idx]
        #         image_number = image_numbers[idx]
        #         paragraph_number = paragraph_numbers[idx]
        #         matches.add((document_id, image_number, paragraph_number, "Paragraph"))

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
        azure_full_image_with_boxes_shower(document_id, image_number)
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

        selected_option = display_option.get()
        if selected_option == "No Model":
            pass
        elif selected_option == "Azure Form Recognizer":
            # Call the corresponding function for Azure Form Recognizer
            Azure_box_shower(document_id, image_number, box_number)
        elif selected_option == "AWS Textract":
            # Call the corresponding function for AWS Textract
            pass

    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id, image_number, or box_number")

def boxed_paragraph_shower_btn():
    try:
        document_id = int(document_id_entry.get())
        image_number = int(image_number_entry.get())
        paragraph_number = int(paragraph_number_entry.get())

        selected_option = display_option.get()
        if selected_option == "No Model":
            pass
        elif selected_option == "Azure Form Recognizer":
            # Call the corresponding function for Azure Form Recognizer
            Azure_boxed_paragraph_shower(document_id, image_number, paragraph_number)
        elif selected_option == "AWS Textract":
            # Call the corresponding function for AWS Textract
            pass

    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id, image_number, or paragraph_number")


def submit_comment_btn():
    try:
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

            selected_option = display_option.get()

            # Insert the comment into the appropriate table
            if item_type == 'box':
                if selected_option in ["No Model", "Show Full Image with Boxes (CRAFT-Pytorch)"]:
                    BoxedImages.BoxedImageComments.insert1(key)
                elif selected_option in ["Azure Form Recognizer"]:
                    AzureBoxedImages.AzureBoxedImageComments.insert1(key)
            elif item_type == 'paragraph':
                if selected_option in ["Show Full Image (No Model)", "Show Full Image with Boxes (CRAFT-Pytorch)"]:
                    BoxedImages.BoxedParagraphComments.insert1(key)
                elif selected_option in ["Azure Form Recognizer"]:
                    AzureBoxedImages.AzureBoxedParagraphComments.insert1(key)

            messagebox.showinfo("Info", f"Comment submitted: {comment}")

        else:
            messagebox.showerror("Error", "Please enter a comment")
    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id, image_number, or item_number")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")



def export_to_json_btn():
    try:
        document_id = int(document_id_entry.get())
        image_number = int(image_number_entry.get())

        selected_option = display_option.get()
        if selected_option == "Show Full Image (No Model)":
            pass
        elif selected_option == "Azure Form Recognizer":
            # Call the corresponding function for Azure Form Recognizer
            Azure_export_to_json(document_id, image_number)
        elif selected_option == "AWS Textract":
            # Call the corresponding function for AWS Textract
            pass
        
        messagebox.showinfo("Info", "Export to JSON successful")
    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id or image_number")


# Create the execute button
def execute_display_option():
    try:
        document_id = int(document_id_entry.get())
        image_number = int(image_number_entry.get())

        selected_option = display_option.get()
        if selected_option == "No Model":
            full_image_shower_btn()
        elif selected_option == "Azure Form Recognizer":
            form_recognizer_full_image_shower(document_id, image_number)
        elif selected_option == "AWS Textract":
            full_aws_textract_processing_btn()

    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id or image_number")




root = tk.Tk()
root.title("Form Recognizer Image Viewer")

# Create widgets

dataloader_button = tk.Button(root, text="Load Data", command=dataloader_btn)

document_id_label = tk.Label(root, text="Document ID:")
document_id_entry = tk.Entry(root)

image_number_label = tk.Label(root, text="Image Number:")
image_number_entry = tk.Entry(root)

# Create a StringVar for the dropdown box
display_option = tk.StringVar(root)
display_option.set("No Model")  # Set default value

# Create the dropdown box (OptionMenu)
display_option_label = tk.Label(root, text="Select Model:")
display_option_menu = tk.OptionMenu(
    root,
    display_option,
    "No Model",
    # "Show Full Image with Boxes (CRAFT-Pytorch)",
    "Azure Form Recognizer",
    "AWS Textract",
)


execute_button = tk.Button(root, text="Show", command=execute_display_option)



export_to_json_button = tk.Button(root, text="Export to JSON", command=export_to_json_btn)


box_number_label = tk.Label(root, text="Box Number:")
box_number_entry = tk.Entry(root)
box_shower_button = tk.Button(root, text="Show Boxed Image", command=box_shower_btn)

paragraph_number_label = tk.Label(root, text="Paragraph Number:")
paragraph_number_entry = tk.Entry(root)
boxed_paragraph_shower_button = tk.Button(root, text="Show Boxed Paragraph", command=boxed_paragraph_shower_btn)

comment_label = tk.Label(root, text="Label:")
comment_entry = tk.Entry(root, width=50)

item_type_var = tk.StringVar(root)
item_type_var.set('box')  # Set default value
item_type_label = tk.Label(root, text="Label Type:")
item_type_optionmenu = tk.OptionMenu(root, item_type_var, 'box', 'paragraph')

item_number_label = tk.Label(root, text="Item Number:")
item_number_entry = tk.Entry(root)

submit_comment_button = tk.Button(root, text="Submit Label", command=submit_comment_btn)

# Create search widgets
search_label = tk.Label(root, text="Search for word(s):")
search_entry = tk.Entry(root)
search_button = tk.Button(root, text="Search", command=search_word)



result_text = tk.StringVar()
# Place widgets on the window
dataloader_button.pack(pady=10)

display_option_label.pack()
display_option_menu.pack()

document_id_label.pack()
document_id_entry.pack()

image_number_label.pack()
image_number_entry.pack()

execute_button.pack(pady=10)
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

filter_option = tk.StringVar(root)
filter_option.set("All")  # Set default value
# Step 2: Create the filter dropdown box (OptionMenu)
filter_option_label = tk.Label(root, text="Filter:")
filter_option_menu = tk.OptionMenu(
    root,
    filter_option,
    "All",
    "Handwritten",
    "Not Handwritten",
)

# Place the filter dropdown box (OptionMenu) on the window
filter_option_label.pack()
filter_option_menu.pack()


scrollable_frame = create_scrollable_frame(root)

root.mainloop()

