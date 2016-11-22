"""
 Created by waldo on 11/22/16
"""
import os
import logger
from abc import ABCMeta, abstractmethod
from enum import Enum
from PIL import Image


__author__ = "waldo"
__project__ = "BatchConvert"


class Format(Enum):
    ALL = 0
    PHOTO = 1
    VIDEO = 2


class ImageSize(object):
    HD = {'length': 1920, 'width': 1080}
    ULTRA_HD = {'length': 3840, 'width': 2160}


class Converter(object):
    __metaclass__ = ABCMeta

    input_formats = []
    output_formats = []

    def retrieve_filelist(self, dirpath, subdirectories=True):
        filelist = []

        # If we want to traverse the path AND its subdirectories, we use 'os.walk'.
        if subdirectories is True:
            for (dirpath, dirnames, filenames) in os.walk(dirpath):
                for filename in filenames:
                    file_extension = os.path.splitext(filename)[1][1:].lower()
                    if self.valid_format(file_extension):
                        filelist.append(dirpath + "/" + filename)
        # Else, we are only interested in the files in the passed dirpath.
        else:
            for item in os.listdir(dirpath):
                filepath = os.path.join(dirpath, item)
                if os.path.isfile(filepath):
                    file_extension = os.path.splitext(item)[1][1:].lower()
                    if self.valid_format(file_extension):
                        filelist.append(filepath)

        return filelist

    @abstractmethod
    def valid_format(self, extension):
        raise NotImplementedError("Please implement this method.")

    def convert(self):
        raise NotImplementedError("Please implement this method.")

    def resize(self):
        pass


class ImageConverter(Converter):
    input_formats = ['jpg', 'jpeg', 'nef']
    output_formats = ['jpg', 'jpeg', 'nef']

    def valid_format(self, extension):
        # A file is valid if it is in the input list for its type.
        return Format.PHOTO and extension in self.input_formats

    def resize_images(self, length, width, input_path, output_path, subdirectories=True):
        image_list = self.retrieve_filelist(input_path, subdirectories=subdirectories)

        message = "Number of files to resize: " + str(len(image_list))
        logger.write_log(message)

        raw_input("\nPress any key to continue...\n")

        for index, item in enumerate(image_list):
            try:
                filename = item.split('/')[-1]
                file_extension = filename.split('.')[1].lower()

                if not self.valid_format(file_extension):
                    message = "[{0}] Unable to convert '{1}'. Unsupported source format.".format(index, filename)
                    logger.write_log(message)
                    continue

                image = Image.open(item)

                new_width, new_height = ImageConverter.calculate_size(image.width, image.height,
                                                                      length, width)

                message = "[" + str(index) + "] Resizing and saving file: '" + filename + "'."
                logger.write_log(message)

                img_resized = image.resize((new_width, new_height), Image.ANTIALIAS)

                # EXIF data: things like ISO speed, shutter speed, aperture, white balance, camera model etc.
                exif = image.info['exif']
                img_resized.save(output_path + '/' + filename, exif=exif)

            except Exception as e:
                message = "[{0}] Failed to resize. Message: {1}.".format(index, e.strerror)
                logger.write_log(message)

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


class VideoConverter(object):
    input_formats = ['wmv', 'mov']
    output_formats = ['mp4']

    def valid_format(self, file_format, extension):
        # A file is valid if it is in the input list for its type.
        return file_format == Format.VIDEO and extension in VideoConverter.input_formats

    @staticmethod
    def convert_video(input_path, output_folder, input_format, output_format):
        # First check whether the requested conversion formats are valid. If not, notify user and return.
        if input_format.lower() not in VideoConverter.input_formats or \
                        output_format.lower() not in VideoConverter.output_formats:
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

