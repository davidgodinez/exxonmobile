
# Exxonmobile

## Getting your environment set up 

### If you have an M1 Macbook, you can follow steps 1-3 seamlessly.
1. Ensure that you have miniconda or anaconda installed on your machine. If you do not you can visit the following [link](https://docs.conda.io/en/latest/miniconda.html).
2. Ensure that you have sql server. This could be mysql, MariaDB, or any similar variant.
 (I am currently using a mysql database and got set up using this [link](https://dev.mysql.com/downloads/mysql/).) 
 Be sure to set up database credentials setting a username and password. 
3. Once you have conda installed and a database set up, you can open up your IDE to your project's directory, open terminal, or whatever bash/sh/zsh you prefer and run the following: `conda env create -f environment.yml`. This will create a conda environment with all the required dependencies that will allow you to run your pipeline as a script and serve as your notebook kernel.

# If You can also use toml file to build your environment.

Use the command `poetry run jupyter notebook` to bring up the notebook.


## Preparing the pipeline

1. Ensure that your `dj_local_conf.json` file has been updated to reflect your database credentials. This will make it easier everytime as it will essentially autofill your credentials for you whenever you restart your kernel.
2. You can modify the `schema` but ensure that this is consistent across all files the require the schema.


## Preparing the notebook 


1. Ensure that the third cell containing the line `folder_path = '</folder/path/to/files>'` has been updated to reflect the path where your files are stored. 




