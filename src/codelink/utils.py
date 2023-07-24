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


# Yields all values corresponding to a key (i.e. "UUID") in a nested dictionary
def find_key_values(state: dict, key: str) -> str:
    if isinstance(state, list):
        for i in state:
            for x in find_key_values(i, key):
                yield x

    elif isinstance(state, dict):
        if key in state:
            yield state[key]
        for j in state.values():
            for x in find_key_values(j, key):
                yield x


# Replaces all occurrences of old_value with new_value for a given key in a nested dictionary
def replace_key_values(state: dict, key: str, old_value: str, new_value: str) -> None:
    if isinstance(state, list):
        for i in state:
            replace_key_values(i, key, old_value, new_value)

    elif isinstance(state, dict):
        if key in state:
            if type(state[key]) is list and key == "Link":
                if state[key][0] == old_value:
                    state[key] = (new_value, state[key][1])
            elif type(state[key]) is list and key == "Framed Nodes UUID's":
                for idx, item in enumerate(state[key]):
                    if item == old_value:
                        state[key][idx] = new_value
            else:
                if state[key] == old_value:
                    state[key] = new_value

        for j in state.values():
            replace_key_values(j, key, old_value, new_value)
