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
            '----------------------------',
        ],
        new_file=True,
    )

    # get the objects from the input data
    objects = orig_data.get('objects', [])
    if len(objects) == 0:
        fylr_util.return_empty_objects()

    # load the configuration and
    # check if the current objects are relevant
    main_objecttype = objects[0].get('_objecttype')

    # map: linked tan objecttypes -> (tag id (before), tag id (after))
    linked_settings = {}

    for s in fylr_util.get_json_value(
        orig_data,
        'info.config.plugin.fylr-plugin-linked-object-use-once.config.tan_settings.linked_settings',
        default=[],
    ):
        if main_objecttype != s.get('main_objecttype'):
            continue

        tan_ot = s.get('tan_objecttype')
        if not tan_ot:
            continue

        linked_settings[tan_ot] = (
            s.get('tag_before', 0),
            s.get('tag_after', 0),
        )

    if len(linked_settings) == 0:
        fylr_util.return_empty_objects()

    # get the server urls
    external_url = fylr_util.get_json_value(
        orig_data,
        'info.external_url',
    )
    if not external_url:
        fylr_util.return_error_response('info.external_url missing!')

    api_url = fylr_util.get_json_value(
        orig_data,
        'info.api_url',
    )
    if not api_url:
        fylr_util.return_error_response('info.api_url missing!')

    # get a session token
    access_token = fylr_util.get_json_value(
        orig_data,
        'info.api_user_access_token',
    )
    if not access_token:
        fylr_util.return_error_response('info.api_user_access_token missing!')

    updated_objects = []
    idx = -1
    for obj in objects:
        idx += 1

        for tan_ot, tag_ids in linked_settings.items():

            # check if any tan object is linked
            linked_tan_objects = util.find_linked_tan_objects(
                obj=obj.get(main_objecttype, {}),
                tan_objecttype=tan_ot,
            )
            if len(linked_tan_objects) == 0:
                # nothing to do
                continue

            # check if there is a tag before and after configured => use this to create a tagfilter
            # if the linked tan object does not match the tagfilter for a free object,
            # this means the linked object was already linked in another object
            # => throw an api error

            tagfilter = fylr_util.TagFilter()
            tagfilter_def = {}
            if tag_ids[0] > 0:
                # linked tan object has the "before" tag and any other tags
                tagfilter_def['any'] = [tag_ids[0]]
            if tag_ids[1] > 0:
                # linked tan object does not have the "after" tag
                tagfilter_def['not'] = [tag_ids[1]]

            tagfilter.parse(tagfilter_def)
            if tagfilter.is_empty():
                # OK, no need to check
                continue

            # the linked tan object(s) have not been linked before
            # they need to be marked as assigned by changing the tags
            for linked_info in linked_tan_objects:

                linked_ot = linked_info[0]
                linked_mask = linked_info[1]
                linked_obj_id = linked_info[2]

                tries = 0
                max_tries = 3
                while tries < max_tries:
                    tries += 1

                    # load the current version of the linked object
                    # and post an updated version of the object (version+1)
                    # if it fails, check if the linked tan object was linked in the meantime
                    # try to repeat the update of the linked object

                    resp, statuscode = fylr_util.get_from_api(
                        api_url=f'{api_url}/api/v1',
                        path=f'db/{linked_ot}/{linked_mask}/{linked_obj_id}?format=long',
                        access_token=access_token,
                        log_in_tmp_file=True,
                    )
                    util.tmplog(
                        [
                            'linked_tan_object: get',
                            statuscode,
                            resp,
                        ],
                    )

                    loaded_linked_object = None
                    try:
                        if statuscode != 200:
                            # could not load linked object -> api error
                            raise Exception('statuscode != 200')

                        obj_js = json.loads(resp)
                        if not isinstance(obj_js, list) or len(obj_js) < 1:
                            raise Exception('expect result as non-empty array')

                        loaded_linked_object = obj_js[0]

                    except Exception as e:
                        fylr_util.return_error_response_with_parameters(
                            error=f'{util.PLUGIN_NAME}.error.could_not_load_tan_object',
                            parameters={
                                'msg': str(e),
                                'statuscode': statuscode,
                                'response': resp,
                            },
                        )

                    if not tagfilter.match(loaded_linked_object.get('_tags', [])):
                        fylr_util.return_error_response_with_parameters(
                            error=f'{util.PLUGIN_NAME}.error.tan_object_already_linked',
                            parameters={
                                'idx': idx,
                                'tan_objecttype': tan_ot,
                                'tan_obj_sysid': fylr_util.get_json_value(
                                    loaded_linked_object,
                                    '_system_object_id',
                                    default=0,
                                ),
                                'tan_obj_id': fylr_util.get_json_value(
                                    loaded_linked_object,
                                    f'{tan_ot}._id',
                                    default=0,
                                ),
                            },
                        )

                    updated_linked_object = util.incremented_linked_object(
                        obj=loaded_linked_object,
                        objecttype=linked_ot,
                        tag_before=tag_ids[0],
                        tag_after=tag_ids[1],
                    )
                    if not updated_linked_object:
                        # xxx exception? ignore?
                        continue

                    util.tmplog(
                        [
                            'updated linked_tan_object:',
                            fylr_util.dumpjs(updated_linked_object),
                        ],
                    )

                    resp, statuscode = fylr_util.post_to_api(
                        api_url=f'{api_url}/api/v1',
                        path=f'db/{linked_ot}',
                        access_token=access_token,
                        payload=fylr_util.dumpjs(
                            [
                                updated_linked_object,
                            ]
                        ),
                        log_in_tmp_file=True,
                    )
                    util.tmplog(
                        [
                            'linked_tan_object: post',
                            statuscode,
                            resp,
                        ],
                    )

                    if statuscode == 200:
                        # update was successful, nothing else to do
                        break

                    # there was an api error
                    # if it is a version mismatch, it is possible that the linked tan object was updated in the meantime
                    # check if it still matches the "free" tagfilter, then update it again
                    # else it can not be linked, throw an api error
                    try:
                        error_js = json.loads(resp)
                        code = error_js.get('code')
                        if code != 'VersionMismatch':
                            raise Exception(code)

                    except Exception as e:
                        fylr_util.return_error_response_with_parameters(
                            error=f'{util.PLUGIN_NAME}.error.could_not_update_tan_object',
                            parameters={
                                'msg': str(e),
                                'statuscode': statuscode,
                                'response': resp,
                            },
                        )

        updated_objects.append(obj)

    fylr_util.return_response(
        {
            'objects': updated_objects,
        }
    )


if __name__ == '__main__':
    main()
