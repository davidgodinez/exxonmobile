
# Exxonmobile

## Our OCR engine

1. We are using the easy_ocr library which is a wrapper for CRAFT-pytorch (Character Recognition Awareness For Text-Detection). To read more about this library click [here](https://www.jaided.ai/easyocr/documentation/).
2. Learn about [CRAFT-pytorch](https://github.com/clovaai/CRAFT-pytorch).
3. [Github repo for More OCR Reading](https://github.com/JaidedAI/EasyOCR).

## Getting your environment set up

1. Ensure that you have sql server. This could be mysql, MariaDB, or any similar variant.
 (I am currently using a mysql database and got set up using this [link](https://dev.mysql.com/downloads/mysql/).)
 Be sure to set up database credentials setting a username and password.
2. Ensure that you have poetry installed. If you do not, refer to the following [link](https://python-poetry.org/docs/#installing-with-the-official-installer:~:text=its%20own%20environment.-,Install,-Poetry). In your terminal, run `poetry shell` and `poetry install` to create your environment. This will allow you to run your files.

## Preparing the pipeline

1. Ensure that your `dj_local_conf.json` file has been updated to reflect your database credentials. This will make it easier everytime as it will essentially autofill your credentials for you whenever you restart your kernel.
2. You can modify the `schema` but ensure that this is consistent across all files the require the schema.

## The GUI

1. The GUI will be your main tool in this repo. It will allow you to convert your pdf files to PNG's, perform text-detection and boxing and store each image in your database with the click of a button. 
2. You can explore the files more granuarly with this GUI and even submit comments on what you believe the correct text should be for a word. 
3. You are also able to export the the text generated from each page of your PDF as a json file. 

## The Notebook

1. This notebook can be run after interacting with the notebook and can be used to examin the contents of the database, namely the comments inserted from the GUI.
2. Running the notebook requires you to run the following command in your temrinal: `poetry run python jupyter notebook`. This will open a window in your browser showing all the files in your repo. Navigate to the desired notebook and run.  
