# test_windows_keyboard_class.py
# coding=utf8
import types
import builtins
from windows import KeyBoard

# Capture simulated send calls
sent_events = []

def mock_send_vk(vk, is_keyup):
    sent_events.append(("vk", vk, is_keyup))

def mock_send_unicode(ch, is_keyup):
    sent_events.append(("uni", ch, is_keyup))


def test_KeyBoard_basic():
    kb = KeyBoard()

    # Inject mock functions
    kb._send_vk = types.MethodType(lambda self, vk, up: mock_send_vk(vk, up), kb)
    kb._send_unicode = types.MethodType(lambda self, ch, up: mock_send_unicode(ch, up), kb)
    globals()['_send_vk'] = mock_send_vk
    globals()['_send_unicode'] = mock_send_unicode

    # Test normal keys
    kb.press("a")
    kb.release("a")

    # Test uppercase and shift handling
    kb.press("A")
    kb.release("A")

    # Test special keys
    kb.press("enter")
    kb.release("enter")

    # Test reset
    kb.press("b")
    kb.reset_keyboard()

    # Verify call records
    print("[+] Simulated event records:")
    for ev in sent_events:
        print(ev)

    assert any(e[0] == "vk" for e in sent_events), "Virtual key event not called"
    assert any(e[0] == "uni" for e in sent_events), "Unicode event not called"
    assert any(e[2] for e in sent_events), "Release event not detected"
    print("[+] KeyBoard test passed.")

if __name__ == "__main__":
    test_KeyBoard_basic()
