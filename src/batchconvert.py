import sys
import argparse
import logger
from converter import ImageConverter
from converter import VideoConverter


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
        logger.write_log("Starting execution.", 'w')

        self.parser = argparse.ArgumentParser(
            prog=self.AP_PROGRAM,
            description=self.AP_DESCRIPTION,
            formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=32)
        )
        self.vargs = None

        groups = dict()
        for arg in self.AP_ARGUMENTS:
            # Return the mutually exclusive group or 'None' if not present.
            group = arg.pop("group", None)
            if group is not None:
                # Create a dictionary of mutually exclusive groups
                groups.setdefault(group, []).append(arg)
            else:
                # Add the remaining arguments by unpacking the dictionary with remaining menu entries.
                name = arg.pop("name")
                self.parser.add_argument(name, **arg)

        # If there are mutually exclusive groups to be made, we go into this loop
        for group_name, arguments in groups.iteritems():
            group = self.parser.add_mutually_exclusive_group()
            for arg in arguments:
                name = arg.pop("name")
                group.add_argument(name, **arg)

    def run(self):
        self.vargs = vars(self.parser.parse_args())
        self.actual_command()
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


class ConversionTool(CommandLineTool):
    formats = ImageConverter.output_formats + VideoConverter.output_formats

    AP_PROGRAM = u"Batch convert"
    AP_DESCRIPTION = u"Convert and resize images and video's."
    AP_ARGUMENTS = [
        {
            "name": "FOLDER",
            "nargs": None,
            "type": str,
            "default": None,
            "help": "Output folder"
        },
        {
            "name": "-r",
            "action": "store_true",
            "help": "Include subfolders"
        },
        {
            "group": "input",
            "name": "--input",
            "nargs": '?',
            "type": str,
            "default": None,
            "help": "Input folder",
            "metavar": "FOLDER"
        },
        {
            "group": "input",
            "name": "--file",
            "nargs": '*',
            "type": str,
            "default": None,
            "help": "One or more input files"
        },
        {
            "group": "action",
            "name": "--format",
            "nargs": 1,
            "type": str,
            "default": None,
            "help": "Output format after conversion",
            "choices": formats
        },
        {
            "group": "action",
            "name": "--resize",
            "nargs": 2,
            "type": int,
            "default": None,
            "help": "Output image size",
            "metavar": ("LENGTH", "WIDTH")
        },
    ]

    def actual_command(self):
        output_folder = self.vargs["FOLDER"]

        # If the input consists of a folder...
        if self.vargs["input"]:
            input_folder = self.vargs["input"]
        # else if input files...

        if self.vargs["resize"]:
            new_sizes = self.vargs["resize"]
            length = new_sizes[0]
            width = new_sizes[1]
            include_subdirectories = self.vargs['r']
            ImageConverter().resize_images(length, width, input_folder, output_folder, include_subdirectories)
        if self.vargs["format"]:
            pass

    def reformat(self):
        pass


def main():
    ConversionTool().run()

    # def run(self):
    # logger.write_log("Starting execution.", 'w')

    # resize_images('/media/waldo/SSD/Nikon-SDs/Kingston-MicroSD-94749-2',
    #               '/media/waldo/TRANSCEND-SSD/Photos/Sylvia/Uitzoeken-KINGSTON-SD', subdirectories=True)

    # self.resize_images('/media/waldo/DATA-SHARE/Code/BatchConvert/test/input',
    #                    '/media/waldo/DATA-SHARE/Code/BatchConvert/test/output',
    #                    subdirectories=True)


    # def run():
    #     logger.write_log("Starting execution.", 'w')
    #
    #     # resize_images('/media/waldo/SSD/Nikon-SDs/Kingston-MicroSD-94749-2',
    #     #               '/media/waldo/TRANSCEND-SSD/Photos/Sylvia/Uitzoeken-KINGSTON-SD', subdirectories=True)
    #
    #     ImageConverter().resize_images('/media/waldo/DATA-SHARE/Code/BatchConvert/test/input',
    #                                    '/media/waldo/DATA-SHARE/Code/BatchConvert/test/output',
    #                                    subdirectories=True)
    #     # convert_video(
    #     #     '/media/waldo/TRANSCEND-SSD/Film/Video/Travels/New Zealand_2016/New Zealand V - Waikato & King Country.wmv',
    #     #     '/tmp', 'wmv', 'mp4')


if __name__ == '__main__':
    main()