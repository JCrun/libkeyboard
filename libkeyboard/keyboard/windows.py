# coding=utf8
"""
@Author: baicaimp3 (windows port)
@Date: 2025/10/11
Simulated keyboard implementation under Windows.
Keeps function names and calling methods consistent with the original Xlib version.
"""

import ctypes
import contextlib
import time
from ctypes import wintypes
from ..keyboard import Key, NORMAL_MODIFIERS
from .keyboard_mapping_win import keyboardMapping as kmp

# Win32 Constants
USER32 = ctypes.windll.user32

# INPUT structure and substructure definitions
PUL = ctypes.POINTER(ctypes.c_ulong)


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", PUL),
    ]


class INPUT_union(ctypes.Union):
    _fields_ = [
        ("ki", KEYBDINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_union)
    ]


# flags
INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

# useful VK
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt
VK_LWIN = 0x5B
VK_RMENU = 0xA5  # AltGr (often VK_RMENU)
# helper to send input


def _send_vk(vk, is_keyup):
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    flags = 0
    if is_keyup:
        flags |= KEYEVENTF_KEYUP
    inp.union.ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=flags, time=0, dwExtraInfo=None)
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))


def _send_unicode(ch, is_keyup):
    """Send unicode character (fallback)"""
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    flags = KEYEVENTF_UNICODE
    if is_keyup:
        flags |= KEYEVENTF_KEYUP
    inp.union.ki = KEYBDINPUT(wVk=0, wScan=ord(ch), dwFlags=flags, time=0, dwExtraInfo=None)
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))


