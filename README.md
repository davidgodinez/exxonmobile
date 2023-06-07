
# Exxonmobile

## Our OCR engine

1. We are using the Azure Form Recognizer to perform handwriting recognition. 

## Getting your environment set up

1. Ensure that you have a local sql server. This could be mysql, MariaDB, or any similar variant.
 (I am currently using a mysql database and got set up using this [link](https://dev.mysql.com/downloads/mysql/).)
 Be sure to set up database credentials setting a username and password.
2. Ensure that you have poetry installed. If you do not, refer to the following [link](https://python-poetry.org/docs/#installing-with-the-official-installer:~:text=its%20own%20environment.-,Install,-Poetry). In your terminal, run `poetry shell` and `poetry install` to create your environment. This will allow you to run your files.

## Preparing the pipeline

1. Ensure that your `exxonmobile/dj_local_conf.json` file has been updated to reflect your database credentials. This will make it easier everytime as it will essentially autofill your credentials for you whenever you restart your kernel. If this file does not exist, be sure to create one and format it in the following way:

```
{
    "database.host": "localhost",
    "database.user": "<username>",
    "database.password": "<password>"
}
```

2. You can modify the `schema` but ensure that this is consistent across all files the require the schema.

## Azure Credentials

1. You'll need a `credentials.json` file to get the Form Recognizer api working. The file should be in the same directory you run your gui. 

You should have the following in the file:

```
{
    "API_key": "<api_key>",
    "endpoint": "https:/<resource-name>.cognitiveservices.azure.com/"
}
```

## The GUI

1. The GUI will be your main tool in this repo. It will allow you to perform text-detection and boxing and store each all your processed documents in your database with the click of a button.
2. You can explore the files more granuarly with this GUI and even submit comments on what you believe the correct text should be for a word.
3. You are also able to export the the text generated from each page of your PDF as a json file.
4. To run the gui ensure your poetry shell has been spun up and necessary dependencies install. Ensure that you're in the `exxonmobile` directory then from the terminal run poetry run python pipeline/gui.py

## The Notebooks

1. `database.ipynb` gives you a starting point to explore the tables in your database. 
2. Demo 5-24 contains the confusion matrix used in our presentation to exxon on 5-24. 
2. Running a notebook requires you to run the following command in your temrinal: `poetry run python jupyter notebook`. This will open a window in your browser showing all the files in your repo. Navigate to the desired notebook and run.  
