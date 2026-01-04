# coding=utf8

"""
@Author: baicaimp3
@Date: 2024/11/08
Core methods for simulated keyboard under Linux
"""

import Xlib
import Xlib.X
import Xlib.ext
import Xlib.XK
import contextlib
from Xlib.display import Display
from Xlib.ext.xtest import fake_input
from ..keyboard import Key, NORMAL_MODIFIERS
from ..util.xorg import display_manager, alt_gr_mask, alt_mask
from .keyboard_mapping import keyboardMapping as kmp


class KeyBoard(Display):
    def __init__(self):
        super().__init__()
        self.min_keycode      = self.display.info.min_keycode               # Minimum key code
        self.max_keycode      = self.display.info.max_keycode               # Maximum key code
        self.count            = self.max_keycode - self.min_keycode + 1     # Number of keys that can be registered
        self.press_event      = Xlib.display.event.KeyPress                 # Event for pressing a key
        self.release_event    = Xlib.display.event.KeyRelease               # Event for releasing a key
        self.ctrl_press       = Xlib.X.KeyPress
        self.ctrl_release     = Xlib.X.KeyRelease
        self.register_mapping = {}      # {keysym: {keycode: 1, keyidx: 0}} Registered keyboard mapping table
        self.event_mapping    = {}      # {keysym: {keycode: 1, keyidx: 0, count: 1}} Number of times pressed
        self.modifiers        = set()
        self.closed           = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        try:
            if self.closed is False:
                self.close()
        except AttributeError:
            pass

    def key_to_keysym(self, key):
        """Convert to text code keysym"""
        _key = None
        keysym = None
        if key.lower() in ('ps', 'printscreen', 'print screen'):
            key = 'print_screen'
        if hasattr(Key, key.lower()):
            keysym = getattr(Key, key.lower()).value.vk
            _key = getattr(Key, key.lower()).value

        elif key in ("\n", "\r"):
            _key = Key.enter.value
            keysym = _key.vk

        elif key == "\t":
            _key = Key.Tab.value
            keysym = _key.vk

        elif key.lower() in {'win', 'cmd', 'winleft'}:
            keysym = Key.cmd.value.vk
            _key = Key.cmd.value

        elif key in kmp:
            keysym = kmp.get(key)
            _key = None

        elif len(key) != 1:
            self.pro_raise(Exception("Character length must be 1"))
        else:
            keysym = self.char_to_keysym(key)
        return _key, keysym

    def _update_modifiers(self, key, is_press):
        """Record when key is ctrl, shift, alt"""
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
        :param register: Whether to register the key when it does not exist. For security reasons, true only when writing()
        """
        _key, keysym = self.key_to_keysym(key)      # Get corresponding text code
        if _key is not None:
            self._update_modifiers(_key, True)

        if kmp.get(key) is not None:
            keycode, keyidx = kmp.get(key), 0
            needshift = True if key.isupper() or key in '~!@#$%^&*()_+{}|:"<>?' else False
            if needshift:
                self._send_event(self.ctrl_press, kmp['shift'])     # Press shift

            self._send_event(self.ctrl_press, kmp.get(key))

            if needshift:
                self._send_event(self.ctrl_release, kmp['shift'])   # Release shift

        else:
            keycode, keyidx = self.get_keycode(keysym, register)        # Get key code
            if keycode is None:
                self.pro_raise(KeyError(f"No such key '{key}'"))
            event = self.press_event if not _key else self.ctrl_press
            self._send_event(event, keycode, keyidx)        # Send keyboard event

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

        if kmp.get(key) is not None:        # Hot key
            keycode = kmp.get(key)
            self._send_event(self.ctrl_release, keycode)

        elif keysym in self.event_mapping:
            keycode, keyidx = self.event_mapping[keysym]["keycode"], self.event_mapping[keysym]['keyidx']
            event = self.release_event if not _key else self.ctrl_release
            self._send_event(event, keycode, keyidx)

        self.sync()
        # Clear event record
        if keysym in self.event_mapping:
            self.event_mapping[keysym]["count"] -= 1
            if self.event_mapping[keysym]["count"] == 0:
                del self.event_mapping[keysym]

    def _shift_statue(self, modifiers):
        return 0 | (alt_mask(self) if Key.alt in modifiers else 0) | (
            alt_gr_mask if Key.alt_gr in modifiers else 0) | (
            Xlib.X.ControlMask if Key.ctrl in modifiers else 0) | (
            Xlib.X.ShiftMask if Key.shift in modifiers else 0)

    def reset_keyboard(self):
        """Reset keyboard, release all keys"""
        for keysym, data in self.event_mapping.items():
            keycode, keyidx, count = data["keycode"], data["keyidx"], data["count"]
            if count >= 0:
                for i in range(count):
                    self._send_event(self.release_event, keycode, keyidx)
                data['count'] = 0
        self.event_mapping = {}

    def _send_event(self, event, keycode, keyidx=0):
        """Send a keyboard event"""
        with display_manager(self) as dm, self._modifiers as modifiers:
            if isinstance(event, int):
                Xlib.ext.xtest.fake_input(dm, event, keycode)
            else:
                window = dm.get_input_focus().focus
                send_event = getattr(window, "send_event", lambda _event: dm.send_event(window, _event))
                send_event(event(
                    detail=keycode,
                    state=keyidx | self._shift_statue(modifiers),
                    time=0,
                    root=dm.screen().root,
                    window=window,
                    same_screen=0,
                    child=Xlib.X.NONE,
                    root_x=0, root_y=0, event_x=0, event_y=0
                ))

    @property
    @contextlib.contextmanager
    def _modifiers(self):
        yield set(NORMAL_MODIFIERS.get(modifier, None) for modifier in self.modifiers)

    def get_all_mapping(self):
        """Get all keyboard mappings"""
        return self.get_keyboard_mapping(self.min_keycode, self.count)

    def get_void_keycode(self):
        """Get an unregistered key value"""
        for _keycode, _keysym in enumerate(self.get_all_mapping()[128:]):
            if not any(_keysym):
                keyidx = 0
                return _keycode + self.min_keycode + 128, keyidx

        # No spare keys, take an unpressed key from the registered ones
        for keysym, data in self.register_mapping.items():
            if keysym not in self.event_mapping or self.event_mapping[keysym].get('count', 0) == 0:
                return data["keycode"], data["keyidx"]
        self.pro_raise("No spare keys")

    def _update_register_mapping(self, keysym, keycode, keyidx):
        """Modify registered keyboard mapping table"""
        _temp = None
        for _keysym, data in self.register_mapping.items():
            if data["keycode"] == keycode and data["keyidx"] == keyidx:
                if keysym == _keysym:
                    _temp = _keysym
                    break
        if _temp:
            del self.register_mapping[_temp]
        self.register_mapping[keysym] = {"keycode": keycode, "keyidx": keyidx}

    def _register(self, keysym, keycode, keyidx):
        """Register key. Usually called when content is Chinese"""
        mapping = self.get_all_mapping()
        mapping[keycode - self.min_keycode][0] = keysym
        with display_manager(self) as dm:
            mapping[keycode - self.min_keycode][keyidx] = keysym
            dm.change_keyboard_mapping(keycode, mapping[keycode - self.min_keycode: keycode - self.min_keycode + 1])
            self._update_register_mapping(keysym, keycode, keyidx)

        return keycode, keyidx

    def get_keycode(self, keysym, register=False):
        """Convert symbol code keysym to key code keycode"""
        keycode = self.keysym_to_keycode(keysym)
        if keycode:
            try:
                all_kb = self.get_all_mapping()
                keyidx = all_kb[keycode - self.min_keycode].index(keysym)
                return keycode, keyidx
            except ValueError:
                return keycode, 0

        if keysym in self.register_mapping:     # Find this key in registered ones
            return self.register_mapping[keysym]['keycode'], self.register_mapping[keysym]['keyidx']

        for keycode, mapping in enumerate(self.get_all_mapping()):      # Find this key in keyboard mapping
            if mapping[0] == keysym:
                return keycode + self.min_keycode, 0
            elif mapping[1] == keysym:
                return keycode + self.min_keycode, 1

        if register:        # Key not found, register it
            keycode, keyidx = self._register(keysym, *self.get_void_keycode())
            return keycode, keyidx
        return None, None

    @staticmethod
    def char_to_keysym(char):
        """
        Text code corresponding to text
        :param char: Character of length 1
        :return: text code keysym
        """
        ordinal = ord(char)
        if ordinal < 0x100:
            return ordinal
        else:
            return ordinal | 0x01000000

    def clear_keycode(self, keycode):
        """Clear a key"""
        mapping = self.get_all_mapping()
        max_num = len(mapping[keycode - self.min_keycode])
        with display_manager(self) as dm:
            mapping[keycode - self.min_keycode] = [0 for i in range(max_num)]
            dm.change_keyboard_mapping(keycode, mapping[keycode - self.min_keycode: keycode - self.min_keycode + 1])

    def clear_mapping(self):
        """
        Clear all registered keys
        """
        if self.register_mapping:
            mapping = self.get_all_mapping()
            del_list = []
            with display_manager(self) as dm:
                for keysym, data in self.register_mapping.items():
                    mapping[data['keycode'] - self.min_keycode] = [0 for i in range(7)]
                    dm.change_keyboard_mapping(data['keycode'], mapping[data['keycode'] - self.min_keycode: data['keycode'] - self.min_keycode + 1])
                    del_list.append(keysym)

            for k in del_list:
                del self.register_mapping[k]

    def pro_raise(self, ex):
        """Raise exception"""
        self.close()
        raise ex

    def close(self):
        try:
            self.reset_keyboard()       # Release all keys
        except Exception as e:
            pass

        try:
            self.clear_mapping()        # Clear all registered keys
        except Exception as e:
            pass

        try:
            self.display.close()
            self.closed = True
        except Xlib.error.ConnectionClosedError:
            pass
