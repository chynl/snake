#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111

from datetime import datetime


def log(*msgs):
    msg_str = ""
    for msg in msgs:
        msg_str += str(msg)
    print("[%s]" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg_str)
