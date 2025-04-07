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


# -------------------------------------------


def find_linked_tan_objects(
    obj: dict,
    tan_objecttype: str,
    found: list = None,
) -> list[str, str, int]:  # return list of tuples of objecttype, mask, object id
    if found is None:
        found = []

    for fieldname, fieldvalue in obj.items():
        if fieldname.startswith('_') and not fieldname.startswith('_nested:'):
            continue

        if isinstance(fieldvalue, dict):
            if fylr_util.get_json_value(fieldvalue, '_objecttype') == tan_objecttype:
                found.append(
                    (
                        tan_objecttype,
                        fylr_util.get_json_value(
                            fieldvalue, '_mask', default='_all_fields'
                        ),
                        fylr_util.get_json_value(
                            fieldvalue, f'{tan_objecttype}._id', default=0
                        ),
                    )
                )
                continue

            find_linked_tan_objects(fieldvalue, tan_objecttype, found)

        elif isinstance(fieldvalue, list):
            for el in fieldvalue:
                if isinstance(el, dict):
                    find_linked_tan_objects(el, tan_objecttype, found)

    return found


def incremented_linked_object(
    obj: dict,
    objecttype: str,
    tag_before: int = 0,
    tag_after: int = 0,
) -> dict:

    version = fylr_util.get_json_value(obj, f'{objecttype}._version', default=None)
    if not isinstance(version, int):
        return None

    new_obj = obj.copy()
    new_obj[objecttype]['_version'] = version + 1

    # if tags are given (id > 0) and the linked object has tags, replace tags
    old_tags = fylr_util.get_json_value(obj, '_tags', default=None)
    if not isinstance(old_tags, list):
        return new_obj

    new_tags = []

    # remove the "before" tag
    for tag in old_tags:
        if tag_before > 0:
            tag_id = tag.get('_id')
            if tag_id == tag_before:
                continue
        new_tags.append(tag)

    if tag_after > 0:
        new_tags.append(
            {
                '_id': tag_after,
            }
        )

    new_obj['_tags'] = new_tags

    return new_obj

