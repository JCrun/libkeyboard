# libkeyboard

Simulated keyboard input for desktop environments on Linux systems, supporting Xinchuang systems and Chinese input.

## Dependencies

- Python 3
- python-xlib (>=0.16)

## Usage

Copy the `libkeyboard` folder to the `site-packages` directory of your Python installation.

```python
from libkeyboard import keyboard_write, keyboard_group


keyboard_write("Test Content 123")       # Simulate typing

keyboard_group("ctrl", "a")              # ctrl+a

keyboard_group("ctrl", "shift", "a")     # ctrl+shift+a
```
