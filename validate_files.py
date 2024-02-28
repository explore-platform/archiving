import h5py
from argparse import ArgumentParser
from sys import argv, exit
import astropy.io.fits as fits
import os
import numpy as np
import csv


def parseoptions(argvalues):
    #Argument parser
    parser = ArgumentParser(description='Code to validate files of a project')

    parser.add_argument('-d', '--dir',   dest='dir',   help="file_directory", required=True)
    parser.add_argument('-o', '--omit',  dest='omit',  help="omit list")

    args = parser.parse_args(argvalues)

    return args

def list_and_return_all_files(directory):
    """
    Lists all files in the given directory and its subdirectories.

    Parameters:
    - directory: The directory path.

    Returns:
    - A list of file paths.
    """
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

def print_files_status(validated_list, failed_list):
    """
    To print the results.

    Parameters:
    - validated_list: List of files that have passed.
    - failed_list: List of files that have failed.

    Returns:
    - None
    """
    if len(validated_list) != 0:
        print('Validation successful: The files that have passed are')
        for entry in validated_list:
            print(entry)
        print('\n')
    if len(failed_list) != 0:
        print('Validation failed: The files that have failed are')
        for entry in failed_list:
            print(entry)
        print('\n')


def validate_hdf5(files):
    """
    Validates HDF5 files.

    Parameters:
    - files: List of files to be validated.

    Returns:
    - list of validated and not validate file
    """
    validated_files = []
    not_validated_files = []

    if len(files)> 0:
        for hdf5file in files:
            print(f'Processing the file: {hdf5file}')
            try:
                with h5py.File(hdf5file, 'r') as hf:
                    cube = hf['explore/cube_datas'][:]
                    dc = hf['explore/cube_datas']
                    headers = {k: v for k, v in dc.attrs.items()}
                    for key, value in headers.items():
                        print(f'{key}: {value}')
                    print(f"The hdf5 file at {hdf5file} conforms to hdf5 standards.")
                    print('\n')
                    validated_files.append(hdf5file)
            except Exception as e:
                print(f"The hdf5 file at {hdf5file} does not conforms to hdf5 standards.")
                print(f"Error details: {e}")
                print('\n')
                not_validated_file.append(hdf5file)
        return validated_files, not_validated_files
    else:
        #print("No hdf5 file found in the folder")
        return validated_files, not_validated_files

def validate_fits(files):
    """
    Validates FITS files.

    Parameters:
    - files: List of files to be validated.

    Returns:
    - list of validated and not validate file
    """
    #initate list of validated files
    validated_files = []
    not_validated_files = []

    if len(files)> 0:
        for file in files:
            print(f'Processing the file: {file}')
            try:
                hdul = fits.open(file)
                hdul.verify()
                print(f"The FITS file at {file} conforms to FITS standards.")
                header = hdul[0].header
                data = hdul[0].data
                for key, value in header.items():
                    print(f'{key}: {value}')
                hdul.close()
                validated_files.append(file)
                print('\n')
            except fits.verify.VerifyError as e:
                print(f"The FITS file at {file} does not conform to FITS standards.")
                print(f"Error details: {e}")
                print('\n')
                not_validated_file.append(file)
        return validated_files, not_validated_files
    else:
        #print("No fits file found in the folder")
        return validated_files, not_validated_files

def validate_numpy(files):
    """
    Validates NumPy .npz files.

    Parameters:
    - files: List of files to be validated.

    Returns:
    - list of validated and not validate file
    """
    #initate list of validated files
    validated_files = []
    not_validated_files = []

    if len(files)> 0:
        for npzfile in files:
            print(f'Processing the file: {npzfile}')
            try:
                with np.load(npzfile, allow_pickle=True) as data:
                    for key in data.keys():
                        array_info = data[key]
                        # Optionally, print or inspect the actual array data
                        # print(array_info)
                print(f"The npz file at {npzfile} is valid.")
                validated_files.append(npzfile)
                print('\n')
            except Exception as e:
                print(f"Error details: {e}")
                print('\n')
                not_validated_file.append(npzfile)
        return validated_files, not_validated_files
    else:
        #print("No numpy file found in the folder")
        return validated_files, not_validated_files

def validate_csv(files):
    """
    Validates CSV files.

    Parameters:
    - files: List of files to be validated.

    Returns:
    - list of validated and not validate file
    """
    #initate list of validated files
    validated_files = []
    not_validated_files = []

    if len(files)> 0:
        for csvfilename in files:
            print(f'Processing the file: {csvfilename}')
            try:
                with open(csvfilename, newline='') as csvfile:
                    reader = csv.DictReader(csvfile, ['index_1', 'source_id'])
                    next(reader, None)  # Skip header
                    for row in reader:
                        if not row['index_1'].isdigit() or not row['source_id'].isdigit():
                            print(f"The csv file at {csvfilename} is invalid.")
                            not_validated_file.append(csvfilename)
                            return validated_files, not_validated_files
                print(f"The csv file at {csvfilename} is valid.")
                validated_files.append(csvfilename)
            except Exception as e:
                print(f"Error details: {e}")
                print('\n')
                not_validated_file.append(csvfilename)
        return validated_files, not_validated_files
    else:
        #print("No csv file found in the folder")
        return validated_files, not_validated_files

def main(argv=None):
    #Parse command line arguments
    args  = parseoptions(argv)

    all_files = list_and_return_all_files(args.dir)
    print('The files present in the folder are: {}\n' .format(all_files))

    #Check if there is an omit list with list of files to be omitted from being validated 
    if (args.omit):
        extensions_filename = args.omit
        extensions = read_extensions_from_file(extensions_filename)
        # Filter files based on specific extensions
        filtered_files = filter_files(all_files, extensions)
    else:
        filtered_files = all_files

    print('The files to be validated are: {}\n' .format(filtered_files))

    #Create lists of each file type
    fits_list = [f for f in filtered_files if f.endswith(".fits")]
    h5_list = [f for f in filtered_files if f.endswith(".h5")]
    npz_list = [f for f in filtered_files if f.endswith(".npz")]
    csv_list = [f for f in filtered_files if f.endswith(".csv")]

    #Check and print validation of fits files
    validated_fits, failed_fits = validate_fits(fits_list)
    print_files_status(validated_fits, failed_fits)

    #Check and print validation of hdf5 files
    validated_hdf5, failed_hdf5 = validate_hdf5(h5_list)
    print_files_status(validated_hdf5, failed_hdf5)

    #Check and print validation of npz files
    validated_npz, failed_npz = validate_numpy(npz_list)
    print_files_status(validated_npz, failed_npz)

    #Check and print validation of csv files
    validated_csv, failed_csv = validate_csv(csv_list)
    print_files_status(validated_csv, failed_csv)

if __name__ == "__main__":
    main(argv[1:])
