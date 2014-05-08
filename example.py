#!/usr/bin/env python

from gsr import *
import argparse as ap

class OptionParser:
    def __init__(self):
        desc = "Gadget Snapshot Reader (GSR)"
        self.parser = ap.ArgumentParser(prog="GSR",
                                        description=desc,
                                        formatter_class=ap.RawTextHelpFormatter)

        # General options
        self.general_group = self.parser.add_argument_group("General options")
        self.add_general_options()

    def add_general_options(self):
        file_help = "Input filename"
        self.general_group.add_argument("-f",
                                        dest="fname",
                                        type=str,
                                        nargs="*",
                                        help=file_help,
                                        required=True)

    def get_options(self):
        return self.parser.parse_args()



if __name__ == '__main__':
    op = OptionParser().get_options()
    for f in op.fname:
        print("Processing snapshot", f,"...")
        snap = Snapshot(f)
        # snap.to_ascii()
        # snap.get_data_by_type(5)
        snap.print_data_by_type(5)
