import os
import requests
from argparse import ArgumentParser
from sys import argv, exit
from dotenv import load_dotenv
import json
load_dotenv()

#Generic variable
zenodo_url = 'https://zenodo.org/api/deposit/depositions'


def parseoptions(argvalues):
    #Argument parser
    parser = ArgumentParser(description='Code to push file and metadata to zenodo')

    parser.add_argument('-d', '--dir',   dest='dir',   help="file_directory", required=True)
    parser.add_argument('-j', '--json',  dest='json',  help="metadata_json",  required=True)
    parser.add_argument('-t', '--token', dest='token', help="token zenodo")
    parser.add_argument('-o', '--omit',  dest='omit',  help="omit list")

    args = parser.parse_args(argvalues)

    if args.token is None:
        print("Token will be obtained from env variable")
        args.token = os.getenv('ZENODO_TOKEN')
    return args

def list_and_return_all_files(directory):
    """
    Check if the given path exists and return all the files inside the path

    Parameters:
    - directory: The directoy path to search.

    Returns:
    - A list containing the paths of all files found.
    """
    #Check if the given path exists and return all the files inside the path
    if os.path.isdir(directory) and os.path.exists(directory):
        file_list = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                #print(f"File: {file_path}")
                file_list.append(file_path)
        return file_list
    else:
        print("Given directory: ", directory, " does not exists")
        exit(0)

def read_extensions_from_file(filename):
    """
    Read list of file extensions from a file.

    Parameters:
    - filename: Name of the file containing list of file extensions.

    Returns:
    - A list of file extensions.
    """
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            extensions = [line.strip() for line in file]
        return extensions
    else:
        print("Given file: ", filename, " does not exists")
        exit(1)

def filter_files(files, extensions):
    """
    Filter out files with specific extensions.

    Parameters:
    - files: List of file paths.
    - extensions: List of file extensions to filter out.

    Returns:
    - A filtered list of file paths.
    """
    try:
        filtered_files = [file for file in files if not any(file.endswith(ext) for ext in extensions)]
        return filtered_files
    except Exception as e:
        print("Failed to perform filtering: ", str(e))
        exit(2)

def generate_deposition_id_bucket(zenodo_url, token):
    #Generate deposoition id and bucket to upload file
    """
    Generate deposition id and bucket to upload file.

    Parameters:
    - zenodo_url: Zenodo API url.
    - token: zenodo authentication token.

    Returns:
    - deposition_id, bucket_url
    """
    try:
        params = {'access_token': token}
        r = requests.post(zenodo_url, params=params, json={})
        if r.status_code == 201:
            deposition_id = r.json()["id"]
            bucket_url = r.json()["links"]["bucket"]
            return deposition_id, bucket_url
        else:
            print("Failed to get deposoition id and bucket_url")
            print(r.text)
    except Exception as e:
        print("Failed to get info: ", str(e))
        exit(3)

def upload_files(files, bucket_url, token):
    """
    Upload files to Zenodo deposition.

    Parameters:
    - files: List of file paths to upload.
    - bucket_url: URL of the Zenodo bucket.
    - token: zenodo authentication token.

    Returns:
    - None
    """
    try:
        params = {'access_token': token}
        for file in files:
            path = "%s" % file
            filename = os.path.basename(file)
            print('Trying to upload the file: {}' .format(filename))
            with open(path, 'rb') as fp:
                r = requests.put(
                    "%s/%s" % (bucket_url, filename),
                    data=fp,
                    params=params,
                )
            r.json()
            print(r.json())
    except:
        exit(4)

def add_metadata(zenodo_url, deposition_id, token, metadata_json):
    """
    Add metadata to the zenodo record.

    Parameters:
    - zenodo_url: Zenodo API url.
    - deposition_id: Zenodo record id.
    - token: zenodo authentication token.
    - metadata_json: The metadata to be added to the record

    Returns:
    - None
    """
    try:
        headers = {"Content-Type": "application/json"}
        full_url = '%s/%s' % (zenodo_url, deposition_id)
        r = requests.put(full_url,
                  params={'access_token': token}, data=json.dumps(metadata_json),
                  headers=headers)
    except Exception as e:
        print("Failed to add metadata info: ", str(e))
        exit(5)

def publish_record(zenodo_url, deposition_id, token):
    """
    To publish the zenodo record.

    Parameters:
    - zenodo_url: Zenodo API url.
    - deposition_id: Zenodo record id.
    - token: zenodo authentication token.

    Returns:
    - None
    """
    try:
        full_url = '%s/%s/actions/publish' % (zenodo_url, deposition_id)
        print(full_url)
        r = requests.post(full_url,
                  params={'access_token': token} )
    except Exception as e:
        print("Failed to publish record: ", str(e))
        exit(6)

def get_record(zenodo_url,  token):
    """
    To fetch all the depositions and print them.

    Parameters:
    - zenodo_url: Zenodo API url.
    - token: zenodo authentication token.

    Returns:
    - None
    """
    try:
        response = requests.get(zenodo_url,
                        params={'access_token': token})
        print('\nThe deposition records available are: {}\n' .format(response.json()))
    except Exception as e:
        print("Unable to fetch records: ", str(e))
        exit(7)


def main(argv=None):
    #Parse command line arguments
    args  = parseoptions(argv)
     
    #Get all files present in the directory
    all_files = list_and_return_all_files(args.dir)
    print('The files present in the folder are: {}\n' .format(all_files))
    
    #Check if there is an omit list with list of files to be omitted from uploading
    if (args.omit):
        extensions_filename = args.omit
        extensions = read_extensions_from_file(extensions_filename)
        # Filter files based on specific extensions
        filtered_files = filter_files(all_files, extensions)
    else:
        filtered_files = all_files

    print('The files to be uploaded are: {}\n' .format(filtered_files))

    #get deposition id and bucket_url
    deposition_id, bucket_url = generate_deposition_id_bucket(zenodo_url, args.token)
    print(deposition_id, bucket_url)
    
    #Upload all files
    upload_files(filtered_files, bucket_url, args.token)

    #Fetch the metadata file 
    with open(args.json, 'r') as f:
        json_data = json.load(f)

    # Add the metadata to the record
    add_metadata(zenodo_url, deposition_id, args.token, json_data)

    # Publish the record
    publish_record(zenodo_url, deposition_id, args.token)

    # Get the record details to check - optional
    #get_record(zenodo_url, args.token)


if __name__ == "__main__":
    main(argv[1:])

