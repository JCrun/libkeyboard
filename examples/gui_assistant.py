import time
import ctypes
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
import sys
import os

# Add parent directory to path to import libkeyboard
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from libkeyboard.keyboard.keyboard_mapping_win import keyboardMapping
except ImportError:
    # Fallback if running from root or installed
    try:
        from libkeyboard.keyboard.keyboard_mapping_win import keyboardMapping
    except ImportError:
        print("Error: Could not import libkeyboard. Make sure you are running from the examples directory or have the package installed.")
        sys.exit(1)

user32 = ctypes.WinDLL('user32', use_last_error=True)


class KeyboardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LibKeyboard Input Assistant")
        self.root.geometry("300x700")
        self.root.attributes('-topmost', False)

        # Multi-line text box
        self.textbox = scrolledtext.ScrolledText(root, height=8, width=70)
        self.textbox.pack(pady=10)

        # Delay slider
        tk.Label(root, text="Input delay (s):").pack()
        self.delay_scale = tk.Scale(root, from_=0, to=5, orient=tk.HORIZONTAL, resolution=0.1)
        self.delay_scale.set(2.0)
        self.delay_scale.pack()

        # Interval slider
        tk.Label(root, text="Char interval (s):").pack()
        self.interval_scale = tk.Scale(root, from_=0, to=1, orient=tk.HORIZONTAL, resolution=0.01)
        self.interval_scale.set(0.05)
        self.interval_scale.pack()

        # Topmost button
        self.top_btn = tk.Button(root, text="Window topmost", command=self.toggle_topmost)
        self.top_btn.pack(pady=5)

        # Log text box
        tk.Label(root, text="Log:").pack()
        self.logbox = scrolledtext.ScrolledText(root, height=6, width=70, state='disabled')
        self.logbox.pack(pady=5)

        # Start typing button
        self.start_btn = tk.Button(root, text="Start typing", command=self.start_typing)
        self.start_btn.pack(pady=10)

        # ====== Todo completion: Default append enter function ======
        self.add_enter_var = tk.BooleanVar(value=True)
        self.add_enter_check = tk.Checkbutton(
            root,
            text="Auto enter after typing",
            variable=self.add_enter_var,
            onvalue=True,
            offvalue=False
        )
        self.add_enter_check.pack(pady=5)
        # =====================================

        # Image upload button
        self.upload_btn = tk.Button(root, text="Upload QR Code Image", command=self.upload_image)
        self.upload_btn.pack(pady=5)

        # Image preview
        self.img_label = tk.Label(root)
        self.img_label.pack()

    def log(self, msg):
        self.logbox.config(state='normal')
        self.logbox.insert(tk.END, msg + "\n")
        self.logbox.see(tk.END)
        self.logbox.config(state='disabled')

    def toggle_topmost(self):
        top = not self.root.attributes('-topmost')
        self.root.attributes('-topmost', top)
        self.top_btn.config(text="Cancel topmost" if top else "Window topmost")

    def start_typing(self):
        text = self.textbox.get("1.0", tk.END).strip()
        delay = self.delay_scale.get()
        interval = self.interval_scale.get()
        if not text:
            self.log("Text box is empty!")
            return
        self.log(f"Start typing after {delay}s...")
        threading.Thread(target=self.type_text, args=(text, delay, interval), daemon=True).start()

    def press_key(self, vk_code):
        user32.keybd_event(vk_code, 0, 0, 0)
        user32.keybd_event(vk_code, 0, 0x0002, 0)

    def type_text(self, text, delay, interval):
        time.sleep(delay)
        for char in text:
            if ord(char) < 128:
                vk = keyboardMapping.get(char)
                if vk is not None:
                    self.press_key(vk)
                    self.log(f"Input: {char}")
                    time.sleep(interval)
                else:
                    self.log(f"Mapping not found: {char}")
            else:
                self.log(f"Skip non-English char: {char}")

        # ====== Append Enter if 'Auto Enter' is enabled ======
        if self.add_enter_var.get():
            vk_enter = keyboardMapping.get("enter") or 0x0D  # Default VK_RETURN
            self.press_key(vk_enter)
            self.log("Typing finished, auto send Enter.")
        # ==========================================

    def upload_image(self):
        filetypes = (
            ('Image files',  '.png .jpg .jpeg .bmp .gif'),
            ('All files', '*.*')
        )
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if not file_path:
            return
        try:
            img = Image.open(file_path)
            img.thumbnail((150, 150))
            self.img_label.img = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.img_label.img)
            qr_data = self.decode_qr(file_path)
            if qr_data:
                self.textbox.delete("1.0", tk.END)
                self.textbox.insert(tk.END, qr_data)
                self.log(f"QR code recognized: {qr_data}")
            else:
                self.log("No QR code content recognized")
        except Exception as e:
            self.log(f"Image processing failed: {e}")

    def decode_qr(self, img_path):
        img = Image.open(img_path).convert('RGB')
        decoded = decode(img)
        if decoded:
            return decoded[0].data.decode('utf-8')
        return ""


def main():
    root = tk.Tk()
    app = KeyboardGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
