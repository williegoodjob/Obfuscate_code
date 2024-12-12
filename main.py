"""
Copyright (c) 2024 豆伯

This software is licensed under the MIT License. See LICENSE for details.
"""
from CodeObfuscator import CodeObfuscator
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path

class ObfuscatorGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Python 程式碼混淆器")
        self.window.geometry("600x300")
        
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
        length_scale = ttk.Scale(length_frame, from_=8, to=128, 
                               variable=self.length, orient="horizontal")
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