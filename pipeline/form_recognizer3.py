import json
import pandas as pd
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential



def form_recognizer():
    with open('/Users/David.Godinez/Downloads/7b12da4f-7664-433c-9a34-4306c35f1aab_removed.json', 'r') as f:
        data = json.load(f)
        
    result = pd.json_normalize(data)

    # getting the initial paragraph dataframe
    df_paragraph = pd.DataFrame(result['analyzeResult.paragraphs'][0])
    # create paragraph dataframe
    paragraph_spans = []

    for index, row in df_paragraph.iterrows():
        for span in row['spans']:
            span['content'] = row['content']
            span['boundingRegions'] = row['boundingRegions']
            paragraph_spans.append(span)

    df_paragraph_spans = pd.DataFrame(paragraph_spans)

    # getting initial styles dataframe
    styles = result['analyzeResult.styles']
    df_styles = pd.DataFrame(styles[0])

    # create styles dataframe 
    style_spans = []

    for index, row in df_styles.iterrows():
        for span in row['spans']:
            span['confidence'] = row['confidence']
            span['isHandwritten'] = row['isHandwritten']
            span['fontStyle'] = row['fontStyle']
            span['fontWeight'] = row['fontWeight']
            span['similarFontFamily'] = row['similarFontFamily']
            span['color'] = row['color']
            span['backgroundColor'] = row['backgroundColor']
            style_spans.append(span)

    df_style_spans = pd.DataFrame(style_spans)

    df_merged = pd.merge(df_paragraph_spans, df_style_spans, on=['offset', 'length'], how='inner')
    # Normalize the boundingRegions column and reset the index
    df_bounding_regions_normalized = pd.json_normalize(df_merged['boundingRegions'].explode()).reset_index(drop=True)

    # Merge the original DataFrame with the normalized boundingRegions DataFrame
    df_merged2 = pd.concat([df_merged.drop(columns=['boundingRegions']), df_bounding_regions_normalized], axis=1)
    df_merged2[df_merged['isHandwritten'] == True]




