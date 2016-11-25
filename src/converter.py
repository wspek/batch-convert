"""
 Created by waldo on 11/22/16
"""
import os
import logger
import rawpy
import imageio
from PIL import Image
from abc import ABCMeta, abstractmethod
from enum import Enum


__author__ = "waldo"
__project__ = "BatchConvert"


class Format(Enum):
    ALL = 0
    PHOTO = 1
    VIDEO = 2


class ImageSize(object):
    HD = {'length': 1920, 'width': 1080}
    ULTRA_HD = {'length': 3840, 'width': 2160}


class MediaObject(object):
    __metaclass__ = ABCMeta

    def __init__(self, path):
        self.path = path
        self.filename = self.path.split('/')[-1]
        self.root, extension = self.filename.split('.')
        self.extension = extension.lower()
        self.width, self.height = self.size()

    @abstractmethod
    def size(self):
        raise NotImplementedError("Please implement this method.")

    @abstractmethod
    def resize(self, new_length, new_width):
        raise NotImplementedError("Please implement this method.")

    @abstractmethod
    def save(self, output_path):
        raise NotImplementedError("Please implement this method.")

    @abstractmethod
    def save_as_format(self, format, output_path):
        raise NotImplementedError("Please implement this method.")

    def calc_new_size(self, width, height, max_length, max_width):
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


class JPGImageObject(MediaObject):
    def __init__(self, path):
        self.pil_image = Image.open(path)

        # EXIF data: things like ISO speed, shutter speed, aperture, white balance, camera model etc.
        self.exif = self.pil_image.info['exif']
        super(JPGImageObject, self).__init__(path)

    def size(self):
        return self.pil_image.width, self.pil_image.height

    def resize(self, new_length, new_width):
        message = "Resizing file: '{0}'.".format(self.filename)
        logger.write_log(message)

        new_width, new_height = self.calc_new_size(self.width, self.height, new_length, new_width)
        self.pil_image = self.pil_image.resize((new_width, new_height), Image.ANTIALIAS)

    def save(self, output_path):
        self.pil_image.save(output_path + '/' + self.filename, exif=self.exif)

    def save_as_format(self, file_format, output_path):
        if file_format in ['png']:
            message = "Converting file '{0}' to PNG.".format(self.filename)
            logger.write_log(message)

            file_path = '{0}/{1}.{2}'.format(output_path, self.root, file_format)
            self.pil_image.save(file_path)
        elif file_format in ['jpg', 'jpeg']:
            message = "Not converting file '{0}'. File is already JPEG.".format(self.filename)
            logger.write_log(message)
        else:
            message = "Cannot convert file '{0}'. Extension '{1}' not supported.".format(self.filename, file_format)
            logger.write_log(message)


class NEFImageObject(MediaObject):
    def __init__(self, path):
        self.rawpy_image = rawpy.imread(path)
        super(NEFImageObject, self).__init__(path)

    def size(self):
        size = self.rawpy_image.sizes
        return size.raw_width, size.raw_height

    def resize(self, new_length, new_width):
        message = "Cannot resize file '{0}'. NEF images cannot be resized.".format(self.filename)
        raise NotImplementedError(message)

    def save(self, output_path):
        message = "Cannot save file '{0}'. NEF images can only be read, not written.".format(self.filename)
        raise NotImplementedError(message)

    def save_as_format(self, file_format, output_path):
        if file_format in ['jpg', 'jpeg', 'png']:
            message = "Converting file '{0}' to JPEG.".format(self.filename)
            logger.write_log(message)

            file_path = '{0}/{1}.{2}'.format(output_path, self.root, file_format)
            post_processed = self.rawpy_image.postprocess(no_auto_bright=True, use_camera_wb=True)
            pil_image = Image.fromarray(post_processed)
            pil_image.save(file_path)
        else:
            message = "Cannot convert file '{0}'. Extension '{1}' not supported.".format(self.filename)
            logger.write_log(message)


