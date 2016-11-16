import os
import filesync
import argparse
from enum import Enum
from PIL import Image

output_log = '/media/waldo/DATA-SHARE/Code/BatchConvert/output/output.log'


input_formats_image = ['jpg', 'jpeg', 'nef']
output_formats_image = ['jpg', 'jpeg', 'nef']
input_formats_video = ['wmv', 'mov']
output_formats_video = ['mp4']

AP_PROGRAM = u"Batch convert"
AP_DESCRIPTION = u"Convert and resize images and video's."
AP_ARGUMENTS = [
    {
        "name": "file",
        "nargs": '*',
        "type": str,
        "default": None,
        "help": "One or more input files"
    },
    # {
    #     "name": "--output",
    #     "nargs": "?",
    #     "type": str,
    #     "default": None,
    #     "help": "Output to file instead of using the standard output"
    # },
    # {
    #     "name": "--csv",
    #     "action": "store_true",
    #     "help": "Output in CSV format instead of human-readable format"
    # },
    # {
    #     "name": "--pdf",
    #     "nargs": "?",
    #     "type": str,
    #     "default": None,
    #     "help": "Output to PDF"
    # },
    # {
    #     "name": "--list",
    #     "action": "store_true",
    #     "help": "List the titles of books with annotations or highlights"
    # },
    # {
    #     "name": "--book",
    #     "nargs": "?",
    #     "type": str,
    #     "default": None,
    #     "help": "Output annotations and highlights only from the book with the given title"
    # },
    # {
    #     "name": "--bookid",
    #     "nargs": "?",
    #     "type": str,
    #     "default": None,
    #     "help": "Output annotations and highlights only from the book with the given ID"
    # },
    # {
    #     "name": "--annotations-only",
    #     "action": "store_true",
    #     "help": "Outputs annotations only, excluding highlights"
    # },
    # {
    #     "name": "--highlights-only",
    #     "action": "store_true",
    #     "help": "Outputs highlights only, excluding annotations"
    # },
    # {
    #     "name": "--info",
    #     "action": "store_true",
    #     "help": "Print information about the number of annotations and highlights"
    # },
]


class Format(Enum):
    ALL = 0
    PHOTO = 1
    VIDEO = 2


class ImageSize(object):
    HD = {'length': 1920, 'width': 1080}
    ULTRA_HD = {'length': 3840, 'width': 2160}


def retrieve_list(dirpath, file_format=Format.ALL, subdirectories=True):
    filelist = []
    if subdirectories is True:
        for (dirpath, dirnames, filenames) in os.walk(dirpath):
            for filename in filenames:
                file_extension = os.path.splitext(filename)[1][1:].lower()
                if (file_format == Format.PHOTO and file_extension in input_formats_image or
                    file_format == Format.VIDEO and file_extension in input_formats_video or
                    file_format == Format.ALL and file_extension in input_formats_image + input_formats_video):
                        filelist.append(dirpath + "/" + filename)
    else:
        for item in os.listdir(dirpath):
            filename = os.path.join(dirpath, item)
            if os.path.isfile(filename):
                file_extension = os.path.splitext(item)[1][1:].lower()
                if (file_format == Format.PHOTO and file_extension in input_formats_image or
                    file_format == Format.VIDEO and file_extension in input_formats_video or
                    file_format == Format.ALL and file_extension in input_formats_image + input_formats_video):
                    filelist.append(dirpath + "/" + filename)

    return filelist


def resize_images(input_path, output_path, subdirectories=True):
    image_list = retrieve_list(input_path, file_format=Format.PHOTO, subdirectories=subdirectories)

    print "Number of files to resize: " + str(len(image_list))

    raw_input("Press any key to continue")

    for index, item in enumerate(image_list):
        try:
            filename = item.split('/')[-1]
            image = Image.open(item)
            exif = image.info['exif']
            new_width, new_height = calculate_size(image.width, image.height,
                                                   ImageSize.ULTRA_HD['length'], ImageSize.ULTRA_HD['width'])

            message = "[" + str(index) + "] Resizing and saving file: '" + filename + "'."
            write_log(message)

            img_resized = image.resize((new_width, new_height), Image.ANTIALIAS)
            img_resized.save(output_path + '/' + '4-' + filename, exif=exif)
        except Exception as e:
            message = "[{0}] Failed to resize. Message: {1}.".format(index, e.message)
            write_log(message)


def write_log(message='', mode='a'):
    print message
    with open(output_log, mode) as log:
        log.write(message + '\n')


def calculate_size(width, height, max_length, max_width):
    orig_length = max(height, width)
    orig_width = min(height, width)

    length_ratio = max_length / float(orig_length)
    width_ratio = max_width / float(orig_width)

    resize_factor = max(length_ratio, width_ratio)
    new_width, new_height = map(lambda x: resize_factor * x, (width, height))
    return int(new_width), int(new_height)


def convert_video(input_path, output_folder, input_format, output_format):
    # First check whether the requested conversion formats are valid. If not, notify user and return.
    if input_format not in input_formats_video or output_format not in output_formats_video:
        print "Conversion from '" + input_format + "' to '" + output_format + "' not possible.",

        # Print all possible allowed conversion formats to screen.
        conversions = ((i, o) for i in input_formats_video for o in output_formats_video)
        print "Possible conversions:\n"
        for i, o in conversions:
            print i + " -> " + o
        return
    # If the input file or folder (path) is invalid, notify the user and return.
    if not os.path.exists(input_path):
        print "The path '" + input_path + "' does not seem to exist. Please retry with a valid path."
        return
    # If the input path is a directory, list all the video files in the directory for conversion.
    if os.path.isdir(input_path):
        inputfiles = [os.path.splitext(f)[0] for f in os.listdir(input_path) if
                      os.path.splitext(f.lower())[1][1:] in input_formats_video]

        for f in inputfiles:
            os.system('ffmpeg -i "%s/%s.%s" -c:v:1 copy -strict -2 "%s/%s.%s"' % (
                input_path, f, input_format, output_folder, f, output_format))
    # If the input path is a file, then store this as an only element in the list to convert.
    elif os.path.isfile(input_path):
        if os.path.splitext(input_path.lower())[1][1:] in input_formats_video:
            inputfile = os.path.splitext(input_path)[0]
            file_name = inputfile.split('/')[-1]
        os.system('ffmpeg -i "%s.%s" -c:v:1 copy -strict -2 "%s/%s.%s"' % (
            inputfile, input_format, output_folder, file_name, output_format))


def run():
    parser = argparse.ArgumentParser(
        AP_PROGRAM,
        AP_DESCRIPTION
    )
    parser.parse_args()

    write_log("Starting execution.", 'w')

    resize_images('/media/waldo/SSD/Nikon-SDs/Kingston-MicroSD-94749-2',
                  '/media/waldo/TRANSCEND-SSD/Photos/Sylvia/Uitzoeken-KINGSTON-SD', subdirectories=True)

    # resize_images('/media/waldo/DATA-SHARE/Code/BatchConvert/test/input',
    #               '/media/waldo/DATA-SHARE/Code/BatchConvert/test/output', subdirectories=True)
    # convert_video(
    #     '/media/waldo/TRANSCEND-SSD/Film/Video/Travels/New Zealand_2016/New Zealand V - Waikato & King Country.wmv',
    #     '/tmp', 'wmv', 'mp4')


def main():
    run()


if __name__ == '__main__':
    main()
