# coding=utf8


from fylr_lib_plugin_python3 import util as fylr_util, plugin_info_json
from link_once_modules import util

import json


def main():

    info_json = plugin_info_json.PluginCallbackInfo(util.PLUGIN_NAME)
    info_json.parse_from_stdin()

    # if there are transitions which need to be confirmed,
    # the same callback is executed multiple times.
    # this causes problems if the linked tan object is updated
    # in the first request, in later requests the "assigned" tag
    # is already set by the plugin and a error would be thrown.
    # the plugin must only check and update the tan object
    # if the query parameters suggest the requests are not
    # repeated requests during a 202 process.

    if util.is_in_202_process(info_json):
        fylr_util.return_empty_objects()

    # get the objects from the input data
    objects = info_json.get_object_list()
    if len(objects) == 0:
        fylr_util.return_empty_objects()

    # load the configuration and
    # check if the current objects are relevant
    main_objecttype = info_json.get_main_objecttype()

    # map: linked tan objecttypes -> (tag id (before), tag id (after))
    linked_settings = {}

    for s in info_json.get_list_from_plugin_config('tan_settings.linked_settings'):
        if main_objecttype != s.get('main_objecttype'):
            continue

        tan_ot = s.get('tan_objecttype')
        if not tan_ot:
            continue

        linked_settings[tan_ot] = (
            s.get('tag_before', 0),
            s.get('tag_after', 0),
        )

    if not linked_settings:
        fylr_util.return_empty_objects()

    # get the server urls
    external_url = info_json.get_external_url()
    if not external_url:
        fylr_util.return_error_response('info.external_url missing!')
    api_url = info_json.get_api_url()
    if not api_url:
        fylr_util.return_error_response('info.api_url missing!')

    # get a session token
    access_token = info_json.get_access_token()
    if not access_token:
        fylr_util.return_error_response('info.api_user_access_token missing!')

    updated_objects = []

    # iterate over the list of objects first and check if any linked tan object is linked multiple times
    # this can happen if the group edit mode is used for more than one object
    # this can not work, so return a special api error
    seen_linked_tan_objects = {}
    linked_tan_objects_by_object = {}
    idx = -1
    for obj in objects:
        idx += 1

        for tan_ot in linked_settings.keys():
            # check if any new tan object is linked

            current = obj.get('_current', {})
            if isinstance(current, list) and len(current) > 0:
                current = current[0].get(main_objecttype, {})
            if not isinstance(current, dict):
                current = {}
            new_linked_tan_objects = util.find_new_linked_tan_objects(
                obj=obj.get(main_objecttype, {}),
                current=current,
                tan_objecttype=tan_ot,
            )
            if len(new_linked_tan_objects) == 0:
                # nothing to do
                continue

            # check if the linked tan object was already seen in another object
            # => throw an api error
            if not tan_ot in seen_linked_tan_objects:
                seen_linked_tan_objects[tan_ot] = []

            for s in seen_linked_tan_objects[tan_ot]:
                for o in new_linked_tan_objects:
                    if s[2] == o[2]:  # ids match
                        fylr_util.return_error_response_with_parameters(
                            error=f'{util.PLUGIN_NAME}.error.duplicate_tan_object',
                            parameters={
                                'idx': idx,
                                'tan_objecttype': tan_ot,
                                'tan_obj_id': s[2],
                            },
                        )

            seen_linked_tan_objects[tan_ot] += new_linked_tan_objects

            # store the linked tan objects for each object to handle them in the next step
            sys_id_key = obj.get('_system_object_id')
            if not sys_id_key in linked_tan_objects_by_object:
                linked_tan_objects_by_object[sys_id_key] = {}
            if not tan_ot in linked_tan_objects_by_object[sys_id_key]:
                linked_tan_objects_by_object[sys_id_key][tan_ot] = []
            linked_tan_objects_by_object[sys_id_key][tan_ot] += new_linked_tan_objects

    idx = -1
    for obj in objects:
        idx += 1

        for tan_ot, tag_ids in linked_settings.items():

            # check if any tan object is linked

            sys_id_key = obj.get('_system_object_id')
            if not sys_id_key in linked_tan_objects_by_object:
                continue
            if not tan_ot in linked_tan_objects_by_object[sys_id_key]:
                continue

            new_linked_tan_objects = linked_tan_objects_by_object[sys_id_key][tan_ot]

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
            for linked_info in new_linked_tan_objects:

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
                    )

                    loaded_linked_object = {}
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
                                'idx': idx,
                                'tan_objecttype': linked_ot,
                                'tan_obj_id': linked_obj_id,
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
                                'tan_objecttype': linked_ot,
                                'tan_obj_id': linked_obj_id,
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

                    resp, statuscode = fylr_util.post_to_api(
                        api_url=f'{api_url}/api/v1',
                        path=f'db/{linked_ot}',
                        access_token=access_token,
                        payload=fylr_util.dumpjs(
                            [
                                updated_linked_object,
                            ]
                        ),
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
                                'idx': idx,
                                'tan_objecttype': linked_ot,
                                'tan_obj_id': linked_obj_id,
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
