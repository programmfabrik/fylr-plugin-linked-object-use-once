# coding=utf8


from fylr_lib_plugin_python3 import util as fylr_util
from link_once_modules import util

import json
import sys


def main():

    orig_data = json.loads(sys.stdin.read())
    util.tmplog(
        [
            fylr_util.dumpjs(orig_data),
        ],
        new_file=True,
    )

    # get the objects from the input data
    objects = fylr_util.get_json_value(orig_data, 'objects')
    if not isinstance(objects, list):
        fylr_util.return_empty_objects()
    if len(objects) < 1:
        fylr_util.return_empty_objects()

    # get a session token
    access_token = fylr_util.get_json_value(orig_data, 'info.api_user_access_token')
    if access_token is None:
        fylr_util.return_error_response('info.api_user_access_token missing!')

    updated_objects = []
    idx = -1
    for obj in objects:
        idx += 1

        # todo

        updated_objects.append(obj)

    fylr_util.return_response(
        {
            'objects': updated_objects,
        }
    )


if __name__ == '__main__':
    main()
