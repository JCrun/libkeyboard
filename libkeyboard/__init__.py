# coding=utf8

"""
@Author: baicaimp3
@Date: 2024/11/08
"""

import sys
import time

if sys.platform == 'win32':
    from .keyboard.windows import KeyBoard
else:
    from .keyboard.linux import KeyBoard


def keyboard_write(text, delay=0.0):
    """
    Simulate typing text.
    :param text: String to type
    :param delay: Delay between keystrokes in seconds
    """
    with KeyBoard() as kb:
        for char in text:
            kb.press(char)
            kb.release(char)
            if delay > 0:
                time.sleep(delay)


def keyboard_group(*keys):
    """
    Simulate key combination (e.g. ctrl+c).
    :param keys: Sequence of keys to press together.
                 The last key is pressed and released while others are held down.
    """
    if not keys:
        return

    with KeyBoard() as kb:
        # Press modifiers/prefix keys
        for key in keys[:-1]:
            kb.press(key)
        
        # Press and release the final key
        kb.press(keys[-1])
        kb.release(keys[-1])
        
        # Release modifiers/prefix keys in reverse order
        for key in reversed(keys[:-1]):
            kb.release(key)
