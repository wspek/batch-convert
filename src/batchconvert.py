import sys
import os
import argparse
from enum import Enum
from PIL import Image


output_log = '/media/waldo/DATA-SHARE/Code/BatchConvert/output/output.log'


class Format(Enum):
    ALL = 0
    PHOTO = 1
    VIDEO = 2


class ImageSize(object):
    HD = {'length': 1920, 'width': 1080}
    ULTRA_HD = {'length': 3840, 'width': 2160}


def write_log(message='', mode='a'):
    print message
    with open(output_log, mode) as log:
        log.write(message + '\n')


def retrieve_filelist(dirpath, file_format=Format.ALL, subdirectories=True):
    filelist = []

    # If we want to traverse the path AND its subdirectories, we use 'os.walk'.
    if subdirectories is True:
        for (dirpath, dirnames, filenames) in os.walk(dirpath):
            for filename in filenames:
                # file_extension = os.path.splitext(filename)[1][1:].lower()
                # if valid_format(file_format, file_extension):
                        filelist.append(dirpath + "/" + filename)
    # Else, we are only interested in the files in the passed dirpath.
    else:
        for item in os.listdir(dirpath):
            filename = os.path.join(dirpath, item)
            if os.path.isfile(filename):
                # file_extension = os.path.splitext(item)[1][1:].lower()
                # if valid_format(file_format, file_extension):
                    filelist.append(dirpath + "/" + filename)

    return filelist


class CommandLineTool(object):
    # overload in the actual subclass
    #
    AP_PROGRAM = sys.argv[0]
    AP_DESCRIPTION = u"Generic Command Line Tool"
    AP_ARGUMENTS = [
        # required args
        # {"name": "foo", "nargs": 1, "type": str, "default": "baz", "help": "Foo help"},
        #
        # optional args
        # {"name": "--bar", "nargs": "?", "type": str,, "default": "foofoofoo", "help": "Bar help"},
        # {"name": "--quiet", "action": "store_true", "help": "Do not output to stdout"},
    ]

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog=self.AP_PROGRAM,
            description=self.AP_DESCRIPTION
        )
        self.vargs = None
        for arg in self.AP_ARGUMENTS:
            if "action" in arg:
                self.parser.add_argument(
                    arg["name"],
                    action=arg["action"],
                    help=arg["help"]
                )
            else:
                self.parser.add_argument(
                    arg["name"],
                    nargs=arg["nargs"],
                    type=arg["type"],
                    default=arg["default"],
                    help=arg["help"]
                )

    def run(self):
        self.vargs = vars(self.parser.parse_args())
        # self.actual_command() #TODO
        sys.exit(0)

    # overload this in your actual subclass
    def actual_command(self):
        self.print_stdout(u"This script does nothing. Invoke another .py")

    @staticmethod
    def error(message):
        print u"ERROR: {0}".format(message)
        sys.exit(1)

    @staticmethod
    def print_stdout(*args, **kwargs):
        print u"{0}\n{1}".format(args, kwargs)

    @staticmethod
    def print_stderr(*args, **kwargs):
        print u"{0}\n{1}\n{2}".format(args, sys.stderr, kwargs)


