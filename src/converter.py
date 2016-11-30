"""
 Created by waldo on 11/22/16
"""
import os
import logger
import rawpy
import subprocess
import itertools
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
    def save_as_format(self, file_format, output_path):
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


class PILImageObject(MediaObject):
    def __init__(self, path):
        self.pil_image = Image.open(path)
        super(PILImageObject, self).__init__(path)

    def size(self):
        return self.pil_image.width, self.pil_image.height

    def resize(self, new_length, new_width):
        message = "Resizing file: '{0}'.".format(self.filename)
        logger.write_log(message)

        new_width, new_height = self.calc_new_size(self.width, self.height, new_length, new_width)
        self.pil_image = self.pil_image.resize((new_width, new_height), Image.ANTIALIAS)

    def save(self, output_path):
        self.pil_image.save(output_path + '/' + self.filename)

    def save_as_format(self, file_format, output_path):
        if file_format in ['png', 'jpg', 'jpeg']:
            if self.extension == file_format:
                message = "Resaving file '{0}'. File is already in {1} format.".format(self.filename, file_format.upper())
                logger.write_log(message)
                self.save(output_path)
            else:
                message = "Converting file '{0}' to {1}.".format(self.filename, file_format.upper())
                logger.write_log(message)
                file_path = '{0}/{1}.{2}'.format(output_path, self.root, file_format)
                self.pil_image.save(file_path)
        else:
            message = "Cannot convert file '{0}'. Extension '{1}' not supported.".format(self.filename, file_format)
            logger.write_log(message)


class EXIFImageObject(PILImageObject):
    def __init__(self, path):
        super(EXIFImageObject, self).__init__(path)

        # EXIF data: things like ISO speed, shutter speed, aperture, white balance, camera model etc.
        self.exif = self.pil_image.info['exif']

    def save(self, output_path):
        self.pil_image.save(output_path + '/' + self.filename, exif=self.exif)


class NEFImageObject(MediaObject):
    def __init__(self, path):
        with rawpy.imread(path) as rawpy_image:
            post_processed = rawpy_image.postprocess(no_auto_bright=True, use_camera_wb=True)
            self.pil_image = Image.fromarray(post_processed)

        super(NEFImageObject, self).__init__(path)

    def size(self):
        return self.pil_image.width, self.pil_image.height

    def resize(self, new_length, new_width):
        message = "Resizing file: '{0}'.".format(self.filename)
        logger.write_log(message)

        new_width, new_height = self.calc_new_size(self.width, self.height, new_length, new_width)
        self.pil_image = self.pil_image.resize((new_width, new_height), Image.ANTIALIAS)

    def save(self, output_path):
        message = "Cannot save file '{0}'. NEF images can only be read, not written.".format(self.filename)
        raise NotImplementedError(message)

    def save_as_format(self, file_format, output_path):
        if file_format in ['jpg', 'jpeg', 'png']:
            message = "Converting file '{0}' to {1}.".format(self.filename, file_format.upper())
            logger.write_log(message)

            file_path = '{0}/{1}.{2}'.format(output_path, self.root, file_format)
            self.pil_image.save(file_path)
        else:
            message = "Cannot convert file '{0}'. Extension '{1}' not supported.".format(self.filename, file_format)
            logger.write_log(message)


class VideoObject(MediaObject):
    def __init__(self, path):
        super(VideoObject, self).__init__(path)

    def size(self):
        try:
            command = 'ffprobe -v error -show_entries stream=width,height -select_streams v:0 ' \
                      '-of default=noprint_wrappers=1 {0}'.format(self.path)
            output = subprocess.check_output(command.split())
            width, height = [int(dim.split('=')[1]) for dim in output.strip().split('\n') if dim]
        except Exception as e:
            message = "Failed to get size of MP4 object. Exiting. Message: {0}. File: {1}".format(e.message, self.path)
            logger.write_log(message)
            exit(1)
        return width, height

    def save(self, output_path):
        try:
            output = output_path + '/' + self.filename
            command = 'ffmpeg -i {0} -vf scale={1}:{2} -strict -2 {3} -hide_banner'.format(self.path, self.width, self.height, output)
            subprocess.call(command.split())
        except Exception as e:
            message = "Failed to save video object. Exiting. Message: {0}. File: {1}".format(e.message, self.path)
            logger.write_log(message)

    def resize(self, new_length, new_width):
        message = "Resizing file: '{0}'.".format(self.filename)
        logger.write_log(message)

        width, height = self.calc_new_size(self.width, self.height, new_length, new_width)

        # To resize with ffmpeg we can only use dimensions divisible by 2 (i.e. even numbers)
        self.width = width + (width % 2)
        self.height = height + (height % 2)

    def save_as_format(self, file_format, output_path):
        if file_format in ['avi', 'mp4', 'wmv', 'mov']:
            message = "Converting file '{0}' to {1}.".format(self.filename, file_format.upper())
            logger.write_log(message)

            file_path = '{0}/{1}.{2}'.format(output_path, self.root, file_format)
            command = 'ffmpeg -i {0} -vf scale={1}:{2} -strict -2 {3} -hide_banner'.format(self.path, self.width, self.height, file_path)
            subprocess.call(command.split())
        else:
            message = "Cannot convert file '{0}'. Extension '{1}' not supported.".format(self.filename, file_format)
            logger.write_log(message)


class Converter(object):

    valid_input_formats = ['jpg', 'jpeg', 'nef', 'png', 'mp4', 'avi', 'wmv', 'mov']
    valid_output_formats = ['jpg', 'jpeg', 'png', 'avi', 'mp4', 'wmv', 'mov']

    def __init__(self):
        available_classes = self.media_list(MediaObject)
        pass

    def media_list(self, cls):
        # Retrieve all subclasses
        subclasses = cls.__subclasses__()

        # Retrieve all nested subclasses and merge the nested subclasses with the subclasses
        nested_subclasses = subclasses + [self.media_list(c) for c in subclasses]

        # Remove any empty lists in the total list
        cleaned_up = [subclass for subclass in nested_subclasses if subclass]

        # There may be lists of subclass lists in the cleaned up list. Flatten the list.
        flattened = []
        for sublist in cleaned_up:
            if isinstance(sublist, list):
                for val in sublist:
                    flattened.append(val)
            else:
                flattened.append(sublist)

        return flattened

    @staticmethod
    def convert(**kwargs):
        if kwargs["input_folder"]:
            file_list = Converter.retrieve_filelist(kwargs["input_folder"], kwargs["include_subdirectories"])
        else:
            file_list = kwargs["input_files"]

        message = "Number of files to process: " + str(len(file_list))
        logger.write_log(message)

        # Process the list of media files
        num_files = len(file_list)
        for index, media_path in enumerate(file_list):
            media_object = Converter.create_media(media_path)
            if media_object is not None:
                logger.write_log("Processing file {0}/{1}".format(index+1, num_files))
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

        # If the input file is a file with EXIF data:
        if extension in ['jpg', 'jpeg']:
            return EXIFImageObject(path)
        # If the input file is a generic image file (without EXIF data):
        elif extension in ['png']:
            return PILImageObject(path)
        # Specific file formats follow here
        elif extension == 'nef':
            return NEFImageObject(path)
        elif extension in ['avi', 'mp4', 'wmv', 'mov']:
            return VideoObject(path)
        else:
            message = "Cannot convert '{0}'. File extension not supported.".format(filename)
            logger.write_log(message)
            return None

    @staticmethod
    def valid_format(extension):
        # A file is valid if it is in the input list for its type.
        return extension in Converter.valid_input_formats