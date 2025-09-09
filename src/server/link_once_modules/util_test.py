from fylr_lib_plugin_python3 import plugin_info_json
from . import util

# tests for find_linked_tan_objects()


def test_empty_dict():
    assert (
        util.__find_linked_tan_objects(
            obj={},
            tan_objecttype='tan_ot',
            found=[],
        )
        == []
    )


def test_no_matches():
    assert (
        util.__find_linked_tan_objects(
            obj={
                'linked_tan': {
                    '_objecttype': 'tan_ot',
                    'tan_ot': {
                        '_id': 123,
                    },
                },
            },
            tan_objecttype='other',
            found=[],
        )
        == []
    )


def test_match_in_top_level():
    assert util.__find_linked_tan_objects(
        obj={
            'linked_tan': {
                '_objecttype': 'tan_ot',
                'tan_ot': {
                    '_id': 123,
                },
            },
        },
        tan_objecttype='tan_ot',
        found=[],
    ) == [
        (
            'tan_ot',
            '_all_fields',
            123,
        )
    ]

    assert util.__find_linked_tan_objects(
        obj={
            'linked_tan': {
                '_tags': [
                    {
                        '_id': 1,
                    },
                    {
                        '_id': 2,
                    },
                ],
                '_objecttype': 'tan_ot',
                '_mask': 'tan_ot_mask',
                'tan_ot': {
                    '_id': 123,
                },
            },
        },
        tan_objecttype='tan_ot',
        found=[],
    ) == [
        (
            'tan_ot',
            'tan_ot_mask',
            123,
        )
    ]


def test_match_in_nested():
    assert util.__find_linked_tan_objects(
        obj={
            '_nested:main_ot__tans': [
                {
                    'linked_tan': {
                        '_mask': 'mask_1',
                        '_objecttype': 'tan_ot',
                        'tan_ot': {
                            '_id': 123,
                        },
                    },
                },
                {
                    'linked_tan': {
                        '_objecttype': 'tan_ot',
                        'tan_ot': {
                            '_id': 45,
                        },
                    },
                },
            ]
        },
        tan_objecttype='tan_ot',
        found=[],
    ) == [
        (
            'tan_ot',
            'mask_1',
            123,
        ),
        (
            'tan_ot',
            '_all_fields',
            45,
        ),
    ]


def test_match_in_deep_nested():
    assert util.__find_linked_tan_objects(
        obj={
            '_nested:main_ot__nested_level_1': [
                {
                    '_nested:main_ot__nested_level_1__nested_level_2': [
                        {
                            '_nested:main_ot__nested_level_1__nested_level_2__nested_level_3': [
                                {
                                    'linked_tan': {
                                        '_mask': 'mask_1',
                                        '_objecttype': 'tan_ot',
                                        'tan_ot': {
                                            '_id': 123,
                                        },
                                    },
                                },
                                {
                                    'linked_tan': {
                                        '_objecttype': 'tan_ot',
                                        'tan_ot': {
                                            '_id': 45,
                                        },
                                    },
                                },
                            ]
                        },
                    ]
                },
            ]
        },
        tan_objecttype='tan_ot',
        found=[],
    ) == [
        (
            'tan_ot',
            'mask_1',
            123,
        ),
        (
            'tan_ot',
            '_all_fields',
            45,
        ),
    ]


def test_is_in_202_process():
    info_json = plugin_info_json.PluginCallbackInfo(plugin_name=util.PLUGIN_NAME)

    info_json.parse(
        raw_info_json="""
            {
                "info": {
                    "request": {
                        "query": {
                            "confirmTransition": [
                                "78f27eca682f76ff2b05196c14345b31"
                            ]
                        }
                    }
                }
            }
        """
    )
    assert util.is_in_202_process(info_json)

    info_json.parse(
        raw_info_json="""
            {
                "info": {
                    "request": {
                        "query": {
                            "confirmTransition": [
                                "SKIP"
                            ]
                        }
                    }
                }
            }
        """
    )
    assert not util.is_in_202_process(info_json)

    info_json.parse(
        raw_info_json="""
            {
                "info": {
                    "request": {
                        "query": {
                            "confirmTransition": [
                                "ALL"
                            ]
                        }
                    }
                }
            }
        """
    )
    assert not util.is_in_202_process(info_json)

    info_json.parse(
        raw_info_json="""
            {
                "info": {
                    "request": {
                        "query": {
                            "confirmTransition": []
                        }
                    }
                }
            }
        """
    )
    assert not util.is_in_202_process(info_json)

    info_json.parse(
        raw_info_json="""
            {
                "info": {
                    "request": {
                        "query": {}
                    }
                }
            }
        """
    )
    assert not util.is_in_202_process(info_json)
