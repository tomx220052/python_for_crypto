#!/bin/bash
# ===================================================================
# 虛擬幣價格查詢工具 - GUI 版本一鍵啟動腳本 (macOS/Linux)
# ===================================================================

echo ""
echo "==================================================================="
echo "  虛擬幣價格查詢工具 GUI 版本"
echo "==================================================================="
echo ""

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    echo "[錯誤] 找不到 Python3！"
    echo ""
    echo "請先安裝 Python 3.7 或以上版本"
    echo ""
    echo "macOS: brew install python3"
    echo "Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "Fedora/RHEL: sudo dnf install python3 python3-pip"
    echo ""
    exit 1
fi

echo "[1/3] 檢查 Python 版本..."
python3 --version
echo ""

# 檢查 pip 是否可用
if ! python3 -m pip --version &> /dev/null; then
    echo "[錯誤] pip 未安裝或無法使用！"
    echo ""
    echo "macOS: python3 -m ensurepip --upgrade"
    echo "Linux: sudo apt-get install python3-pip"
    echo ""
    exit 1
fi

echo "[2/3] 檢查並安裝依賴套件..."
echo ""

# 檢查 customtkinter 是否已安裝
if ! python3 -c "import customtkinter" &> /dev/null; then
    echo "[安裝中] 正在安裝 customtkinter..."
    python3 -m pip install customtkinter --quiet --user
    if [ $? -ne 0 ]; then
        echo "[錯誤] customtkinter 安裝失敗！"
        exit 1
    fi
    echo "[完成] customtkinter 安裝成功"
else
    echo "[已安裝] customtkinter"
fi

# 檢查 pillow 是否已安裝
if ! python3 -c "import PIL" &> /dev/null; then
    echo "[安裝中] 正在安裝 pillow..."
    python3 -m pip install pillow --quiet --user
    if [ $? -ne 0 ]; then
        echo "[錯誤] pillow 安裝失敗！"
        exit 1
    fi
    echo "[完成] pillow 安裝成功"
else
    echo "[已安裝] pillow"
fi

# 檢查 requests 是否已安裝
if ! python3 -c "import requests" &> /dev/null; then
    echo "[安裝中] 正在安裝 requests..."
    python3 -m pip install requests --quiet --user
    if [ $? -ne 0 ]; then
        echo "[錯誤] requests 安裝失敗！"
        exit 1
    fi
    echo "[完成] requests 安裝成功"
else
    echo "[已安裝] requests"
fi

echo ""
echo "[3/3] 啟動 GUI..."
echo ""
echo "==================================================================="
echo ""

# 啟動 GUI
python3 crypto_price_gui.py

# 檢查退出狀態
if [ $? -ne 0 ]; then
    echo ""
    echo "==================================================================="
    echo "[錯誤] GUI 啟動失敗！"
    echo "==================================================================="
    echo ""
    echo "可能原因："
    echo "1. crypto_price_gui.py 檔案不存在或損壞"
    echo "2. src/ 目錄中的模組檔案缺失"
    echo "3. Python 版本過舊（需要 3.7+）"
    echo ""
    echo "請檢查以下檔案是否存在："
    echo "- crypto_price_gui.py"
    echo "- src/core.py"
    echo "- src/utils.py"
    echo "- src/__init__.py"
    echo ""
    exit 1
fi

# 正常結束
echo ""
echo "==================================================================="
echo "GUI 已關閉"
echo "==================================================================="
echo ""
