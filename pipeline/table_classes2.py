import sqlite3
import io
import os
from PIL import Image
import numpy as np
import cv2
from easyocr import Reader
from pathlib import Path
import fitz

folder_path = '../files'
db_file = 'exxonmobile.db'

# Create a connection to the SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Define the table creation queries
create_documents_table = """
CREATE TABLE IF NOT EXISTS Documents (
    document_id INTEGER PRIMARY KEY,
    datetime TEXT,
    file_name TEXT
);
"""

create_converted_documents_table = """
CREATE TABLE IF NOT EXISTS ConvertedDocuments (
    document_id INTEGER PRIMARY KEY,
    FOREIGN KEY (document_id) REFERENCES Documents (document_id)
);
"""

create_images_table = """
CREATE TABLE IF NOT EXISTS Images (
    document_id INTEGER,
    image_number INTEGER,
    image BLOB,
    PRIMARY KEY (document_id, image_number),
    FOREIGN KEY (document_id) REFERENCES ConvertedDocuments (document_id)
);
"""

create_boxed_images_table = """
CREATE TABLE IF NOT EXISTS BoxedImages (
    document_id INTEGER,
    image_number INTEGER,
    full_boxed_image BLOB,
    PRIMARY KEY (document_id, image_number),
    FOREIGN KEY (document_id, image_number) REFERENCES Images (document_id, image_number)
);
"""

create_boxed_image_blobs_table = """
CREATE TABLE IF NOT EXISTS BoxedImageBlobs (
    document_id INTEGER,
    image_number INTEGER,
    box_number INTEGER,
    boxed_image BLOB,
    ocr_text TEXT,
    ocr_prob REAL,
    PRIMARY KEY (document_id, image_number, box_number),
    FOREIGN KEY (document_id, image_number) REFERENCES BoxedImages (document_id, image_number)
);
"""

create_boxed_paragraph_blobs_table = """
CREATE TABLE IF NOT EXISTS BoxedParagraphBlobs (
    document_id INTEGER,
    image_number INTEGER,
    paragraph_number INTEGER,
    boxed_paragraph BLOB,
    PRIMARY KEY (document_id, image_number, paragraph_number),
    FOREIGN KEY (document_id, image_number) REFERENCES BoxedImages (document_id, image_number)
);
"""

create_boxed_image_comments_table = """
CREATE TABLE IF NOT EXISTS BoxedImageComments (
    document_id INTEGER,
    image_number INTEGER,
    box_number INTEGER,
    comment_timestamp TEXT,
    comment TEXT,
    PRIMARY KEY (document_id, image_number, box_number, comment_timestamp),
    FOREIGN KEY (document_id, image_number, box_number) REFERENCES BoxedImageBlobs (document_id, image_number, box_number)
);
"""

create_boxed_paragraph_comments_table = """
CREATE TABLE IF NOT EXISTS BoxedParagraphComments (
    document_id INTEGER,
    image_number INTEGER,
    paragraph_number INTEGER,
    comment_timestamp TEXT,
    comment TEXT,
    PRIMARY KEY (document_id, image_number, paragraph_number, comment_timestamp),
    FOREIGN KEY (document_id, image_number, paragraph_number) REFERENCES BoxedParagraphBlobs (document_id, image_number, paragraph_number)
);
"""

# Create the tables
cursor.execute(create_documents_table)
cursor.execute(create_converted_documents_table)
cursor.execute(create_images_table)
cursor.execute(create_boxed_images_table)
cursor.execute(create_boxed_image_blobs_table)
cursor.execute(create_boxed_paragraph_blobs_table)
cursor.execute(create_boxed_image_comments_table)
cursor.execute(create_boxed_paragraph_comments_table)

# Commit the changes and close the connection
conn.commit()
conn.close()
print('done!')


# Path: pipeline/table_classes2.py

def list_tables(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    conn.close()
    return tables

def print_table_schema(db_file, table_name):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({table_name});")
    schema = cursor.fetchall()

    print(f"Schema for table {table_name}:")
    for column in schema:
        print(column)

    conn.close()

# Example usage:

db_file = 'exxonmobile.db'
tables = list_tables(db_file)
print("Tables in the database:")
for table in tables:
    print(table[0])

print()

for table in tables:
    print_table_schema(db_file, table[0])
    print()


def print_table_data(db_file, table_name):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name};")
    data = cursor.fetchall()

    print(f"Data in table {table_name}:")
    for row in data:
        print(row)

    conn.close()

# Example usage:
db_file = 'exxonmobile.db'
tables = list_tables(db_file)

for table in tables:
    print_table_data(db_file, table[0])
    print()
