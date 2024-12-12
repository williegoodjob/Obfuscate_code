"""
Copyright (c) 2024 豆伯

This software is licensed under the MIT License. See LICENSE for details.
"""
from CodeObfuscator import CodeObfuscator
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from faker import Faker

class ObfuscatorGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Python 程式碼混淆器")
        self.window.geometry("600x500")  # 調整視窗高度
        
        # Faker 語言選擇區域
        faker_frame = ttk.LabelFrame(self.window, text="Faker 語言設定", padding=10)
        faker_frame.pack(fill="x", padx=10, pady=5)
        
        self.faker_langs = {
            "不使用Faker": None,
            "繁體中文": "zh_TW",
            "簡體中文": "zh_CN",
            "英文": "en_US",
            "日文": "ja_JP",
            "韓文": "ko_KR"
        }
        
        self.faker_var = tk.StringVar(value="不使用Faker")
        faker_combo = ttk.Combobox(
            faker_frame, 
            textvariable=self.faker_var,
            values=list(self.faker_langs.keys()),
            state="readonly"
        )
        faker_combo.pack(fill="x")
        
        # 輸入檔案區域
        input_frame = ttk.LabelFrame(self.window, text="輸入檔案", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        self.input_path = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_path).pack(side="left", fill="x", expand=True)
        ttk.Button(input_frame, text="選擇檔案", command=self.select_input).pack(side="right")
        
        # 輸出檔案區域
        output_frame = ttk.LabelFrame(self.window, text="輸出檔案", padding=10)
        output_frame.pack(fill="x", padx=10, pady=5)
        
        self.output_path = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path).pack(side="left", fill="x", expand=True)
        ttk.Button(output_frame, text="選擇檔案", command=self.select_output).pack(side="right")
        
        # Length 設定區域
        length_frame = ttk.LabelFrame(self.window, text="混淆長度設定", padding=10)
        length_frame.pack(fill="x", padx=10, pady=5)
        
        self.length = tk.IntVar(value=64)
        length_scale = tk.Scale(
            length_frame, from_=1,
            to=1024,
            variable=self.length,
            orient="horizontal",
            resolution = 1
        )
        length_scale.pack(fill="x")
        
        length_label = ttk.Label(length_frame, textvariable=self.length)
        length_label.pack()
        
        # 執行按鈕
        ttk.Button(self.window, text="執行混淆", command=self.run_obfuscation).pack(pady=20)
        
        self.status_var = tk.StringVar()
        ttk.Label(self.window, textvariable=self.status_var).pack()
        
    def select_input(self):
        filename = filedialog.askopenfilename(
            title="選擇 Python 檔案",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            self.input_path.set(filename)
            if not self.output_path.get():
                # 自動設定預設輸出檔案名稱
                p = Path(filename)
                self.output_path.set(str(p.parent / f"obfuscated_{p.name}"))
    
    def select_output(self):
        filename = filedialog.asksaveasfilename(
            title="選擇輸出位置",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            defaultextension=".py"
        )
        if filename:
            self.output_path.set(filename)
    
    def run_obfuscation(self):
        input_file = self.input_path.get()
        output_file = self.output_path.get()
        
        if not input_file or not output_file:
            self.status_var.set("錯誤：請選擇輸入和輸出檔案")
            return
            
        try:
            # 根據選擇的語言設定 Faker
            faker_lang = self.faker_langs[self.faker_var.get()]
            if faker_lang:
                fake = Faker(faker_lang)
                name_generator = lambda: fake.name().replace(' ', '_')
                ob = CodeObfuscator(
                    name_generator=name_generator,
                    length=self.length.get()
                )
            else:
                ob = CodeObfuscator(length=self.length.get())
                
            ob.obfuscate(input_file, output_file)
            self.status_var.set("混淆完成！")
        except Exception as e:
            self.status_var.set(f"錯誤：{str(e)}")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ObfuscatorGUI()
    app.run()
