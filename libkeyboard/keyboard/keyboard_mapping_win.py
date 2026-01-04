# coding=utf8
"""
@Author: Jim
@Date: 2025/10/11
@Description: Windows keyboard mapping table, returns the virtual key code (VK code) for each key
"""

import ctypes

# WinAPI
user32 = ctypes.WinDLL('user32', use_last_error=True)

# Convert character to virtual key code
def _to_vk(char):
    vk = user32.VkKeyScanW(ord(char))
    return vk & 0xff if vk != -1 else None

keyboardMapping = {
    # Control keys
    'backspace': 0x08,
    'tab': 0x09,
    'enter': 0x0D,
    'return': 0x0D,
    'shift': 0x10,
    'ctrl': 0x11,
    'alt': 0x12,
    'pause': 0x13,
    'capslock': 0x14,
    'esc': 0x1B,
    'escape': 0x1B,
    'space': 0x20,
    'pgup': 0x21,
    'pageup': 0x21,
    'pgdn': 0x22,
    'pagedown': 0x22,
    'end': 0x23,
    'home': 0x24,
    'left': 0x25,
    'up': 0x26,
    'right': 0x27,
    'down': 0x28,
    'printscreen': 0x2C,
    'insert': 0x2D,
    'delete': 0x2E,
    'winleft': 0x5B,
    'winright': 0x5C,
    'apps': 0x5D,
    'numlock': 0x90,
    'scrolllock': 0x91,
    'shiftleft': 0xA0,
    'shiftright': 0xA1,
    'ctrlleft': 0xA2,
    'ctrlright': 0xA3,
    'altleft': 0xA4,
    'altright': 0xA5,
}

# Function keys F1–F24
for i in range(1, 25):
    keyboardMapping[f'f{i}'] = 0x6F + i

# Numeric keypad
for i in range(10):
    keyboardMapping[f'num{i}'] = 0x60 + i
keyboardMapping.update({
    'multiply': 0x6A,
    'add': 0x6B,
    'separator': 0x6C,
    'subtract': 0x6D,
    'decimal': 0x6E,
    'divide': 0x6F,
})

# Main keyboard alphanumeric
for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890':
    vk = _to_vk(c)
    if vk:
        keyboardMapping[c] = vk

# Common symbols
for sym in '`~!@#$%^&*()-_=+[{]}\\|;:\'",<.>/?':
    vk = _to_vk(sym)
    if vk:
        keyboardMapping[sym] = vk

# Space and newlines
keyboardMapping.update({
    ' ': 0x20,
    '\t': 0x09,
    '\r': 0x0D,
    '\n': 0x0D,
    '\b': 0x08,
})

if __name__ == '__main__':
    for k, v in list(keyboardMapping.items())[:30]:
        print(f'{k}: {v}')
