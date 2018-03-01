#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

import argparse
import os

from tensorflow.python.tools import inspect_checkpoint as chkp

parser = argparse.ArgumentParser(description="Print data in tensorflow checkpoint file.")
parser.add_argument("global_step", help="global step of the checkpoint file to print")
parser.add_argument("-n", metavar="tensor_name", default="",
                    help="name of the tensor in the checkpoint file to print "
                         "or print all tensors if not provided.")
args = parser.parse_args()

file_name = os.path.join("logs", "solver-net-{}".format(args.global_step))
tensor_name = args.n
all_tensors = True if args.n == "" else False

chkp.print_tensors_in_checkpoint_file(file_name, tensor_name=tensor_name, all_tensors=all_tensors)