class Converter(object):
    valid_input_formats = ['jpg', 'jpeg', 'nef']
    valid_output_formats = ['jpg', 'jpeg', 'png']

    @staticmethod
    def convert(**kwargs):
        if kwargs["input_folder"]:
            file_list = Converter.retrieve_filelist(kwargs["input_folder"],
                                                    kwargs["include_subdirectories"])
        else:
            file_list = kwargs["input_files"]

        message = "Number of files to process: " + str(len(file_list))
        logger.write_log(message)

        # Process the list of media files
        for index, media_path in enumerate(file_list):
            media_object = Converter.create_media(media_path)
            if media_object is not None:
                try:
                    if kwargs["resize"]:
                        new_length = kwargs["resize"][0]
                        new_width = kwargs["resize"][1]
                        media_object.resize(new_length, new_width)
                    if kwargs["output_format"]:
                        media_object.save_as_format(kwargs["output_format"], kwargs["output_folder"])
                    else:
                        media_object.save(kwargs["output_folder"])
                except Exception as e:
                    message = "Failed to convert file. Message: {0}".format(e.message)
                    logger.write_log(message)

    @staticmethod
    def retrieve_filelist(dirpath, subdirectories=True):
        filelist = []

        # If we want to traverse the path AND its subdirectories, we use 'os.walk'.
        if subdirectories is True:
            for (dirpath, dirnames, filenames) in os.walk(dirpath):
                for filename in filenames:
                    file_extension = os.path.splitext(filename)[1][1:].lower()
                    if Converter.valid_format(file_extension):
                        filelist.append(dirpath + "/" + filename)
        # Else, we are only interested in the files in the passed dirpath.
        else:
            for item in os.listdir(dirpath):
                filepath = os.path.join(dirpath, item)
                if os.path.isfile(filepath):
                    file_extension = os.path.splitext(item)[1][1:].lower()
                    if Converter.valid_format(file_extension):
                        filelist.append(filepath)

        return filelist

    # Factory
    @staticmethod
    def create_media(path):
        filename = path.split('/')[-1]
        extension = filename.split('.')[1].lower()

        if extension in ['jpg', 'jpeg']:
            return JPGImageObject(path)
        elif extension == 'nef':
            return NEFImageObject(path)
        else:
            message = "Cannot convert '{0}'. File extension not supported.".format(filename)
            logger.write_log(message)
            return None

    @staticmethod
    def valid_format(extension):
        # A file is valid if it is in the input list for its type.
        return extension in Converter.valid_input_formats


# class VideoConverter(object):
#     input_formats = ['wmv', 'mov']
#     output_formats = ['mp4']
#
#     def valid_format(self, file_format, extension):
#         # A file is valid if it is in the input list for its type.
#         return file_format == Format.VIDEO and extension in VideoConverter.input_formats
#
#     @staticmethod
#     def convert_video(input_path, output_folder, input_format, output_format):
#         # First check whether the requested conversion formats are valid. If not, notify user and return.
#         if input_format.lower() not in VideoConverter.input_formats or \
#                         output_format.lower() not in VideoConverter.output_formats:
#             print "Conversion from '" + input_format + "' to '" + output_format + "' not possible.",
#
#             # Print all possible allowed conversion formats to screen.
#             conversions = ((i, o) for i in VideoConverter.input_formats for
#                            o in VideoConverter.output_formats)
#             print "Possible conversions:\n"
#             for i, o in conversions:
#                 print i + " -> " + o
#             return
#         # If the input file or folder (path) is invalid, notify the user and return.
#         if not os.path.exists(input_path):
#             print "The path '" + input_path + "' does not seem to exist. Please retry with a valid path."
#             return
#         # If the input path is a directory, list all the video files in the directory for conversion.
#         if os.path.isdir(input_path):
#             inputfiles = [os.path.splitext(f)[0] for f in os.listdir(input_path) if
#                           os.path.splitext(f.lower())[1][1:] in VideoConverter.input_formats]
#
#             for f in inputfiles:
#                 os.system('ffmpeg -i "%s/%s.%s" -c:v:1 copy -strict -2 "%s/%s.%s"' % (
#                     input_path, f, input_format, output_folder, f, output_format))
#         # If the input path is a file, then store this as an only element in the list to convert.
#         elif os.path.isfile(input_path):
#             if os.path.splitext(input_path.lower())[1][1:] in VideoConverter.input_formats:
#                 inputfile = os.path.splitext(input_path)[0]
#                 file_name = inputfile.split('/')[-1]
#             os.system('ffmpeg -i "%s.%s" -c:v:1 copy -strict -2 "%s/%s.%s"' % (
#                 inputfile, input_format, output_folder, file_name, output_format))