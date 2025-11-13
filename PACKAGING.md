# PyInstaller 打包說明

本文件說明如何將 `crypto_price_tool.py` 打包為可執行檔，讓客戶無需安裝 Python 即可使用。

## 前置準備

### 1. 確認 Python 環境

```bash
python3 --version  # 確認 Python 版本（建議 3.8+）
```

### 2. 安裝 PyInstaller

```bash
pip3 install pyinstaller
```

或使用 requirements.txt：

```bash
pip3 install -r requirements.txt
```

## 打包方式

### 方式一：基本打包（單一執行檔）

最簡單的方式，產生單一執行檔：

```bash
pyinstaller --onefile crypto_price_tool.py
```

打包完成後，執行檔位於：
- **macOS/Linux**: `dist/crypto_price_tool`
- **Windows**: `dist\crypto_price_tool.exe`

### 方式二：進階打包（自訂選項）

#### macOS/Linux

```bash
pyinstaller --onefile \
  --name crypto_price_tool \
  --clean \
  crypto_price_tool.py
```

#### Windows

```bash
pyinstaller --onefile ^
  --name crypto_price_tool ^
  --clean ^
  crypto_price_tool.py
```

### 參數說明

- `--onefile`: 打包為單一執行檔
- `--name`: 指定輸出檔案名稱
- `--clean`: 清理暫存檔案
- `--console`: 顯示終端機視窗（預設，適合本工具）
- `--noconsole`: 隱藏終端機視窗（GUI 程式用）

## 打包後的檔案結構

```
python_for_crypto/
├── dist/
│   └── crypto_price_tool          # 可執行檔（macOS/Linux）
│   └── crypto_price_tool.exe      # 可執行檔（Windows）
├── build/                         # 暫存目錄（可刪除）
├── crypto_price_tool.spec         # PyInstaller 設定檔
└── crypto_price_tool.py           # 原始碼
```

## 測試可執行檔

### macOS/Linux

```bash
# 1. 賦予執行權限
chmod +x dist/crypto_price_tool

# 2. 測試執行
./dist/crypto_price_tool bitcoin \
  --from 2025-11-10 \
  --to 2025-11-12 \
  --api-key "你的API金鑰"

# 3. 測試 help
./dist/crypto_price_tool --help
```

### Windows

```cmd
# 測試執行
dist\crypto_price_tool.exe bitcoin ^
  --from 2025-11-10 ^
  --to 2025-11-12 ^
  --api-key "你的API金鑰"

# 測試 help
dist\crypto_price_tool.exe --help
```

## 交付給客戶

### 1. 準備交付檔案

建立交付資料夾並複製必要檔案：

#### macOS/Linux

```bash
# 建立交付目錄
mkdir crypto_price_tool_release

# 複製執行檔
cp dist/crypto_price_tool crypto_price_tool_release/

# 複製 README
cp README.md crypto_price_tool_release/

# 建立使用範例腳本（選用）
cat > crypto_price_tool_release/example.sh << 'EOF'
#!/bin/bash
# 使用範例

# 替換成你的 API key
API_KEY="你的API金鑰"

# 查詢 Bitcoin 最近一週
./crypto_price_tool bitcoin \
  --from 2025-11-05 \
  --to 2025-11-12 \
  --api-key "$API_KEY"
EOF

chmod +x crypto_price_tool_release/example.sh

# 打包
zip -r crypto_price_tool_macos.zip crypto_price_tool_release/
```

#### Windows

```cmd
# 建立交付目錄
mkdir crypto_price_tool_release

# 複製執行檔
copy dist\crypto_price_tool.exe crypto_price_tool_release\

# 複製 README
copy README.md crypto_price_tool_release\

# 建立使用範例腳本（選用）
echo @echo off > crypto_price_tool_release\example.bat
echo REM 替換成你的 API key >> crypto_price_tool_release\example.bat
echo set API_KEY=你的API金鑰 >> crypto_price_tool_release\example.bat
echo. >> crypto_price_tool_release\example.bat
echo REM 查詢 Bitcoin 最近一週 >> crypto_price_tool_release\example.bat
echo crypto_price_tool.exe bitcoin --from 2025-11-05 --to 2025-11-12 --api-key %%API_KEY%% >> crypto_price_tool_release\example.bat

# 打包（需要安裝 7-Zip 或其他壓縮工具）
# 7z a crypto_price_tool_windows.zip crypto_price_tool_release\
```

### 2. 交付清單

- `crypto_price_tool` 或 `crypto_price_tool.exe` - 可執行檔
- `README.md` - 使用說明
- `example.sh` 或 `example.bat` - 使用範例腳本（選用）

### 3. 客戶端使用說明

提供給客戶的簡易說明：

