from __future__ import annotations
from collections.abc import Iterable
from typing import Callable

import awkward as ak
import PySide2.QtGui as QtGui


def crop_text(text: str = "Test", width: float = 30, font: QtGui.QFont = QtGui.QFont()) -> str:
    font_metrics: QtGui.QFontMetrics = QtGui.QFontMetrics(font)

    cropped_text: str = "..."
    string_idx: int = 0
    while all([font_metrics.horizontalAdvance(cropped_text) < width - font_metrics.horizontalAdvance("..."),
               string_idx < len(text)]):
        cropped_text = cropped_text[:string_idx] + text[string_idx] + cropped_text[string_idx:]
        string_idx += 1

    if string_idx == len(text):
        cropped_text: str = cropped_text[:len(text)]

    return cropped_text


def flatten(nested_list: Iterable) -> Iterable:
    """Flattens an arbitrary nested iterable.

    This function flattens an arbitrary nested list by concatenating all nested items.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :return: Flat list
    :rtype: Iterable
    """

    flattened: list = []
    for item in nested_list:
        if isinstance(item, Iterable):
            flattened.extend(flatten(item))
        else:
            flattened.append(item)
    return flattened


def simplify(nested_list: Iterable) -> Iterable:
    """Simplifies an arbitrary nested iterable to the minimal nesting level.

    Flattens an iterable, but it leaves a minimal nesting. This is i.e. for vector sockets, where one usually does
    not want to concatenate coordinates of different vectors into a flat list.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :return: Simplified list of iterables
    :rtype: Iterable
    """

    res: list = []

    copy: list = nested_list[:]
    while copy:
        entry: list = copy.pop()
        if isinstance(entry, Iterable):
            if len(list(entry)) > 0 and not all([isinstance(i, Iterable) for i in entry]):
                res.append(entry)
            else:
                copy.extend(entry)
        else:
            res.append(entry)

    res.reverse()
    return res


def graft(nested_list: Iterable) -> Iterable:
    """Grafts each atomic element into its own list.

    This function adds a level of nesting by inserting each atomic object of an iterable into its own list.
    This function considers vectors with three components as atomic objects, so it encloses each vector into a separate
    iterable.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :return: Grafted list
    :rtype: Iterable
    """

    if isinstance(nested_list, Iterable):
        if len(list(nested_list)) == 3 and all([isinstance(i, float) for i in nested_list]):
            # Vectors with three components
            return [nested_list]
        else:
            temp_list: list = []
            for sub_list in nested_list:
                temp_list.append(graft(sub_list))
            return temp_list
    else:
        # Default atomic item, i.e. int, float, str, ...
        return [nested_list]


def graft_topology(nested_list: Iterable) -> Iterable:
    """Grafts each atomic element (lists of nesting level 1) into its own list.

    This function basically performs a graft operation, that considers lists with a nesting level 1 as atomic objects.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :return: Grafted list
    :rtype: Iterable
    """

    if isinstance(nested_list, Iterable):
        if not all([isinstance(i, Iterable) for i in nested_list]):
            # Nesting level 1
            return [nested_list]
        else:
            temp_list: list = []
            for sub_list in nested_list:
                temp_list.append(graft_topology(sub_list))
            return temp_list
    else:
        # Default atomic item, i.e. int, float, str, ...
        return nested_list


def unwrap(nested_list: Iterable) -> Iterable:
    """Unwraps a nested iterable.

    This function removes one pair of square brackets from a nested list if possible.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :return: Unwrapped list
    :rtype: Iterable
    """

    return list(nested_list)[0] if len(list(nested_list)) == 1 else nested_list


def wrap(nested_list: Iterable) -> Iterable:
    """Wraps a nested iterable.

    This function adds one pair of square brackets to a nested list.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :return: Unwrapped list
    :rtype: Iterable
    """

    return [nested_list]


def map_objects(nested_list: Iterable, object_type: type, callback: Callable) -> Iterable:
    """Applies a callback function to each data_type item of a nested input list.

    This function creates a list with evaluated data_type objects and the nested structure of the input list.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :param object_type: Only elements with this data type are evaluated by the callback function.
    :type object_type: type
    :param callback: Function that performs some action to each data_type element.
    :type callback: 'function'
    :return: Nested list with evaluated data_type objects.
    :rtype: Iterable
    """

    if isinstance(nested_list, list):
        temp_list: list = []
        for sub_list in nested_list:
            temp_list.append(map_objects(sub_list, object_type, callback))
        return temp_list
    else:
        if isinstance(nested_list, object_type):
            return callback(nested_list)


def map_last_level(nested_list: Iterable, object_type: type, callback: Callable) -> Iterable:
    """Applies a callback function to every penultimate level of a nested list.

    This function evaluates every penultimate level of a list containing only object_type elements with the specified
    callback function and returns a list with the nested structure of the input list.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :param object_type: Only penultimate list levels contain object_type items are evaluated
    :type object_type: type
    :param callback: Function that performs some action to each penultimate list level
    :type callback: 'function'
    :return: Nested list with evaluated penultimate list levels
    :rtype: Iterable
    """

    if isinstance(nested_list, list):
        if all([isinstance(elem, object_type) for elem in nested_list]):
            return callback(nested_list)
        else:
            temp_list: list = []
            for sub_list in nested_list:
                temp_list.append(map_last_level(sub_list, object_type, callback))
            return temp_list


def broadcast_data_tree(*socket_inputs: Iterable) -> Iterable:
    """Broadcast any number of socket inputs against each other.

    Like NumPy's broadcast_arrays function, this function returns the socket inputs, duplicating elements if necessary
    so that the socket inputs can be combined element by element. This replaces individual elements of the socket inputs
    with element arrays and increases the dimension.

    :param socket_inputs: Arbitrary nested socket inputs
    :type socket_inputs: Iterable
    :return: Broadcasted zipped socket inputs as list of tuples
    :rtype: Iterable
    """

    flatten_inputs: list = [flatten(socket_input) for socket_input in socket_inputs]
    nested_idx_trees: list = []
    for idx, socket_input in enumerate(socket_inputs):
        nested_idx_trees.append(map_objects(socket_input, object, lambda obj: flatten_inputs[idx].index(obj)))

    broadcasted_idx_trees: list = ak.broadcast_arrays(*nested_idx_trees)
    broadcasted_idx_zip: list = ak.zip(broadcasted_idx_trees).tolist()

    # Transforms index tuple to socket input value tuple
    def index_to_obj(idx_tuple: tuple) -> tuple:
        return tuple([flatten_inputs[input_idx][input_elem] for input_idx, input_elem in enumerate(idx_tuple)])

    broadcasted_input_zip: Iterable = map_objects(broadcasted_idx_zip, tuple, index_to_obj)
    return broadcasted_input_zip


def traverse_tuples(nested_list: Iterable) -> Iterable:
    """Generator to yield every tuple within an arbitrary nested iterable.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :return: Tuple item.
    :rtype: Iterable
   """

    if isinstance(nested_list, list):
        for sub_list in nested_list:
            yield from traverse_tuples(sub_list)
    else:
        if isinstance(nested_list, tuple):
            yield nested_list


class ListWrapper:
    """Wrapper for lists.

    This simple class can be used to wrap lists into non-iterable objects to be treated as atomic, non-decomposable
    elements in array broadcasting (many-to-one relationship).

     Attributes:
        wrapped_data (list): Wrapped list
    """
    def __init__(self, wrapped_data: list):
        self.wrapped_data: list = wrapped_data
