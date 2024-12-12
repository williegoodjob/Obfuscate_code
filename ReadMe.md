# Python 代碼混淆工具

這是一個用於混淆 Python 程式碼的工具，可以將代碼中的函數名稱、類別名稱、參數等進行隨機替換，從而提高代碼的保密性與難以理解的程度。這個工具特別適合用於教育場合，或在您需要分享程式碼但又希望保護其邏輯時使用。

## 功能特色
- 隨機生成難以識別的函數、類別及參數名稱。
- 支援避免替換內建函數名稱與 Python 關鍵字。
- 兼容模組別名，確保不影響外部模組的正常調用。
- 使用 Python 標準庫 `ast` 進行代碼解析與操作，無需額外安裝依賴（除第三方模組外）。

## 安裝說明

### 環境需求
- Python 版本：3.9 或以上（如果是舊版本，需額外安裝 `astor` 模組）
- 第三方依賴庫：
  - `Faker`：用於生成隨機名稱。

### 安裝方式
請確保您已安裝必要的依賴庫，執行以下指令即可：
```bash
pip install faker
```

## 使用方法

### 基本指令
```bash
python main.py <輸入文件> [輸出文件]
```

### 參數說明
- `<輸入文件>`：需要進行混淆的 Python 源代碼文件。
- `[輸出文件]`（選填）：混淆後輸出的文件名稱。若未提供，將使用預設名稱 `default_output.py`。

### 範例
假設有一個文件 `example.py`，您可以執行以下指令來混淆代碼並輸出到 `obfuscated_example.py`：
```bash
python main.py example.py obfuscated_example.py
```

執行後，`obfuscated_example.py` 將包含已混淆的代碼。

## 程式邏輯說明
- **模組別名處理**：避免替換導入的模組別名（例如 `import os as system` 中的 `system` 不會被替換）。
- **函數與類別名稱替換**：隨機生成新名稱，確保與 Python 關鍵字或內建名稱不衝突。
- **參數名稱替換**：對函數參數進行混淆，並保證邏輯一致性。
- **屬性名稱保留**：屬性名稱（例如 `object.attribute`）不會被替換，以避免影響程式運行。

## 目錄結構
```plaintext
.
├── LICENSE           # 授權條款文件
├── main.py           # 主程式
└── README.md         # 使用說明文件
```

## 注意事項
1. 請務必在測試環境下確認混淆後的代碼是否能正確執行。
2. 混淆過程中，將會覆蓋輸出文件的內容，請自行備份重要代碼。

## 授權方式
本專案遵循 [MIT 授權條款](https://opensource.org/licenses/MIT)。歡迎自由使用、修改及分發。
