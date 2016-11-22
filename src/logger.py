"""
 Created by waldo on 11/22/16
"""

__author__ = "waldo"
__project__ = "BatchConvert"

output_log = '/media/waldo/DATA-SHARE/Code/BatchConvert/output/output.log'


def write_log(message='', mode='a'):
    print message
    with open(output_log, mode) as log:
        log.write(message + '\n')
