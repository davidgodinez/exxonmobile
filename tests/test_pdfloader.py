from pipeline.PDFloader import PDFFileLoader
from pipeline.table_classes import Documents

folder_path = '/absolute/path/to/files'

# This test is currently designed to fail
def test_pdfloader(folder_path=folder_path):
    loader = PDFFileLoader(folder_path=folder_path)
    loader.load_files()
    assert len(Documents()) == 0 
