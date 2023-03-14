
# Exxonmobile

## Getting your environment set up 

1. Ensure that you have sql server. This could be mysql, MariaDB, or any similar variant.
 (I am currently using a mysql database and got set up using this [link](https://dev.mysql.com/downloads/mysql/).)
 Be sure to set up database credentials setting a username and password.
2. Ensure that you have poetry installed. If you do not, refer to the following [link](https://python-poetry.org/docs/#installing-with-the-official-installer:~:text=its%20own%20environment.-,Install,-Poetry)

## Preparing the pipeline

1. Ensure that your `dj_local_conf.json` file has been updated to reflect your database credentials. This will make it easier everytime as it will essentially autofill your credentials for you whenever you restart your kernel.
2. You can modify the `schema` but ensure that this is consistent across all files the require the schema.

## Preparing/running the notebook

1. Ensure that the third cell containing the line `folder_path = '</folder/path/to/files>'` has been updated to reflect the path where your files are stored. 
2. Run the command `poetry run jupyter notebook`