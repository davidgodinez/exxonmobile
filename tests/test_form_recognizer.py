import os
import pytest
from pipeline.form_recognizer import analyze_document, create_paragraph_dataframe, create_style_dataframe
from azure.ai.formrecognizer._models import AnalyzeResult
import pandas as pd 

# Path to the directory containing the file
dir_path = os.path.dirname(os.path.realpath(__file__))
# file name
file = '7b12da4f-7664-433c-9a34-4306c35f1aab_removed.pdf'

# Path to the file
file_path = os.path.join(dir_path, '..', 'files', file)

# Absolute path to the file
abs_file_path = os.path.abspath(file_path)

# result for analyzed document

result = analyze_document(abs_file_path)


def test_analyze_document():
    assert isinstance(result,AnalyzeResult)


def test_create_paragraph_dataframe():
    df = create_paragraph_dataframe(result)
    assert isinstance(df, pd.DataFrame )


def test_create_style_dataframe():
    df = create_style_dataframe(result)
    assert isinstance(df, pd.DataFrame)

