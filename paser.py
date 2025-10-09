import time
import Xlib
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode

from libkeyboard import keyboard_write

class KeyboardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LibKeyboard 输入助手")
        self.root.geometry("600x1200")
        self.root.attributes('-topmost', False)

        # 多行文本框
        self.textbox = scrolledtext.ScrolledText(root, height=8, width=70)
        self.textbox.pack(pady=10)

        # 延迟滑块
        tk.Label(root, text="输入延迟 (秒):").pack()
        # 初始值设为1秒
        self.delay_scale = tk.Scale(root, from_=0, to=5, orient=tk.HORIZONTAL, resolution=0.1)
        self.delay_scale.set(2.0)
        self.delay_scale.pack()

        # 间隔滑块
        tk.Label(root, text="字符间隔 (秒):").pack()
        self.interval_scale = tk.Scale(root, from_=0, to=1, orient=tk.HORIZONTAL, resolution=0.01)
        self.interval_scale.set(0.2)
        self.interval_scale.pack()

        # 置顶按钮
        self.top_btn = tk.Button(root, text="窗口置顶", command=self.toggle_topmost)
        self.top_btn.pack(pady=5)

        # 日志文本框（只读）
        tk.Label(root, text="日志:").pack()
        self.logbox = scrolledtext.ScrolledText(root, height=6, width=70, state='disabled')
        self.logbox.pack(pady=5)

        # 开始输入按钮
        self.start_btn = tk.Button(root, text="开始输入", command=self.start_typing)
        self.start_btn.pack(pady=10)

        # 图片上传按钮
        self.upload_btn = tk.Button(root, text="上传二维码图片", command=self.upload_image)
        self.upload_btn.pack(pady=5)

        # 图片预览
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
        self.top_btn.config(text="取消置顶" if top else "窗口置顶")

    def start_typing(self):
        text = self.textbox.get("1.0", tk.END).strip()
        delay = self.delay_scale.get()
        interval = self.interval_scale.get()
        if not text:
            self.log("文本框为空！")
            return
        self.log(f"延迟 {delay}s 后开始输入...")
        threading.Thread(target=self.type_text, args=(text, delay, interval), daemon=True).start()

    def type_text(self, text, delay, interval):
        time.sleep(delay)
        for char in text:
            if ord(char) < 128:  # 只支持英文字符
                keyboard_write(char)
                self.log(f"输入: {char}")
                time.sleep(interval)
            else:
                self.log(f"跳过非英文字符: {char}")

    def upload_image(self):
        # file type
        filetypes = (
            ('图片文件',  '.png .jpg .jpeg .bmp .gif'),
            ('所有文件', '*.*')
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
                self.log(f"二维码识别成功: {qr_data}")
            else:
                self.log("未识别到二维码内容")
        except Exception as e:
            self.log(f"图片处理失败: {e}")

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
