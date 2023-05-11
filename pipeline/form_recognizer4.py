import json
import re 
import os
import pandas as pd
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient, AnalyzeResult

def analyze_document(file_path):
    # Load the credentials from a JSON file and other necessary steps
    credentials_path = os.path.abspath('credentials2.json')
    with open(credentials_path, 'r') as f:
        credentials = json.load(f)

    subscription_key = credentials['API_key']
    endpoint = credentials['endpoint']

    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(subscription_key))

    with open(file_path, "rb") as f:
        file_content = f.read()

    poller = document_analysis_client.begin_analyze_document("prebuilt-read", file_content)
    result = poller.result()
    
    return result



def create_paragraph_dataframe(analyze_result):
    data = []
    
    for paragraph in analyze_result.paragraphs:
        content = paragraph.content
        bounding_region = paragraph.bounding_regions[0]  # Assuming there's always at least one bounding region
        page_number = bounding_region.page_number
        polygon = [(point.x, point.y) for point in bounding_region.polygon]
        span = paragraph.spans[0]  # Assuming there's always at least one span
        
        data.append({
            "offset": span.offset,
            "length": span.length,
            "content": content,
            "page_number": page_number,
            "polygon": polygon
        })
        
    df_paragraph_spans = pd.DataFrame(data)

    return df_paragraph_spans



def create_style_dataframe(analyze_result):
    data = []

    for style in analyze_result.styles:
        is_handwritten = style.is_handwritten
        confidence = style.confidence
        
        for span in style.spans:
            data.append({
                "confidence": confidence,
                "is_handwritten": is_handwritten,
                "offset": span.offset,
                "length": span.length
            })

    df_style_spans = pd.DataFrame(data)

    return df_style_spans



def merge_dataframes(df_paragraph_spans, df_style_spans):
    df_merged = pd.merge(df_paragraph_spans, df_style_spans, on=['offset', 'length'], how='outer')
    # Replace NaN with default values if necessary
    df_merged['confidence'].fillna(0, inplace=True)
    df_merged['is_handwritten'].fillna(False, inplace=True)
    return df_merged.reindex()


def process_analyzed_result(file_path: str):
    result = analyze_document(file_path)
    df_paragraph_spans = create_paragraph_dataframe(result)
    df_style_spans = create_style_dataframe(result)
    df_merged = merge_dataframes(df_paragraph_spans, df_style_spans)


    return df_merged[(df_merged['is_handwritten'] == True) 
                        & (df_merged['length']>1)
                        & (df_merged['content'].notnull()) 
                        & (df_merged['confidence'] > 0.5)].reset_index()
