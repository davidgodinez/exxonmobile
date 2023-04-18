import PyPDF4

def extract_metadata(pdf_file):
    with open(pdf_file, 'rb') as file:
        pdf_reader = PyPDF4.PdfFileReader(file)
        metadata = pdf_reader.getDocumentInfo()
        
        # Convert metadata to a dictionary
        metadata_dict = {key[1:]: value for key, value in metadata.items()}
        
        return metadata_dict


pdf_file = '/Users/David.Godinez/Desktop/BJSS/exxon2/exxonmobile/files/7b12da4f-7664-433c-9a34-4306c35f1aab_removed.pdf'
# pdf_file = 'path/to/your/pdf_file.pdf'
metadata = extract_metadata(pdf_file)
print(metadata)
