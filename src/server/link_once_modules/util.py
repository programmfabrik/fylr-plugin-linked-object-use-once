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


def __find_linked_tan_objects(
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

            __find_linked_tan_objects(fieldvalue, tan_objecttype, found)

        elif isinstance(fieldvalue, list):
            for el in fieldvalue:
                if isinstance(el, dict):
                    __find_linked_tan_objects(el, tan_objecttype, found)

    return found


def find_new_linked_tan_objects(
    obj: dict,
    current: dict,
    tan_objecttype: str,
) -> list[str, str, int]:  # return list of tuples of objecttype, mask, object id

    tmplog(
        [
            'find_new_linked_tan_objects',
            'obj:',
            fylr_util.dumpjs(obj),
            'current:',
            fylr_util.dumpjs(current),
        ]
    )

    # collect the linked objects in the new (not yet saved) object
    linked_objects = __find_linked_tan_objects(
        obj=obj,
        tan_objecttype=tan_objecttype,
    )
    tmplog(
        [
            'find_new_linked_tan_objects',
            '=> linked_objects:',
            fylr_util.dumpjs(linked_objects),
        ]
    )
    if len(linked_objects) == 0:
        # no linked objects in the new object version -> nothing to do
        return linked_objects

    # if the current version is not null (the object was updated), also collect these linked objects
    if not isinstance(current, dict):
        # no current version -> all are new
        return linked_objects

    cur_linked_objects = __find_linked_tan_objects(
        obj=current,
        tan_objecttype=tan_objecttype,
    )
    tmplog(
        [
            'find_new_linked_tan_objects',
            '=> cur_linked_objects:',
            fylr_util.dumpjs(cur_linked_objects),
        ]
    )
    if len(cur_linked_objects) == 0:
        # only new linked objects in the new object version -> nothing to do
        return linked_objects

    # filter out all linked objects that are in both lists, only the new linked objects are relevant
    new_linked_objects = []

    for lo in linked_objects:
        if lo in cur_linked_objects:
            continue
        new_linked_objects.append(lo)

    return new_linked_objects


def incremented_linked_object(
    obj: dict,
    objecttype: str,
    tag_before: int = 0,
    tag_after: int = 0,
) -> dict:

    version = fylr_util.get_json_value(obj, f'{objecttype}._version', default=None)
    if not isinstance(version, int):
        return None

    new_obj = {}
    for k in obj:
        if k in [
            '_acl',
            '_best_mask',
            '_collections',
            '_comment',
            '_generated_rights',
            '_mask_display_name',
            '_objecttype_display_name',
        ]:
            continue
        new_obj[k] = obj[k]

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
