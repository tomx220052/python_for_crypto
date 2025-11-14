# 安裝指南

本文檔說明如何在不同作業系統上安裝和使用虛擬幣價格查詢工具。

---

## 🎯 推薦方式：一鍵啟動腳本

### Windows 用戶

1. **確保已安裝 Python 3.7+**
   - 下載：https://www.python.org/downloads/
   - ⚠️ **重要**：安裝時請勾選 "Add Python to PATH"

2. **雙擊執行 `start_gui.bat`**
   - 腳本會自動檢查並安裝所有依賴
   - 自動啟動 GUI

### macOS/Linux 用戶

1. **確保已安裝 Python 3.7+**
   ```bash
   # macOS
   brew install python3

   # Ubuntu/Debian
   sudo apt-get install python3 python3-pip

   # Fedora/RHEL
   sudo dnf install python3 python3-pip
   ```

2. **雙擊執行 `start_gui.sh` 或在終端機執行**
   ```bash
   ./start_gui.sh
   ```
   - 腳本會自動檢查並安裝所有依賴
   - 自動啟動 GUI

---

## 📦 手動安裝方式

如果一鍵腳本無法使用，可以手動安裝：

### 步驟 1：安裝 Python

#### Windows
1. 下載 Python：https://www.python.org/downloads/
2. 執行安裝程式
3. ⚠️ **勾選 "Add Python to PATH"**
4. 點擊 "Install Now"

#### macOS
```bash
# 使用 Homebrew（推薦）
brew install python3

# 或下載官方安裝包
# https://www.python.org/downloads/macos/
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-tk
```

#### Linux (Fedora/RHEL)
```bash
sudo dnf install python3 python3-pip python3-tkinter
```

### 步驟 2：驗證 Python 安裝

```bash
# Windows
python --version
python -m pip --version

# macOS/Linux
python3 --version
python3 -m pip --version
```

應該顯示 Python 3.7 或以上版本。

### 步驟 3：安裝依賴套件

#### Windows
```cmd
cd C:\path\to\python_for_crypto2
python -m pip install -r requirements.txt
```

#### macOS/Linux
```bash
cd /path/to/python_for_crypto2
python3 -m pip install -r requirements.txt
```

### 步驟 4：啟動 GUI

#### Windows
```cmd
python crypto_price_gui.py
```

#### macOS/Linux
```bash
python3 crypto_price_gui.py
```

---

## 🐛 常見問題排除

### Q1: 執行 `start_gui.bat` 時顯示「找不到 Python」

**解決方法：**
1. 重新安裝 Python，確保勾選 "Add Python to PATH"
2. 或手動將 Python 加入 PATH：
   - 右鍵「我的電腦」→「內容」→「進階系統設定」
   - 點擊「環境變數」
   - 在「系統變數」中找到 `Path`，點擊「編輯」
   - 新增 Python 安裝路徑（例如：`C:\Python311\` 和 `C:\Python311\Scripts\`）

### Q2: pip 安裝套件失敗

**解決方法：**

#### Windows
```cmd
# 升級 pip
python -m pip install --upgrade pip

# 使用國內鏡像源（中國用戶）
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### macOS/Linux
```bash
# 升級 pip
python3 -m pip install --upgrade pip

# 如果權限不足，使用 --user
python3 -m pip install -r requirements.txt --user

# 或使用 sudo（不推薦）
sudo python3 -m pip install -r requirements.txt
```

### Q3: macOS 上執行 `start_gui.sh` 顯示「權限不足」

**解決方法：**
```bash
chmod +x start_gui.sh
./start_gui.sh
```

### Q4: Linux 上 GUI 無法啟動，顯示 tkinter 錯誤

**解決方法：**
安裝 tkinter 套件：

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

### Q5: Windows Defender 或防毒軟體阻擋執行

**解決方法：**
1. 將專案資料夾加入防毒軟體的白名單
2. 或暫時停用防毒軟體的即時掃描功能

### Q6: 安裝 customtkinter 失敗

**解決方法：**

#### 方法 1：單獨安裝
```bash
# Windows
python -m pip install customtkinter pillow

# macOS/Linux
python3 -m pip install customtkinter pillow
```

#### 方法 2：指定版本
```bash
# Windows
python -m pip install customtkinter==5.2.0 pillow==10.1.0

# macOS/Linux
python3 -m pip install customtkinter==5.2.0 pillow==10.1.0
```

#### 方法 3：使用國內鏡像（中國用戶）
```bash
python -m pip install customtkinter -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q7: 執行時出現 ModuleNotFoundError

**可能缺少的模組：**
- `requests` → `pip install requests`
- `customtkinter` → `pip install customtkinter`
- `PIL` (Pillow) → `pip install pillow`

**一次安裝所有：**
```bash
# Windows
python -m pip install requests customtkinter pillow

# macOS/Linux
python3 -m pip install requests customtkinter pillow
```

---

## 📋 必要依賴清單

| 套件名稱 | 版本 | 用途 |
|---------|------|------|
| requests | 2.31.0 | HTTP 請求（API 調用）|
| customtkinter | 5.2.0 | 現代化 GUI 介面 |
| pillow | 10.1.0 | 圖片處理（GUI 依賴）|
| pyinstaller | 6.3.0 | 打包成執行檔（選用）|

**自動安裝的隱藏依賴：**
- `darkdetect` - customtkinter 的依賴，自動安裝
- `packaging` - customtkinter 的依賴，自動安裝

---

## 🚀 驗證安裝

執行以下命令確認所有套件已正確安裝：

### Windows
```cmd
python -c "import requests; import customtkinter; import PIL; print('✓ 所有依賴已安裝')"
```

### macOS/Linux
```bash
python3 -c "import requests; import customtkinter; import PIL; print('✓ 所有依賴已安裝')"
```

如果沒有錯誤訊息並顯示 "✓ 所有依賴已安裝"，表示安裝成功！

---

## 📞 技術支援

如果仍然遇到問題，請提供以下資訊：

1. **作業系統版本**
   - Windows: `winver` 命令查看
   - macOS: `sw_vers`
   - Linux: `cat /etc/os-release`

2. **Python 版本**
   ```bash
   python --version  # Windows
   python3 --version # macOS/Linux
   ```

3. **錯誤訊息截圖或完整錯誤訊息**

4. **嘗試過的解決方法**

---

**最後更新：** 2025-11-14
**版本：** v2.0.0 MVP
