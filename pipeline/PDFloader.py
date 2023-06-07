import os
import datajoint as dj
import datetime
from table_classes import Documents


class PDFFileLoader:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def load_files(self):
        """
        This function takes the files in the `files` directory and loads the file name and file path into the Documents table.
        """
        # Navigate to the folder containing the PDF files
        os.chdir(self.folder_path)

        # Iterate through each file in the folder
        for file_name in os.listdir(self.folder_path):
            # Check if the file is a PDF
            if file_name.endswith('.pdf') and (len((Documents & {'file_name':file_name}).fetch()) == 0):
                # Extract the necessary file information
                date_added = datetime.datetime.now()

                # Insert the file information into the database table
                data = {'document_id': len(Documents.fetch()), 
                        'datetime': date_added, 
                        'file_name': file_name,
                        'folder_path': self.folder_path}  # Add the folder path here
                Documents.insert1(data)

