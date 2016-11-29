import sys
import argparse
import logger
from converter import Converter


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
            formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=64)
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
    formats = Converter.valid_output_formats

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
            "name": "--format",
            "nargs": 1,
            "type": str,
            "default": None,
            "help": "Output format after conversion",
            "choices": formats
        },
        {
            "name": "--resize",
            "nargs": 2,
            "type": int,
            "default": None,
            "help": "Output image size",
            "metavar": ("LENGTH", "WIDTH")
        },
    ]

    def actual_command(self):
        conversion_data = {
            "input_folder": self.vargs["input"],
            "input_files": self.vargs["file"],
            "include_subdirectories": self.vargs["r"],
            "resize": self.vargs["resize"],
            "output_folder": self.vargs["FOLDER"]
        }

        # Make sure only one output format gets parsed
        if self.vargs["format"]:
            conversion_data["output_format"] = self.vargs["format"][0]
        else:
            conversion_data["output_format"] = None

        Converter.convert(**conversion_data)


def main():
    ConversionTool().run()

if __name__ == '__main__':
    main()
