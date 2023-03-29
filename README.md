
# Exxonmobile

## Getting your environment set up 

1. Ensure that you have sql server. This could be mysql, MariaDB, or any similar variant.
 (I am currently using a mysql database and got set up using this [link](https://dev.mysql.com/downloads/mysql/).)
 Be sure to set up database credentials setting a username and password.
2. Ensure that you have poetry installed. If you do not, refer to the following [link](https://python-poetry.org/docs/#installing-with-the-official-installer:~:text=its%20own%20environment.-,Install,-Poetry)

## Preparing the pipeline

1. Ensure that your `dj_local_conf.json` file has been updated to reflect your database credentials. This will make it easier everytime as it will essentially autofill your credentials for you whenever you restart your kernel.
2. You can modify the `schema` but ensure that this is consistent across all files the require the schema.

## The GUI
1. The GUI will be your main tool in this repo. 
## The notebook

1. This notebook can be run after interacting with the notebook and can be used to examin the contents of the database, namely the comments inserted from the GUI. 