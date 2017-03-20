import copy
import junison
import pytest
from junison import Merger
from junison.merger import ObjectSetConflictHandler, ValueConflictHandler, \
    DefaultTo


def make_comparable_item(item):
    if isinstance(item, list):
        return sorted([make_comparable_item(i) for i in item])

    elif isinstance(item, dict):
        return sorted((k, make_comparable_item(v)) for k, v in item.items())

    else:
        return item


def test_simple_values_no_conflict_all_from_head():
    root = update = dict(
        a=5,
        a1=5.1,
        b='barbar',
        c=None,
        d=True,
        e='Not updated'
    )

    head = dict(
        a=6.5,
        a1=6.1,
        b='fubar',
        c='Not none',
        d=False,
        e='Not updated'
    )

    expected = copy.deepcopy(head)

    result = Merger().merge(root=root, head=head, update=update)
    assert result == expected
    assert result == head
    assert result is not head, 'Must be copy'


def test_simple_values_no_conflict_all_from_update():
    root = head = dict(
        a=5,
        a1=5.1,
        b='barbar',
        c=None,
        d=True,
        e='Not updated'
    )

    update = dict(
        a=6.5,
        a1=6.1,
        b='fubar',
        c='Not none',
        d=False,
        e='Not updated'
    )

    expected = copy.deepcopy(update)

    result = Merger().merge(root=root, head=head, update=update)
    assert result == expected
    assert result == update
    assert result is not update, 'Must be copy'


def test_simple_values_attribute_merges():
    root = dict(
        a=5,
        b='42'
    )

    update = copy.deepcopy(root)
    update['d'] = 'foo'
    head = copy.deepcopy(root)
    head['c'] = 'bar'

    result = Merger().merge(root=root, head=head, update=update)
    assert result == dict(
        a=5,
        b='42',
        d='foo',
        c='bar'
    )


def test_list_set_merges():
    root = dict(
        items=[
            {
                'id':   42,
                'data': 'value'
            },
            {
                'id':   '3',
                'data': 55
            },
            {
                'id':   'deleted in head',
                'data': 'deleted'
            },
            {
                'id':   'deleted in update',
                'data': 'deleted'
            },
            {
                'id':   'deleted in head and update',
                'data': 'deleted'
            }
        ],
        id='root'
    )

    head = dict(
        items=[
            {
                'id':   42,
                'data': 'value'
            },
            {
                'id':   '3',
                'data': False
            },
            {
                'id':   '55',
                'data': 'foo'
            },
            {
                'id':   'deleted in update',
                'data': 'updated in head'
            }
        ],
        id='head'
    )

    update = dict(
        items=[
            {
                'id':   '3',
                'data': '55'
            },
            {
                'id':   42,
                'data': 'value from update'
            },
            {
                'id':   '27',
                'data': 'bar'
            },
            {
                'id':   'deleted in head',
                'data': 'updated in update'
            }
        ],
        id='update'
    )

    result = Merger(
        list_conflict_handlers={
            'items': ObjectSetConflictHandler(id='id'),
        },
        value_conflict_handlers={
            'id': ValueConflictHandler(DefaultTo.HEAD)
        }
    ).merge(
        root=root,
        head=head,
        update=update
    )

    expected_items = [
        {'data': '55', 'id': '3'},
        {'data': 'value from update', 'id': 42},
        {'data': 'bar', 'id': '27'},
        {'data': 'foo', 'id': '55'},
        {
            'id':   'deleted in head',
            'data': 'updated in update'
        },
        {
            'id':   'deleted in update',
            'data': 'updated in head'
        }
    ]

    expected_items = make_comparable_item(expected_items)
    actual_items = make_comparable_item(result.pop('items'))
    assert result == {'id': 'head'}
    assert expected_items == actual_items


def test_list_set_merges_missing_id():
    head = dict(items=[
        {
            'id':   '3',
            'data': '55'
        },
    ])
    root = dict(items=[])
    update = dict(items=[
        {
            'wrong_id': '3',
            'data':     '55'
        },
    ])

    try:
        result = Merger(list_conflict_handlers={
            'items': ObjectSetConflictHandler(id='id')
        }).merge(
            root=root,
            head=head,
            update=update)
    except ValueError:
        pass
    else:
        assert False, 'KeyError was not thrown!'


def test_simple_deletes():
    root = dict(
        items=[
            'root',
            'head',
            'update',
            42
        ]
    )

    head = dict(
        items=[
            'root',
            'head',
            42,
        ]
    )

    update = dict(
        items=[
            'root',
            'update',
            'added'
        ]
    )

    result = Merger().merge(
        root=root,
        head=head,
        update=update
    )

    assert result == {'items': ['root', 'added']}


def test_set_none():
    root = dict(
        items={}
    )

    head = dict(
        items={}
    )

    update = dict(
        items=None
    )

    result = Merger().merge(
        root=root,
        head=head,
        update=update
    )

    assert result == {'items': None}


def test_merge_list_and_dict():
    root = dict(
        items={}
    )

    head = dict(
        items=None
    )

    update=dict(
        items=[]
    )

    with pytest.raises(TypeError) as excinfo:
        Merger().merge(
            root=root,
            head=head,
            update=update
        )

    excinfo.match('Unable to merge')


def test_removed_attribute():
    root = dict(
        a='value for a',
        b='value for b'
    )

    head = dict(
        a='value for a'
    )

    update=dict(
        a='value for a',
        c='value for c'
    )

    m = Merger().merge(
        root=root,
        head=head,
        update=update
    )


def test_merger__type():
    m = Merger()
    with pytest.raises(TypeError) as e:
        m._type(lambda: 42)

    e.match('The value .* is not a JSON value')


def test_main():
    assert junison  # use your library here
