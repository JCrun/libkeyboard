# coding=utf8

"""
@Author: baicaimp3
@Date: 2024/11/08
"""

from ._base import Key, KeyCode

# Define NORMAL_MODIFIERS
# This mapping is used to identify modifier keys and normalize them
NORMAL_MODIFIERS = {
    Key.alt: Key.alt,
    Key.alt_l: Key.alt_l,
    Key.alt_r: Key.alt_r,
    Key.alt_gr: Key.alt_gr,
    Key.ctrl: Key.ctrl,
    Key.ctrl_l: Key.ctrl_l,
    Key.ctrl_r: Key.ctrl_r,
    Key.shift: Key.shift,
    Key.shift_l: Key.shift_l,
    Key.shift_r: Key.shift_r,
    Key.cmd: Key.cmd,
    Key.cmd_l: Key.cmd_l,
    Key.cmd_r: Key.cmd_r
}
