import os
# os.chdir('..')
import datajoint as dj
from PDFloader import PDFFileLoader
from table_classes import ConvertedDocuments


parent_directory = os.getcwd()
schema = dj.Schema("exxonmobile")
# use absolute path
folder_path = f'{parent_directory}/files'
loader = PDFFileLoader(folder_path=folder_path)
loader.load_files()
ConvertedDocuments.populate()
print('Populate complete!')