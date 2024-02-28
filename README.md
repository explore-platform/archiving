# Validate and publish records on ZENODO

These codes will validate, publish the files in zenodo and create record

## Description

There are 2 script.
1. To validate the files of the project
2. To upload to zenodo

### Executing program

* Launch the python code with the appropriate arguments
```
python validate_files.py -d directory -o files_to_omit
```
* The argument directory takes the directory path with the files to be validated.
* omit list is an option argument to provide as text file containing the list of files to be omitted
* for reference check the file in the repo

```
python archive_on_zenodo.py -d directory -j json -t token -o files_to_omit
```
* json argument takes the metadata json file. For eg check sample in the folder
* Please build the json according to your need as in the documentation https://developers.zenodo.org/#rest-api
* token is an argument which can be provided here or saved in the .env to be fetched automatically
* -t and -o are optional

## Authors

CHIRAG DEVAIAH