class ImageConverter(CommandLineTool):
    input_formats = ['jpg', 'jpeg', 'nef']
    output_formats = ['jpg', 'jpeg', 'nef']

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

    @staticmethod
    def resize_images(input_path, output_path, subdirectories=True):
        image_list = retrieve_filelist(input_path, file_format=Format.PHOTO, subdirectories=subdirectories)

        message = "Number of files to resize: " + str(len(image_list))
        write_log(message)

        raw_input("\nPress any key to continue...\n")

        for index, item in enumerate(image_list):
            try:
                filename = item.split('/')[-1]
                image = Image.open(item)

                new_width, new_height = ImageConverter.calculate_size(
                                                            image.width, image.height,
                                                            ImageSize.ULTRA_HD['length'],
                                                            ImageSize.ULTRA_HD['width'])

                message = "[" + str(index) + "] Resizing and saving file: '" + filename + "'."
                write_log(message)

                img_resized = image.resize((new_width, new_height), Image.ANTIALIAS)

                # EXIF data: things like ISO speed, shutter speed, aperture, white balance, camera model etc.
                exif = image.info['exif']
                img_resized.save(output_path + '/' + filename, exif=exif)
            except Exception as e:
                message = "[{0}] Failed to resize. Message: {1}.".format(index, e.message)
                write_log(message)

    @staticmethod
    def calculate_size(width, height, max_length, max_width):
        # In this context 'length' means the longest side of the image i.e. the greatest value between height
        # & width. Implicitly this means that 'width' is the shortest side.
        orig_length = max(height, width)
        orig_width = min(height, width)

        # Calculate for both the longest as the shortest side how much the resize factor should be.
        length_ratio = max_length / float(orig_length)
        width_ratio = max_width / float(orig_width)

        # Choose the largest resize factor, since we would like to keep the current aspect ratio of the image.
        resize_factor = max(length_ratio, width_ratio)
        new_width, new_height = map(lambda x: resize_factor * x, (width, height))

        return int(new_width), int(new_height)

    @staticmethod
    def valid_format(file_format, extension):
        # A file is valid if it is in the input list for its type.
        return file_format == Format.PHOTO and extension in ImageConverter.input_formats


class VideoConverter(CommandLineTool):
    input_formats = ['wmv', 'mov']
    output_formats = ['mp4']

    @staticmethod
    def convert_video(input_path, output_folder, input_format, output_format):
        # First check whether the requested conversion formats are valid. If not, notify user and return.
        if input_format not in VideoConverter.input_formats or \
           output_format not in VideoConverter.output_formats:
            print "Conversion from '" + input_format + "' to '" + output_format + "' not possible.",

            # Print all possible allowed conversion formats to screen.
            conversions = ((i, o) for i in VideoConverter.input_formats for
                           o in VideoConverter.output_formats)
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
                          os.path.splitext(f.lower())[1][1:] in VideoConverter.input_formats]

            for f in inputfiles:
                os.system('ffmpeg -i "%s/%s.%s" -c:v:1 copy -strict -2 "%s/%s.%s"' % (
                    input_path, f, input_format, output_folder, f, output_format))
        # If the input path is a file, then store this as an only element in the list to convert.
        elif os.path.isfile(input_path):
            if os.path.splitext(input_path.lower())[1][1:] in VideoConverter.input_formats:
                inputfile = os.path.splitext(input_path)[0]
                file_name = inputfile.split('/')[-1]
            os.system('ffmpeg -i "%s.%s" -c:v:1 copy -strict -2 "%s/%s.%s"' % (
                inputfile, input_format, output_folder, file_name, output_format))

    @staticmethod
    def valid_format(file_format, extension):
        # A file is valid if it is in the input list for its type.
        return file_format == Format.VIDEO and extension in VideoConverter.input_formats_image


def run():
    write_log("Starting execution.", 'w')

    # resize_images('/media/waldo/SSD/Nikon-SDs/Kingston-MicroSD-94749-2',
    #               '/media/waldo/TRANSCEND-SSD/Photos/Sylvia/Uitzoeken-KINGSTON-SD', subdirectories=True)

    ImageConverter().resize_images('/media/waldo/DATA-SHARE/Code/BatchConvert/test/input',
                                   '/media/waldo/DATA-SHARE/Code/BatchConvert/test/output',
                                   subdirectories=True)
    # convert_video(
    #     '/media/waldo/TRANSCEND-SSD/Film/Video/Travels/New Zealand_2016/New Zealand V - Waikato & King Country.wmv',
    #     '/tmp', 'wmv', 'mp4')


def main():
    run()


if __name__ == '__main__':
    main()
