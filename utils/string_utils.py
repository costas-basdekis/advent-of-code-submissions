from typing import Iterable, List

from .math_utils import min_and_max


__all__ = ["join_multiline", "pad_lines", "pad_multiline"]


def join_multiline(
    separator: str, items: Iterable[str], filler: str = " ",
) -> str:
    """
    >>> join_multiline("", [])
    ''
    >>> join_multiline("", ["a\\nb\\nc"])
    'a\\nb\\nc'
    >>> join_multiline("x\\nx\\nx", ["a\\nb\\nc", "d"])
    'axd\\nbx \\ncx '
    >>> join_multiline("x\\nx\\nx", ["a\\nb\\nc", "\\n\\nd"])
    'ax \\nbx \\ncxd'
    >>> join_multiline("x\\nx\\nx", ["\\n\\nd", "a\\nb\\nc"])
    ' xa\\n xb\\ndxc'
    """
    items = iter(items)
    total_lines = []
    separator_lines = []
    for item in items:
        total_lines = pad_lines(item.splitlines())
        separator_lines = pad_lines(separator.splitlines())
        break
    for item in items:
        item_lines = item.splitlines()
        new_line_count = \
            max((len(total_lines), len(separator_lines), len(item_lines)))
        if len(total_lines) < new_line_count:
            total_lines += [""] * (new_line_count - len(total_lines))
        if len(separator_lines) < new_line_count:
            separator_lines += [""] * (new_line_count - len(separator_lines))
        if len(item_lines) < new_line_count:
            item_lines += [""] * (new_line_count - len(item_lines))
        total_lines = [
            "".join(line_tuple)
            for line_tuple in zip(
                pad_lines(total_lines, filler=filler),
                pad_lines(separator_lines, filler=filler),
                pad_lines(item_lines, filler=filler),
            )
        ]
    return "\n".join(total_lines)


def pad_lines(lines: List[str], filler: str = " ") -> List[str]:
    if not lines:
        return lines
    min_length, max_length = min_and_max(map(len, lines))
    if min_length == max_length:
        return lines
    return [
        line.ljust(max_length, filler)
        for line in lines
    ]


def pad_multiline(item: str, filler: str = " ") -> str:
    """
    >>> pad_multiline("")
    ''
    >>> pad_multiline("abc")
    'abc'
    >>> pad_multiline("abc\\n")
    'abc\\n   '
    >>> pad_multiline("abc\\ndef")
    'abc\\ndef'
    >>> pad_multiline("abc\\nd")
    'abc\\nd  '
    >>> pad_multiline("a\\ndef")
    'a  \\ndef'
    >>> pad_multiline("abc\\ndef\\n")
    'abc\\ndef\\n   '
    >>> pad_multiline("abc\\n\\nghi")
    'abc\\n   \\nghi'
    >>> pad_multiline("\\ndef\\nghi")
    '   \\ndef\\nghi'
    """
    if not item:
        return item
    return "\n".join(pad_lines(item.split("\n"), filler=filler))
