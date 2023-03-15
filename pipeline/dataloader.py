import os
os.chdir('..')
import datajoint as dj
from pipeline.PDFloader import PDFFileLoader
from pdf2image import convert_from_path
from pipeline.table_classes import Documents, ConvertedDocuments

schema = dj.Schema("exxonmobile")
# use absolute path
folder_path = '/Users/David.Godinez/Desktop/BJSS/exxonmobile/files/'
loader = PDFFileLoader(folder_path=folder_path)
loader.load_files()
ConvertedDocuments.populate()