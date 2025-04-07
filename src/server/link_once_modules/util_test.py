import pytest
from . import util

# tests for find_linked_tan_objects()


def test_empty_dict():
    assert util.find_linked_tan_objects({}, 'tan_ot') == []


def test_no_matches():
    data = {
        'linked_tan': {
            '_objecttype': 'tan_ot',
            'tan_ot': {
                '_id': 123,
            },
        },
    }
    assert util.find_linked_tan_objects(data, 'other') == []


def test_match_in_top_level():
    data = {
        'linked_tan': {
            '_objecttype': 'tan_ot',
            'tan_ot': {
                '_id': 123,
            },
        },
    }
    assert util.find_linked_tan_objects(data, 'tan_ot') == [
        (
            'tan_ot',
            '_all_fields',
            123,
        )
    ]

    data = {
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
    }
    assert util.find_linked_tan_objects(data, 'tan_ot') == [
        (
            'tan_ot',
            'tan_ot_mask',
            123,
        )
    ]


def test_match_in_nested():
    data = {
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
    }
    assert util.find_linked_tan_objects(data, 'tan_ot') == [
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