```
# 虛擬幣價格查詢工具 - 快速開始

## macOS/Linux 使用者

1. 解壓縮檔案
2. 開啟終端機，切換到解壓縮目錄
3. 賦予執行權限：
   chmod +x crypto_price_tool
4. 執行查詢：
   ./crypto_price_tool bitcoin --from 2025-11-10 --to 2025-11-12 --api-key "你的API金鑰"

## Windows 使用者

1. 解壓縮檔案
2. 開啟命令提示字元 (cmd)，切換到解壓縮目錄
3. 執行查詢：
   crypto_price_tool.exe bitcoin --from 2025-11-10 --to 2025-11-12 --api-key "你的API金鑰"

詳細說明請參考 README.md
```

## 不同平台的打包

### 重要提醒

**PyInstaller 打包的執行檔只能在相同作業系統上執行：**
- 在 macOS 打包 → 只能在 macOS 執行
- 在 Windows 打包 → 只能在 Windows 執行
- 在 Linux 打包 → 只能在 Linux 執行

### 跨平台打包策略

如需提供多平台版本：

1. **方案一：在各平台分別打包**
   - 在 macOS 機器上打包 macOS 版本
   - 在 Windows 機器上打包 Windows 版本
   - 在 Linux 機器上打包 Linux 版本

2. **方案二：使用虛擬機或 CI/CD**
   - 使用 VirtualBox/VMware 建立不同系統的虛擬機
   - 或使用 GitHub Actions 等 CI/CD 服務自動化打包

3. **方案三：提供 Python 原始碼**
   - 對於技術用戶，提供原始碼和 requirements.txt
   - 讓用戶自行執行 Python 腳本

## 常見問題

### Q: 打包後的檔案很大（10-20 MB）？

A: 這是正常的。PyInstaller 會包含 Python 解譯器和所有相依套件。可以透過以下方式減小體積：

```bash
# 使用 UPX 壓縮（需先安裝 UPX）
pyinstaller --onefile --upx-dir=/path/to/upx crypto_price_tool.py
```

### Q: 防毒軟體誤報為病毒？

A: PyInstaller 打包的執行檔可能被誤報。解決方案：

1. **向防毒軟體供應商回報誤報**
2. **將執行檔加入白名單**
3. **使用程式碼簽章（Code Signing）**：
   - macOS: 申請 Apple Developer ID 並簽署
   - Windows: 購買程式碼簽章憑證

### Q: macOS 顯示「無法開啟，因為它來自未識別的開發者」？

A: 需要允許執行：

```bash
# 方法一：移除隔離屬性
xattr -d com.apple.quarantine dist/crypto_price_tool

# 方法二：在系統偏好設定中允許
# 系統偏好設定 > 安全性與隱私 > 一般 > 允許「crypto_price_tool」
```

或進行程式碼簽章：

```bash
# 需要 Apple Developer ID
codesign -s "Developer ID Application: Your Name" dist/crypto_price_tool
```

### Q: Windows SmartScreen 阻擋執行？

A: 使用者需要點擊「更多資訊」→「仍要執行」。

長期解決方案：購買程式碼簽章憑證並簽署執行檔。

### Q: 執行檔啟動很慢？

A: PyInstaller 的執行檔需要解壓縮暫存檔案，第一次執行會較慢（約 1-3 秒），之後會快很多。

### Q: 如何更新執行檔？

A: 修改原始碼後，重新執行打包指令即可：

```bash
pyinstaller --onefile --clean crypto_price_tool.py
```

`--clean` 參數會清理舊的暫存檔案。

## 進階：建立 .spec 檔案

如需更精細的控制，可以編輯 `.spec` 檔案：

```bash
# 1. 產生 spec 檔案
pyi-makespec --onefile crypto_price_tool.py

# 2. 編輯 crypto_price_tool.spec（根據需求調整）

# 3. 使用 spec 檔案打包
pyinstaller crypto_price_tool.spec
```

## 自動化打包腳本

建立 `build.sh`（macOS/Linux）或 `build.bat`（Windows）：

### build.sh

```bash
#!/bin/bash
set -e

echo "清理舊檔案..."
rm -rf build dist *.spec

echo "開始打包..."
pyinstaller --onefile --clean --name crypto_price_tool crypto_price_tool.py

echo "測試執行檔..."
./dist/crypto_price_tool --help

echo "打包完成！"
echo "執行檔位置: dist/crypto_price_tool"
```

### build.bat

```bat
@echo off
echo 清理舊檔案...
rmdir /s /q build dist 2>nul
del *.spec 2>nul

echo 開始打包...
pyinstaller --onefile --clean --name crypto_price_tool crypto_price_tool.py

echo 測試執行檔...
dist\crypto_price_tool.exe --help

echo 打包完成！
echo 執行檔位置: dist\crypto_price_tool.exe
pause
```

## 總結

1. **開發階段**：使用 Python 直接執行，方便除錯
2. **測試階段**：打包為執行檔，在乾淨環境測試
3. **交付階段**：提供執行檔 + README + 範例腳本

如有打包相關問題，請參考：
- PyInstaller 官方文件：https://pyinstaller.org/
- 常見問題：https://github.com/pyinstaller/pyinstaller/wiki