class KeyBoard:
    """
    KeyBoard class implemented for Windows.
    Method names and behaviors are consistent with the Xlib version for easy replacement.
    """

    def __init__(self):
        # Windows does not need a Display object, but retains the same attributes
        self.min_keycode = 0
        self.max_keycode = 0xFF
        self.count = self.max_keycode - self.min_keycode + 1
        # Event type placeholder (different from Xlib, retaining attribute names)
        self.press_event = 'keydown'
        self.release_event = 'keyup'
        self.ctrl_press = 'keydown'
        self.ctrl_release = 'keyup'
        self.register_mapping = {}      # {keysym: {keycode: 1, keyidx: 0}} Registered keyboard mapping table (logical record)
        self.event_mapping = {}         # {keysym: {keycode: 1, keyidx: 0, count: 1}} Number of times pressed
        self.modifiers = set()
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        try:
            if not self.closed:
                self.close()
        except Exception:
            pass

    def key_to_keysym(self, key):
        """Keep original method signature: return (_key, keysym).
        On Windows, we agree that keysym is a virtual key code (VK) or unicode ordinal (>0xFFFF used as unicode)."""
        _key = None
        keysym = None
        if key.lower() in ('ps', 'printscreen', 'print screen'):
            key = 'print_screen'
        if hasattr(Key, key.lower()):
            _key = getattr(Key, key.lower()).value
            # Assume value has vk field or is VK
            try:
                keysym = _key.vk
            except Exception:
                # Compatibility: if value itself is int
                keysym = int(_key)
        elif key in ("\n", "\r"):
            _key = Key.enter.value
            try:
                keysym = _key.vk
            except Exception:
                keysym = int(_key)
        elif key == "\t":
            _key = Key.Tab.value
            try:
                keysym = _key.vk
            except Exception:
                keysym = int(_key)
        elif key.lower() in {'win', 'cmd', 'winleft'}:
            try:
                keysym = Key.cmd.value.vk
                _key = Key.cmd.value
            except Exception:
                keysym = VK_LWIN
                _key = None
        elif key in kmp:
            # kmp should store Windows VK or scan code, return directly
            keysym = kmp.get(key)
            _key = None
        elif len(key) != 1:
            self.pro_raise(Exception("Character length must be 1"))
        else:
            # Return unicode ordinal for using KEYEVENTF_UNICODE path
            keysym = ord(key)
            _key = None
        return _key, keysym

    def _update_modifiers(self, key, is_press):
        """Record when key is ctrl, shift, alt. key here is Key.x.value (or similar)."""
        # Use NORMAL_MODIFIERS mapping to maintain consistency
        if NORMAL_MODIFIERS.get(key, None):
            if is_press:
                self.modifiers.add(key)
            else:
                try:
                    self.modifiers.remove(key)
                except KeyError:
                    pass

    def press(self, key, register=False):
        """
        Press a key
        :param key: Keyboard key
        :param register: Keep consistent with Xlib version interface, but Windows does not need dynamic registration. Only true when writing Chinese.
        """
        _key, keysym = self.key_to_keysym(key)
        if _key is not None:
            self._update_modifiers(_key, True)

        # kmp hotkeys first
        if kmp.get(key) is not None:
            vk = kmp.get(key)
            # Determine if shift is needed (consistent with original logic)
            needshift = True if (len(key) == 1 and key.isupper()) or key in '~!@#$%^&*()_+{}|:"<>?' else False
            if needshift:
                _send_vk(VK_SHIFT, False)
            # Send press
            if isinstance(vk, int):
                _send_vk(int(vk), False)
            else:
                # If mapping returns string or unicode
                if isinstance(vk, str) and len(vk) == 1:
                    _send_unicode(vk, False)
                else:
                    try:
                        _send_vk(int(vk), False)
                    except Exception:
                        _send_unicode(str(vk), False)
            if needshift:
                _send_vk(VK_SHIFT, True)
            keycode = vk
            keyidx = 0
        else:
            # If keysym <= 0xFFFF and not printable VK, treat as VK, else use unicode
            if isinstance(keysym, int) and keysym <= 0xFF:
                # treat as VK
                keycode = keysym
                keyidx = 0
                _send_vk(keycode, False)
            elif isinstance(keysym, int) and keysym <= 0xFFFF:
                # May be ASCII/unicode ordinal, send using unicode
                keycode = keysym
                keyidx = 0
                _send_unicode(chr(keysym), False)
            else:
                # Fallback: try converting to int vk, otherwise treat as unicode char
                try:
                    vk = int(keysym)
                    keycode = vk
                    keyidx = 0
                    _send_vk(vk, False)
                except Exception:
                    # unicode fallback
                    ch = chr(keysym) if isinstance(keysym, int) else str(keysym)
                    keycode = ord(ch[0])
                    keyidx = 0
                    _send_unicode(ch[0], False)

        self.sync()
        # Record event
        if keysym in self.event_mapping:
            self.event_mapping[keysym]['count'] += 1
        else:
            self.event_mapping[keysym] = {"keycode": keycode, "keyidx": keyidx, "count": 1}

    def release(self, key):
        """Release a key"""
        _key, keysym = self.key_to_keysym(key)
        if _key is not None:
            self._update_modifiers(_key, False)

        if kmp.get(key) is not None:
            vk = kmp.get(key)
            if isinstance(vk, int):
                _send_vk(int(vk), True)
            else:
                # unicode or string, keyup using unicode
                if isinstance(vk, str) and len(vk) == 1:
                    _send_unicode(vk, True)
                else:
                    try:
                        _send_vk(int(vk), True)
                    except Exception:
                        _send_unicode(str(vk), True)
        elif keysym in self.event_mapping:
            keycode = self.event_mapping[keysym]["keycode"]
            # Distinguish unicode from VK. We used raw form of keycode when recording
            if isinstance(keycode, int) and keycode <= 0xFF:
                _send_vk(int(keycode), True)
            else:
                # unicode
                try:
                    _send_unicode(chr(keycode), True)
                except Exception:
                    # Try releasing as VK
                    try:
                        _send_vk(int(keycode), True)
                    except Exception:
                        pass

        self.sync()
        # Clear event record
        if keysym in self.event_mapping:
            self.event_mapping[keysym]["count"] -= 1
            if self.event_mapping[keysym]["count"] == 0:
                del self.event_mapping[keysym]

    def _shift_statue(self, modifiers):
        """Keep interface. Return key mask. Windows does not use this value, but keeps compatibility."""
        mask = 0
        # Check using Key.* members
        try:
            if Key.alt in modifiers:
                mask |= VK_MENU
            if Key.alt_gr in modifiers:
                mask |= VK_RMENU
            if Key.ctrl in modifiers:
                mask |= VK_CONTROL
            if Key.shift in modifiers:
                mask |= VK_SHIFT
        except Exception:
            pass
        return mask

    def reset_keyboard(self):
        """Reset keyboard, release all keys"""
        # Iterate event_mapping and release all pressed keys
        for keysym, data in list(self.event_mapping.items()):
            keycode, keyidx, count = data["keycode"], data["keyidx"], data["count"]
            if count > 0:
                for _ in range(count):
                    if isinstance(keycode, int) and keycode <= 0xFF:
                        _send_vk(int(keycode), True)
                    else:
                        try:
                            _send_unicode(chr(keycode), True)
                        except Exception:
                            try:
                                _send_vk(int(keycode), True)
                            except Exception:
                                pass
                data['count'] = 0
        self.event_mapping = {}

    def _send_event(self, event, keycode, keyidx=0):
        """Compatible with original interface, but calls SendInput directly in Windows"""
        # event parameter is not used in Windows implementation, keep signature
        # keycode: VK or unicode ordinal
        if isinstance(keycode, int) and keycode <= 0xFF:
            # key down
            _send_vk(int(keycode), False) if event in (self.press_event, self.ctrl_press, 'keydown') else _send_vk(int(keycode), True)
        else:
            # unicode
            try:
                ch = chr(keycode) if isinstance(keycode, int) else str(keycode)
                _send_unicode(ch[0], False) if event in (self.press_event, self.ctrl_press, 'keydown') else _send_unicode(ch[0], True)
            except Exception:
                pass

    @property
    @contextlib.contextmanager
    def _modifiers(self):
        # Convert active modifiers in NORMAL_MODIFIERS to VK list
        vals = set()
        for mod in self.modifiers:
            v = NORMAL_MODIFIERS.get(mod, None)
            if v is not None:
                vals.add(v)
        yield vals

    def get_all_mapping(self):
        """No equivalent keyboard mapping under Windows. Return empty list for compatibility."""
        return []

    def get_void_keycode(self):
        """Windows does not support dynamic registration of keyboard mapping. Raise exception or return a default value."""
        # Simply return 0xFF as placeholder
        return 0xFF, 0

    def _update_register_mapping(self, keysym, keycode, keyidx):
        """Modify registered keyboard mapping table (logical record only)"""
        _temp = None
        for _keysym, data in list(self.register_mapping.items()):
            if data["keycode"] == keycode and data["keyidx"] == keyidx:
                if keysym == _keysym:
                    _temp = _keysym
                    break
        if _temp:
            del self.register_mapping[_temp]
        self.register_mapping[keysym] = {"keycode": keycode, "keyidx": keyidx}

    def _register(self, keysym, keycode, keyidx):
        """Windows does not need to register key values at the system level. Just record locally and return."""
        self._update_register_mapping(keysym, keycode, keyidx)
        return keycode, keyidx

    def get_keycode(self, keysym, register=False):
        """Symbol code keysym to key code keycode. Windows returns keysym directly (if it is VK or unicode), otherwise tries to read from register_mapping."""
        # If keysym is already int and exists in register_mapping, return
        try:
            if isinstance(keysym, int):
                # Prefer returning registered info
                if keysym in self.register_mapping:
                    entry = self.register_mapping[keysym]
                    return entry['keycode'], entry['keyidx']
                # Treat keysym directly as keycode
                return keysym, 0
        except Exception:
            pass

        # Search register_mapping
        if keysym in self.register_mapping:
            return self.register_mapping[keysym]['keycode'], self.register_mapping[keysym]['keyidx']

        if register:
            kc, ki = self._register(keysym, *self.get_void_keycode())
            return kc, ki
        return None, None

    @staticmethod
    def char_to_keysym(char):
        """
        Text code corresponding to text
        Windows implementation returns unicode ordinal for sending with KEYEVENTF_UNICODE.
        """
        return ord(char)

    def clear_keycode(self, keycode):
        pass

    def clear_mapping(self):
        pass

    def pro_raise(self, ex):
        self.close()
        raise ex

    def close(self):
        try:
            self.reset_keyboard()
        except Exception:
            pass
        self.closed = True

    def sync(self):
        pass
