# libkeyboard

A cross-platform Python library for simulated keyboard input, supporting both Linux (X11) and Windows. It handles complex key combinations and Unicode text input seamlessly.

## Features

- **Cross-Platform**: Works on Linux (via Xlib) and Windows (via Win32 API).
- **Simple API**: Easy-to-use functions for typing text and key combinations.
- **Unicode Support**: Supports input of Chinese and other non-ASCII characters.
- **Context Manager**: Safe resource management using `with KeyBoard() as kb:` syntax.

## Dependencies

- Python 3.6+
- **Linux**: `python-xlib>=0.16`
- **Windows**: Built-in `ctypes` (no external dependencies)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/libkeyboard.git
   cd libkeyboard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### High-level API

The easiest way to use `libkeyboard` is through its high-level functions:

```python
from libkeyboard import keyboard_write, keyboard_group

# Type a string
keyboard_write("Hello World!")

# Type with delay between keystrokes (useful for some applications)
keyboard_write("Slow typing...", delay=0.1)

# Perform key combinations
keyboard_group("ctrl", "c")              # Copy
keyboard_group("ctrl", "shift", "esc")   # Open Task Manager
keyboard_group("win", "r")               # Open Run dialog
```

### Low-level API (KeyBoard Class)

For more control, you can use the `KeyBoard` class directly:

```python
from libkeyboard import KeyBoard

with KeyBoard() as kb:
    kb.press("shift")
    kb.press("a")
    kb.release("a")
    kb.release("shift")
```

## Examples

Check the [examples/](examples/) directory for more usage scripts:
- `examples/gui_assistant.py`: A Tkinter-based GUI tool for testing keyboard input and QR code scanning.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
