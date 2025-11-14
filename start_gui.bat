@echo off
chcp 65001 >nul
REM ===================================================================
REM 虛擬幣價格查詢工具 - GUI 版本一鍵啟動腳本 (Windows)
REM ===================================================================

echo.
echo ===================================================================
echo   虛擬幣價格查詢工具 GUI 版本
echo ===================================================================
echo.

REM 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 Python！
    echo.
    echo 請先安裝 Python 3.7 或以上版本
    echo 下載網址: https://www.python.org/downloads/
    echo.
    echo 安裝時請勾選 "Add Python to PATH"！
    echo.
    pause
    exit /b 1
)

echo [1/3] 檢查 Python 版本...
python --version
echo.

REM 檢查 pip 是否可用
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] pip 未安裝或無法使用！
    echo.
    echo 請重新安裝 Python 並確保勾選 "pip" 選項
    echo.
    pause
    exit /b 1
)

echo [2/3] 檢查並安裝依賴套件...
echo.

REM 檢查 customtkinter 是否已安裝
python -c "import customtkinter" >nul 2>&1
if errorlevel 1 (
    echo [安裝中] 正在安裝 customtkinter...
    python -m pip install customtkinter --quiet
    if errorlevel 1 (
        echo [錯誤] customtkinter 安裝失敗！
        pause
        exit /b 1
    )
    echo [完成] customtkinter 安裝成功
) else (
    echo [已安裝] customtkinter
)

REM 檢查 pillow 是否已安裝
python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo [安裝中] 正在安裝 pillow...
    python -m pip install pillow --quiet
    if errorlevel 1 (
        echo [錯誤] pillow 安裝失敗！
        pause
        exit /b 1
    )
    echo [完成] pillow 安裝成功
) else (
    echo [已安裝] pillow
)

REM 檢查 requests 是否已安裝
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo [安裝中] 正在安裝 requests...
    python -m pip install requests --quiet
    if errorlevel 1 (
        echo [錯誤] requests 安裝失敗！
        pause
        exit /b 1
    )
    echo [完成] requests 安裝成功
) else (
    echo [已安裝] requests
)

echo.
echo [3/3] 啟動 GUI...
echo.
echo ===================================================================
echo.

REM 啟動 GUI
python crypto_price_gui.py

REM 如果 GUI 異常退出，顯示錯誤訊息
if errorlevel 1 (
    echo.
    echo ===================================================================
    echo [錯誤] GUI 啟動失敗！
    echo ===================================================================
    echo.
    echo 可能原因：
    echo 1. crypto_price_gui.py 檔案不存在或損壞
    echo 2. src/ 目錄中的模組檔案缺失
    echo 3. Python 版本過舊（需要 3.7+）
    echo.
    echo 請檢查以下檔案是否存在：
    echo - crypto_price_gui.py
    echo - src/core.py
    echo - src/utils.py
    echo - src/__init__.py
    echo.
    pause
    exit /b 1
)

REM 正常結束
echo.
echo ===================================================================
echo GUI 已關閉
echo ===================================================================
echo.
