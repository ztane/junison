from enum import IntEnum
from numbers import Number
from typing import Union, Dict, List

import copy
from collections import OrderedDict


class MergeException(Exception):
    pass


UNDEFINED = object()
DELETE = object()

JSON = Union[
    Dict[str, 'JSON'],
    List['JSON'],
    int,
    float,
    str,
    bool,
    None
]


def _is_value_type(type):
    return type in {bool, Number, str, None, UNDEFINED}


class DefaultTo(IntEnum):
    HEAD = 0
    UPDATE = 1


class ValueConflictHandler:
    def __init__(self, default_to: DefaultTo = DefaultTo.UPDATE):
        self._default_to = default_to

    def merge(self, *, merger, path, root, head, update):
        return [head, update][self._default_to.value]


class ObjectSetConflictHandler:
    def __init__(self, id='id'):
        self._id_field = id

    @staticmethod
    def _merge_ordered_sets(list_a, list_b):
        """
        Merge two ordered set so that the ordering of list_b is retained
        and interleaved with those items appearing solely in list_a

        :param list_a: the first list
        :param list_b: the second list
        :return: the merged list
        """
        before = {}
        b_set = set(list_b)
        un_anchored = []
        for i in list_a:
            if i in b_set:
                before[i] = un_anchored
                un_anchored = []
            else:
                un_anchored.append(i)

        at_the_end = un_anchored
        result = []
        for i in list_b:
            result.extend(before.get(i, ()))
            result.append(i)

        result.extend(at_the_end)
        return result

    def merge(self, *, merger, path, root, head, update):
        def get_id(item):
            try:
                if isinstance(item, dict):
                    return item[self._id_field]

                else:
                    return item

            except KeyError:
                raise ValueError('{} doesn\'t have id field {}'
                                 .format(item, self._id_field))

        root_items = OrderedDict((get_id(item), item) for item in root)
        head_items = OrderedDict((get_id(item), item) for item in head)
        update_items = OrderedDict((get_id(item), item) for item in update)

        result_items = {}

        for i in root_items:
            if i not in head_items:
                if i not in update_items:
                    result_items[i] = DELETE

                elif update_items[i] == root_items[i]:
                    result_items[i] = DELETE
                else:
                    # ONE DELETED, other UPDATED, keep the updated!
                    # self.merger._add_conflict()
                    result_items[i] = copy.deepcopy(update_items[i])

            elif i not in update_items:
                # it is in head_items nevertheless. If there is no conflict,
                # remove, otherwise keep added

                if head_items[i] == root_items[i]:
                    result_items[i] = DELETE
                else:
                    result_items[i] = copy.deepcopy(head_items[i])

            else:
                # all 3 exist, do a merge.
                result_items[i] = merger._do_merge(
                    path=path,
                    root=root_items[i],
                    head=head_items[i],
                    update=update_items[i])

        for i in head_items:
            if i in result_items:
                continue

            # the item is new.
            if i in update_items:
                result_items[i] = merger._do_merge(
                    path=path,
                    root={},
                    head=head_items[i],
                    update=update_items[i]
                )

            else:
                result_items[i] = copy.deepcopy(head_items[i])

        for i in update_items:
            if i in result_items:
                continue

            # this is the only place where they now occurred
            result_items[i] = copy.deepcopy(update_items[i])

        actual_order = self._merge_ordered_sets(head_items, update_items)
        return [result_items[i]
                for i in actual_order
                if result_items[i] is not DELETE]


class DictMerger:
    def merge(self, *, merger, path, root, head, update):
        root_keys = set(root.keys())
        head_keys = set(head.keys())
        update_keys = set(update.keys())
        all_keys = root_keys | head_keys | update_keys

        result = {}

        for i in all_keys:
            value = merger._do_merge(
                path=path + (i,),
                root=root.get(i, UNDEFINED),
                head=head.get(i, UNDEFINED),
                update=update.get(i, UNDEFINED)
            )

            if value is not UNDEFINED:
                result[i] = value

        return result


def normalize_key(key):
    if isinstance(key, tuple):
        return key

    if isinstance(key, list):
        return tuple(key)

    if key == '':
        return ()

    return tuple(key.split('.'))


class Merger:
    _default_value_conflict_strategy = ValueConflictHandler()
    _default_list_conflict_strategy = ObjectSetConflictHandler()
    _default_dict_conflict_strategy = DictMerger()

    def __init__(
        self,
        list_conflict_handlers=None,
        value_conflict_handlers=None,
        default_value_conflict_handler=None,
        default_list_conflict_handler=None):
        """
        Initialize a new merger instance.
        """

        self._list_conflict_handlers = {
            normalize_key(key): value
            for (key, value)
            in (list_conflict_handlers or {}).items()
            }

        self._value_conflict_handlers = {
            normalize_key(key): value
            for (key, value)
            in (value_conflict_handlers or {}).items()
            }

        if default_value_conflict_handler is not None:
            self._default_value_conflict_strategy = \
                default_value_conflict_handler

        if default_list_conflict_handler is not None:
            self._default_list_conflict_strategy = default_list_conflict_handler

    def _copy(self, item):
        """
        Returns a copy of the given item. The sentinels are not copied but
        returned as is

        :param item: the item to be copied
        :return: a fresh deep copy (if necessary)
        """

        return copy.deepcopy(item)

    def _type(self, inst):
        if isinstance(inst, bool):
            return bool
        if isinstance(inst, Number):
            return Number
        if isinstance(inst, str):
            return str
        if isinstance(inst, (list, tuple)):
            return list
        if isinstance(inst, dict):
            return dict
        if inst is None:
            return None
        if inst is UNDEFINED:
            return UNDEFINED

        raise TypeError('The value {!r} is not a JSON value'.format(inst))

    def _get_merge_algorithm(self, *, path, rtype, htype, utype):
        if _is_value_type(rtype) and _is_value_type(htype) and _is_value_type(
            utype):
            return self._value_conflict_handlers.get(
                path,
                self._default_value_conflict_strategy
            )

        if rtype in (dict, UNDEFINED) and htype in (dict, UNDEFINED) and utype \
            in (dict, UNDEFINED):
            return self._default_dict_conflict_strategy

        if rtype in (list, UNDEFINED) and htype in (list, UNDEFINED) and utype \
            in (list, UNDEFINED):
            return self._list_conflict_handlers.get(
                path,
                self._default_list_conflict_strategy
            )

        raise TypeError('Unable to merge types root={}, head={}, update={}'
                        .format(rtype, htype, utype))

    def _do_merge(self,
                  *,
                  path,
                  root: JSON,
                  head: JSON,
                  update: JSON) -> JSON:
        if root == head:
            return self._copy(update)

        if root == update:
            return self._copy(head)

        merger = self._get_merge_algorithm(
            path=path,
            rtype=self._type(root),
            htype=self._type(head),
            utype=self._type(update))

        return merger.merge(merger=self,
                            path=path,
                            root=root,
                            head=head,
                            update=update)

    def merge(
        self,
        *,
        root: JSON,
        head: JSON = UNDEFINED,
        update: JSON) -> JSON:
        """
        Perform a 3-way merge, using the given root, head and update.

        :param root:
        :param head:
        :param update:
        :return:
        """

        return self._do_merge(
            path=(),
            root=root,
            head=head,
            update=update
        )
