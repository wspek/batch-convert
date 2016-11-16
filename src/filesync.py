'''
 Created by waldo on 10/22/16

 TODO:
 - Remove dot '.' from formats list
'''
import os
import csv
import hashlib
import shutil
from datetime import datetime
from time import sleep
from enum import Enum

__author__ = "waldo"
__project__ = "Snippets"

"""
- Scan all files and folders recursively
    - Get (md5sum, name, location, date/time)
    - Write data to file for later retrieval

- Read out data file and put data into dictionary
    { <id> : (<name>, <location>, <datetime>) }

- Traverse files on GoPro
    - Calculate md5
    - If file exists, log.
    - Else copy file to specified folder and log.
"""

results_file = '/media/waldo/DATA-SHARE/Code/Snippets/output/FileSync/scan_results.csv'
output_log = '/media/waldo/DATA-SHARE/Code/Snippets/output/FileSync/output.log'
photo_formats = ['.jpg', '.jpeg', '.png', '.gif', '.nef']
video_formats = ['.mp4', '.mov', '.wmv']


class Format(Enum):
    ALL = 0
    PHOTO = 1
    VIDEO = 2


def retrieve_files(path_to_folder, file_format=Format.ALL):
    filelist = []

    for (dirpath, dirnames, filenames) in os.walk(path_to_folder):
        for filename in filenames:
            file_extension = os.path.splitext(filename)[1].lower()
            if (file_format == Format.PHOTO and file_extension in photo_formats or
                file_format == Format.VIDEO and file_extension in video_formats or
                file_format == Format.ALL):
                filelist.append(dirpath + "/" + filename)
    return filelist


def md5sum(filename):
    md5 = hashlib.md5()

    with open(filename, 'r') as file_to_calculate:
        for chunk in iter(lambda: file_to_calculate.read(4096), b''):
            md5.update(chunk)
    return md5.hexdigest()


def date_time(filename):
    timestamp = os.path.getmtime(filename)
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


# - Scan all files and folders recursively
#   - Get (md5sum, name, location, date/time)
#   - Write data to file for later retrieval
def index_folder(path_to_folder, file_format=Format.ALL):
    with open(results_file, 'w') as csvfile:
        fieldnames = ['id', 'filename', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Retrieve the list of files we want to analyze
        filelist = retrieve_files(path_to_folder, file_format)
        print "Number of files to process: " + str(len(filelist))
        sleep(2)

        # For each file in 'path_to_folder" and subfolders
        for index, filename in enumerate(filelist):
            checksum = md5sum(filename)
            timestamp = date_time(filename)

            # Write data to file
            print "Writing file [" + str(index + 1) + "]: " + checksum
            writer.writerow({'id': checksum, 'filename': filename, 'timestamp': timestamp})


def sync_folders(input_folder, output_folder, file_format=Format.ALL, checksum=True):
    stored_files = dict()

    # Read the scan results into memory
    with open(results_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for index, row in enumerate(reader):
            print "Reading row [" + str(index + 1) + "]."
            stored_files[row['id']] = (row['filename'], row['timestamp'])

    # For every file in the input folder, determine if the file has been copied yet. Log appropriately.
    with open(output_log, 'w') as logfile:
        source_files = retrieve_files(input_folder, file_format)
        print "Number of source files: " + str(len(source_files))
        sleep(2)

        for index, filename in enumerate(source_files):
            if checksum is True:
                checksum = md5sum(filename)
                if checksum in stored_files.keys():
                    log_message = '[OK] - File ' + str(index + 1) + ' exists already (' + filename + ') in folder (' \
                                  + stored_files[checksum][0] + ')'
                    print log_message
                    logfile.write(log_message + '\n')
                else:
                    log_message = '[XX] - File ' + str(index + 1) + ' does not exist. Copying... (' + filename + ')'
                    print log_message
                    logfile.write(log_message + '\n')
                    shutil.copy(filename, output_folder)
            else:
                log_message = '[XX] - File ' + str(index + 1) + '. Copying... (' + filename + ')'
                print log_message
                logfile.write(log_message + '\n')
                shutil.copy(filename, output_folder)


if __name__ == "__main__":
    # index_folder('/media/waldo/SSD/Nikon-SDs/', Format.ALL)
    sync_folders('/media/waldo/3B18-FA26',
                 '/media/waldo/SSD/Nikon-SDs/Kingston-MicroSD-31436-2/Photo', Format.PHOTO, checksum=False)
