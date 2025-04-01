# coding=utf8


import json
import os

from fylr_lib_plugin_python3 import util as fylr_util

from datetime import datetime


# -------------------------------------------

PLUGIN_NAME = 'fylr-plugin-linked-object-use-once'


# -------------------------------------------


def tmplog(lines: list, new_file: bool = False):
    fylr_util.write_tmp_file(
        f'{PLUGIN_NAME}.log',
        lines,
        new_file,
    )

    return
