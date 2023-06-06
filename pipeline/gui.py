import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from dataloader import dataloader, full_image_shower, Form_recognizer_box_shower
from table_classes import FormRecognizer
from tkinter import messagebox
from datetime import datetime



def search_word():
    search_term = search_entry.get()
    if not search_term:
        messagebox.showwarning("Warning", "Please enter a search term.")
        return

    search_terms = search_term.lower().split()

    try:
        matches = set()
        boxed_image_results = (FormRecognizer.BoxedImageBlobs).fetch("form_recognizer_text")

        # Fetch comment data from the FormRecognizer.BoxedImageComments table
        comment_data = FormRecognizer.BoxedImageComments.fetch("document_id", "page_number", "box_number", "comment")

        for idx, form_recognizer_text in enumerate(boxed_image_results):
            form_recognizer_text_lower = form_recognizer_text.lower()

            document_ids, page_numbers, box_numbers = FormRecognizer.BoxedImageBlobs.fetch("document_id", "page_number", "box_number")
            document_id = document_ids[idx]
            page_number = page_numbers[idx]
            box_number = box_numbers[idx]

            # Check if a comment exists for this document_id, image_number, and box_number
            comment = None
            fetched_comment_data = FormRecognizer.BoxedImageComments & f'document_id={document_id} and page_number={page_number} and box_number={box_number}'
            if fetched_comment_data:
                comment_document_id, comment_page_number, comment_box_number, comment_text, _ = fetched_comment_data.fetch1("document_id", "page_number", "box_number", "comment", "comment_timestamp")
                comment = comment_text

            # Use comment as the search text if it exists, otherwise use the OCR text
            search_text = comment.lower() if comment else form_recognizer_text_lower

            if all(term in search_text for term in search_terms):
                matches.add((document_id, page_number, box_number, "Box"))

        # The rest of the code for searching in the FormRecognizer.BoxedImageBlobs table

        if matches:
            result_string = "Matches found in:\n"
            for document_id, page_number, item_number, item_type in matches:
                result_string += f"Document ID: {document_id}, Page: {page_number}, {item_type}: {item_number}\n"
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
    messagebox.showinfo("Info", "Data analyzed and JSON file created!")


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
        Form_recognizer_box_shower(document_id, image_number, box_number)

    except Exception as e:
        print(f"An error occurred: {e}")



def submit_comment_btn():
    try:
        comment = comment_entry.get()
        if comment:
            document_id = int(document_id_entry.get())
            image_number = int(image_number_entry.get())
            item_number = int(item_number_entry.get())

            key = {
                'document_id': document_id,
                'page_number': image_number,
                'box_number' : item_number,
                'comment_timestamp': datetime.now(),  # insert current timestamp
                'comment': comment,
            }



            # Insert into FormRecognizer.FormRecognizerBoxedImageComments table
            FormRecognizer.BoxedImageComments.insert1(key)
            messagebox.showinfo("Info", f"Comment submitted: {comment}")

        else:
            messagebox.showerror("Error", "Please enter a comment")
    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id, image_number, or item_number")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")




def export_pdf_btn():
    try:
        document_id = int(document_id_entry.get())
        
        # Fetch the boxed_pdf_blob for this document_id
        query = (FormRecognizer & f'document_id={document_id}')
        boxed_pdf_blob = query.fetch1('boxed_pdf_blob')

        # Export the blob as a PDF file
        with open(f'document{document_id}.pdf', 'wb') as f:
            f.write(boxed_pdf_blob)

        messagebox.showinfo("Info", "Export pdf successful")
    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# Create the execute button
def execute_display_option():
    try:
        document_id = int(document_id_entry.get())
        image_number = int(image_number_entry.get())

        total_pages = full_image_shower(document_id, image_number)
        total_pages_label.config(text=f"Page {image_number} of {total_pages}")

    except ValueError:
        messagebox.showerror("Error", "Invalid input for document_id or image_number")





root = tk.Tk()
root.title("Form Recognizer Image Viewer")

# Create widgets

dataloader_button = tk.Button(root, text="Analyze Data", command=dataloader_btn)

document_id_label = tk.Label(root, text="Document ID:")
document_id_entry = tk.Entry(root)

image_number_label = tk.Label(root, text="Page Number:")
image_number_entry = tk.Entry(root)



execute_button = tk.Button(root, text="Show", command=execute_display_option)



box_number_label = tk.Label(root, text="Box Number:")
box_number_entry = tk.Entry(root)
box_shower_button = tk.Button(root, text="Show Boxed Region", command=box_shower_btn)


comment_label = tk.Label(root, text="Label:")
comment_entry = tk.Entry(root, width=30)


item_number_label = tk.Label(root, text="Item Number:")
item_number_entry = tk.Entry(root)

submit_comment_button = tk.Button(root, text="Submit Label", command=submit_comment_btn)

# Create search widgets
search_label = tk.Label(root, text="Search for word(s):")
search_entry = tk.Entry(root)
search_button = tk.Button(root, text="Search", command=search_word)

result_text = tk.StringVar()


# # Place widgets on the window
dataloader_button.pack(pady=10)

document_id_label.pack()
document_id_entry.pack()

image_number_label.pack()
image_number_entry.pack()

execute_button.pack(pady=10)
total_pages_label = tk.Label(root, text="")
total_pages_label.pack(pady=5)


box_number_label.pack()
box_number_entry.pack()

box_shower_button.pack(pady=10)


comment_label.pack()
comment_entry.pack()


item_number_label.pack()
item_number_entry.pack()

submit_comment_button = tk.Button(root, text="Submit Label", command=submit_comment_btn)
submit_comment_button.pack(pady=10)

# Create a new frame at the bottom of the window
bottom_frame = tk.Frame(root)
bottom_frame.pack(side='bottom', pady=10)

# Place search widgets on the window
search_label = tk.Label(root, text="Search for word(s):")
search_entry = tk.Entry(root)
search_button = tk.Button(root, text="Search", command=search_word)
search_label.pack()
search_entry.pack()
search_button.pack(pady=10)

# Add the 'Export to JSON' button to the bottom frame
export_to_json_button = tk.Button(bottom_frame, text="Export PDF", command=export_pdf_btn)
export_to_json_button.pack(pady=10)

scrollable_frame = create_scrollable_frame(root)

root.mainloop()

