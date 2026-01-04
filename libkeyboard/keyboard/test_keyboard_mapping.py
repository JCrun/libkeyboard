# test_keyboard_mapping.py
# coding=utf8

"""
测试 keyboard_mapping.py 是否能正确返回虚拟键码
"""

import time
import ctypes
from keyboard_mapping_win import keyboardMapping

user32 = ctypes.WinDLL('user32', use_last_error=True)

# 模拟按键按下和释放
def press_key(vk_code):
    user32.keybd_event(vk_code, 0, 0, 0)          # 按下
    time.sleep(0.05)
    user32.keybd_event(vk_code, 0, 0x0002, 0)     # 松开

def test_key(name):
    vk = keyboardMapping.get(name)
    if vk is None:
        print(f"[!] Key not found: {name}")
        return
    print(f"[+] Testing {name} -> VK={hex(vk)}")
    press_key(vk)

if __name__ == "__main__":
    print("Start testing common keys...")
    for key in ["a", "A", "1", "enter", "space", "f5", "left", "right", "up", "down"]:
        test_key(key)
        time.sleep(0.3)
    print("Test completed.")
